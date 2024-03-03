from recompression.compress_pair import compress_pair
from recompression.get_empty_substitutions import get_empty_options, get_full_empty_option
from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.get_options_for_pair import get_options_for_pair
from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, compression_node as cn, actions as ac, option as opt
from utils.time import timeit


class Solver:
    def __init__(self, equation_heuristics: list[h.Heurisitcs]):
        self._heuristics = equation_heuristics

    @timeit("equation solving")
    def solve(self, equation: eq.Equation) -> cn.CompressionNode:
        if len(equation.template.get_vars_set()) == 0:
            raise ValueError('template must have at least 1 variable')

        if len(equation.sample.elements) == 0:
            raise ValueError('sample cannot be empty')

        if equation.is_solved:
            return cn.CompressionNode.empty(equation)

        root = cn.CompressionNode.empty(equation)
        self._solve(root)

        return root

    def _solve(self, node: cn.CompressionNode):
        node_eq = node.equation
        actions = get_most_profit_actions(node_eq.sample)

        empty_options = get_empty_options(node_eq.template, node.option)

        for action in actions:
            if isinstance(action, ac.CompressPairAction):
                self._do_pair_compression(node, action, empty_options)
            else:
                print(f'ERROR: unknown action {action}')
                continue

    def _do_pair_compression(
            self,
            node: cn.CompressionNode,
            action: ac.CompressPairAction,
            empty_opts: list[opt.Option],
    ):
        for empty_opt in empty_opts:
            emptied_eq = empty_opt.apply_to(node.equation)
            for option in get_options_for_pair(emptied_eq.template, action.pair, empty_opt):
                new_const, new_eq = compress_pair(
                    action.pair,
                    option.apply_to(emptied_eq)
                )

                new_node = cn.CompressionNode(new_eq, option, (action, new_const), [])

                if new_eq.is_solved:
                    node.children.append(new_node)
                    continue

                is_dropped = False
                for heuristic in self._heuristics:
                    if not heuristic.is_satisfable(new_eq, option):
                        is_dropped = True
                        print(f'WARN: equation {new_eq} dropped bacause of {heuristic.get_name()} heuristics, option {option}')
                        break

                if is_dropped:
                    continue

                node.children.append(new_node)

                o = get_full_empty_option(new_eq.template, option)
                if o is not None:
                    trivial_eq = o.apply_to(new_eq)
                    if trivial_eq.is_solved:
                        new_node.children.append(cn.CompressionNode(trivial_eq, o, None, []))
                        continue

                self._solve(new_node)
