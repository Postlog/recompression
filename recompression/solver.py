from collections import Counter

from recompression.compress_pair import PairCompressor
from recompression.get_empty_substitutions import get_empty_options, get_full_empty_option
from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.get_options_for_pair import get_options_for_pair
from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, compression_node as cn, actions as ac, option as opt, substitution as sb
from utils.time import timeit


class Solver:
    def __init__(self, equation_heuristics: list[h.Heurisitcs]):
        self._heuristics = equation_heuristics
        self._pair_compressor = PairCompressor()

    @timeit("equation solving")
    def solve(self, equation: eq.Equation) -> cn.CompressionNode:
        if len(equation.template.get_vars_set()) == 0:
            raise ValueError('template must have at least 1 variable')

        if len(equation.sample.elements) == 0:
            raise ValueError('sample cannot be empty')

        if equation.is_solved:
            return cn.CompressionNode.empty(equation)

        self._pair_compressor.reset()

        root = cn.CompressionNode.empty(equation)
        self._solve(root)

        return root

    def _solve(self, node: cn.CompressionNode):
        node_eq = node.equation
        actions = get_most_profit_actions(node_eq.sample)

        for action in actions:
            if isinstance(action, ac.CompressPairAction):
                self._do_pair_compression(node, action)
            else:
                print(f'ERROR: unknown action {action}')
                continue

    def _do_pair_compression(
            self,
            parent_node: cn.CompressionNode,
            action: ac.CompressPairAction,
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
                        cn.CompressionNode(new_eq, option, (action, new_const), []),
                    )
                    continue

                is_dropped = False
                for heuristic in self._heuristics:
                    if not heuristic.is_satisfable(new_eq, option):
                        is_dropped = True
                        print(
                            f'WARN: equation {new_eq} dropped bacause of {heuristic.get_name()} heuristics, option {option}')
                        break

                if is_dropped:
                    continue

                child_node = cn.CompressionNode(new_eq, option, (action, new_const), [])
                parent_node.children.append(child_node)

                o = get_full_empty_option(new_eq.template, option)
                if o is not None:
                    trivial_eq = o.apply_to(new_eq)
                    if trivial_eq.is_solved:
                        child_node.children.append(cn.CompressionNode(trivial_eq, o, None, []))
                        continue

                if len(new_eq.sample.elements) == 1:
                    for var, count in Counter(new_eq.template.elements).items():
                        if count != 1:
                            continue

                        emptied_vars = new_eq.template.get_vars_set() - {var}

                        can = True
                        for vr in emptied_vars:
                            subst = sb.EmptySubstitution(vr)
                            if option.restriction is not None and not option.restriction.is_substitution_satisfies(subst):
                                can = False

                        if not can:
                            continue

                        o = opt.Option(
                            [sb.EmptySubstitution(vr) for vr in new_eq.template.get_vars_set() if vr != var],
                            None
                        )

                        trivial_eq = o.apply_to(new_eq)
                        if trivial_eq.is_solved:
                            child_node.children.append(cn.CompressionNode(trivial_eq, o, None, []))

                    continue

                self._solve(child_node)
