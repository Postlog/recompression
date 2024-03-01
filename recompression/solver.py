from recompression.compress_pair import compress_pair
from recompression.get_empty_substitutions import get_empty_options, get_full_empty_option
from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.get_options_for_pair import get_options_for_pair
from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, compression_node as cn, actions as ac
from utils.time import timeit


class Solver:
    def __init__(self, equation_heuristics: list[h.Heurisitcs], max_depth: int = None):
        self._heuristics = equation_heuristics
        self._max_depth = max_depth

    @timeit("equation solving")
    def solve(self, equation: eq.Equation) -> cn.CompressionNode:
        if len(equation.template.get_vars()) == 0:
            raise ValueError('template must have at least 1 variable')

        if len(equation.sample.elements) == 0:
            raise ValueError('sample cannot be empty')

        if equation.is_solved:
            return cn.CompressionNode.empty(equation)

        root = cn.CompressionNode.empty(equation)
        self._solve(root, 1)

        return root

    def _solve(self, node: cn.CompressionNode, depth: int):
        node_eq = node.equation
        actions = get_most_profit_actions(node_eq.sample)

        empty_options = get_empty_options(node_eq.template, node.option)

        for action in actions:
            if not isinstance(action, ac.CompressPairAction):
                print(f'ERROR: unknown action {action}')
                continue

            for empty_option in empty_options:
                empty_eq = empty_option.apply_to(node_eq)
                opts = get_options_for_pair(empty_eq.template, action.pair, empty_option)
                for option in opts:
                    new_const, new_eq = compress_pair(
                        action.pair,
                        option.apply_to(empty_eq)
                    )

                    new_node = cn.CompressionNode(new_eq, option, (action, new_const), [])

                    if new_eq.is_solved:
                        node.children.append(new_node)
                        continue

                    if not all([heuristic.is_satisfable(new_eq, option) for heuristic in self._heuristics]):
                        print(f'WARN: equation {new_eq} dropped bacause of heuristics, option {option}')
                        continue

                    node.children.append(new_node)

                    empty_opt = get_full_empty_option(new_eq.template, option)
                    if empty_opt is not None:
                        emptied_eq = empty_opt.apply_to(new_eq)
                        if emptied_eq.is_solved:
                            new_node.children.append(cn.CompressionNode(
                                equation=emptied_eq,
                                option=empty_opt,
                                compression_action=None,
                                children=[]
                            ))
                            continue

                    if self._max_depth is None or depth <= self._max_depth:
                        self._solve(new_node, depth + 1)
