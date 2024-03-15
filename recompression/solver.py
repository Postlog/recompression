import time
from collections import Counter
from dataclasses import dataclass

from recompression.compress_pair import PairCompressor
from recompression.get_empty_substitutions import get_empty_options, get_full_empty_option
from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.get_options_for_pair import get_options_for_pair
from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, compression_node as cn, actions as ac, option as opt, \
    substitution as sb
from utils.time import timeit


@dataclass
class SolverStats:
    total_working_time: float = 0
    heuristics_timings: dict[str, list[float]] = None
    branches_dropped_by_heuristics: dict[str, int] = None

    def __post_init__(self):
        self.heuristics_timings = {}
        self.branches_dropped_by_heuristics = {}

    def add_heuristics_timing(self, name: str, value: float):
        if name not in self.heuristics_timings:
            self.heuristics_timings[name] = []

        self.heuristics_timings[name].append(value)

    def add_dropped_branches(self, name: str):
        if name not in self.branches_dropped_by_heuristics:
            self.branches_dropped_by_heuristics[name] = 0

        self.branches_dropped_by_heuristics[name] += 1


class Solver:
    def __init__(self, equation_heuristics: list[h.Heurisitcs]):
        self._heuristics = equation_heuristics
        self._pair_compressor = PairCompressor()
        self._node_id_counter = 1

    def _next_node_id(self) -> int:
        self._node_id_counter += 1
        return self._node_id_counter

    def solve(self, equation: eq.Equation) -> tuple[cn.CompressionNode, SolverStats]:
        if len(equation.template.get_vars_set()) == 0:
            raise ValueError('Шаблон должен содержать как минимум 1 переменную')

        if len(equation.sample.elements) == 0:
            raise ValueError('Образец не может быть пустым')

        if equation.is_solved:
            return cn.CompressionNode.empty(equation), SolverStats()

        self._pair_compressor.reset()
        self._node_id_counter = 1

        root = cn.CompressionNode.empty(equation)
        stats = SolverStats()
        start = time.perf_counter()
        self._solve(root, stats)

        stats.total_working_time = time.perf_counter() - start

        return root, stats

    def _solve(self, node: cn.CompressionNode, stats: SolverStats):
        node_eq = node.equation
        actions = get_most_profit_actions(node_eq.sample)

        for action in actions:
            if isinstance(action, ac.CompressPairAction):
                self._do_pair_compression(node, action, stats)
            else:
                print(f'ERROR: unknown action {action}')
                continue

    def _do_pair_compression(
            self,
            parent_node: cn.CompressionNode,
            action: ac.CompressPairAction,
            stats: SolverStats,
    ):
        parent_option = parent_node.option
        if parent_option is not None:
            parent_option = parent_option.optimize(parent_node.equation)

        for empty_opt in get_empty_options(action.pair, parent_node.equation.template, parent_option):
            emptied_eq = empty_opt.apply_to(parent_node.equation)
            for option in get_options_for_pair(
                    emptied_eq,
                    action.pair,
                    empty_opt,
            ):
                new_const, new_eq = self._pair_compressor.compress_pair(
                    action.pair,
                    option.apply_to(emptied_eq)
                )

                if new_eq.is_solved:
                    parent_node.children.append(
                        cn.CompressionNode(self._next_node_id(), new_eq, option, (action, new_const), []),
                    )
                    continue

                is_dropped = False
                for heuristic in self._heuristics:
                    start = time.perf_counter()
                    is_satisfable = heuristic.is_satisfable(new_eq, option)
                    stats.add_heuristics_timing(heuristic.get_name(), time.perf_counter() - start)

                    if not is_satisfable:
                        stats.add_dropped_branches(heuristic.get_name())
                        is_dropped = True
                        break

                if is_dropped:
                    continue

                child_node = cn.CompressionNode(self._next_node_id(), new_eq, option, (action, new_const), [])
                parent_node.children.append(child_node)

                o = get_full_empty_option(new_eq.template, option)
                if o is not None:
                    trivial_eq = o.apply_to(new_eq)
                    if trivial_eq.is_solved:
                        child_node.children.append(cn.CompressionNode(self._next_node_id(), trivial_eq, o, None, []))
                        continue

                if len(new_eq.sample.elements) == 1:
                    for var, count in Counter(new_eq.template.elements).items():
                        if count != 1:
                            continue

                        emptied_vars = new_eq.template.get_vars_set() - {var}

                        can = True
                        for vr in emptied_vars:
                            subst = sb.EmptySubstitution(vr)
                            if option.restriction is not None and not option.restriction.is_substitution_satisfies(
                                    subst):
                                can = False

                        if not can:
                            continue

                        o = opt.Option(
                            [sb.EmptySubstitution(vr) for vr in new_eq.template.get_vars_set() if vr != var],
                            None
                        )

                        trivial_eq = o.apply_to(new_eq)
                        if trivial_eq.is_solved:
                            child_node.children.append(cn.CompressionNode(self._next_node_id(), trivial_eq, o, None, []))

                    continue

                self._solve(child_node, stats)
