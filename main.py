import argparse
import sys
from dataclasses import dataclass

from recompression import solver
from recompression.heuristics import counting, prefix_suffix
from recompression.models import equation as eq, const as c, var as v, compression_node as cn
from recompression.output import tree_image


@dataclass
class Config:
    use_counting_heuristics: bool
    use_prefix_suffix_heuristics: bool
    tree_image_path: str | None


def parse_arguments() -> tuple[str, Config]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'equation',
        help='Сопоставление которое необходимо решить'
    )

    parser.add_argument(
        '-z3',
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
        help='Использовать эвристику подсчета констант (z3)'
    )

    parser.add_argument(
        '-pref-suff',
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
        help='Использовать эвристику подсчета префиксов и суффиксов'
    )

    parser.add_argument(
        '-output',
        required=False,
        metavar='PATH',
        help='Сохранить дерево разбора по пути PATH'
    )

    args = parser.parse_args()

    return args.equation, Config(
        use_counting_heuristics=args.z3,
        use_prefix_suffix_heuristics=args.pref_suff,
        tree_image_path=args.output
    )


def parse_equation(raw: str) -> eq.Equation:
    chunks = raw.replace(' ', '').split('=')

    if len(chunks) != 2:
        raise ValueError('Сопоставление должно содержать символ =')

    tpl_raw, spl_raw = chunks

    tpl = eq.Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in tpl_raw])
    spl = eq.Sample(*[c.AlphabetConst(sym) for sym in spl_raw])

    return eq.Equation(tpl, spl)

def main():
    equation_raw, config = parse_arguments()


    try:
        equation = parse_equation(equation_raw)
    except ValueError as e:
        print(e, file=sys.stderr)
        exit(1)

    heuristics = []
    if config.use_prefix_suffix_heuristics:
        heuristics.append(prefix_suffix.PrefixSuffixHeuristics())
    if config.use_counting_heuristics:
        heuristics.append(counting.CountingHeuristics())

    s = solver.Solver(heuristics)

    try:
        root_node, solver_stats = s.solve(equation)
    except ValueError as e:
        print(e, file=sys.stderr)
        exit(1)

    print(f'Решено за {solver_stats.total_working_time:.4f} секунд')

    stats = collect_tree_stats(root_node)
    for name, timings in solver_stats.heuristics_timings.items():
        print(f'Эвристика {name} в среднем работала за {(sum(timings) / len(timings)):.4f} секунд')
    for name, count in solver_stats.branches_dropped_by_heuristics.items():
        print(f'Эвристика {name} отбросила {count} ветвей')

    print(f'Глубина итогового дерева {stats.depth}')
    print(f'Всего в дереве {stats.nodes_count} узлов')
    print(f'Всего в дереве {stats.solution_nodes_count} узлов-решений')

    if config.tree_image_path is not None:
        print('Сохраняется изображение...')
        generator = tree_image.TreeImage()
        try:
            generator.generate(config.tree_image_path, root_node)
        except Exception as e:
            print(e, file=sys.stderr)
            exit(1)
        print(f'Изображение сохранено по пути {config.tree_image_path}')


@dataclass
class TreeStats:
    depth: int
    nodes_count: int
    solution_nodes_count: int


def collect_tree_stats(node: cn.CompressionNode) -> TreeStats:
    total, solved = calculate_nodes(node)

    return TreeStats(
        depth=calculate_tree_depth(node),
        nodes_count=total,
        solution_nodes_count=solved
    )


def calculate_nodes(node: cn.CompressionNode) -> tuple[int, int]:
    children_ids = set()
    solution_ids = set()

    def _inner(innder_node: cn.CompressionNode):
        if innder_node.equation.is_solved:
            solution_ids.add(innder_node.id)

        children_ids.add(innder_node.id)

        for child in innder_node.children:
            _inner(child)

    _inner(node)

    return len(children_ids), len(solution_ids)


def calculate_tree_depth(node: cn.CompressionNode) -> int:
    if len(node.children) == 0:
        return 1

    max_depth = 0
    for child in node.children:
        max_depth = max(max_depth, calculate_tree_depth(child))

    return max_depth + 1


if __name__ == '__main__':
    main()
