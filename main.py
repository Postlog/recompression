import sys

from recompression import solver
from recompression.heuristics import counting, prefix_suffix
from recompression.models import equation as eq, const as c, var as v, compression_node as cn, option as opt, substitution as sb
from recompression.output import tree_image
from utils.time import timeit


@timeit("total")
def main():
    if len(sys.argv) != 2:
        print('Необходимо указать сопоставление, например: python main.py XY=bba')
        exit(1)

    eq_raw = sys.argv[1].replace(' ', '')

    chunks = eq_raw.split('=')

    if len(chunks) != 2:
        print('Сопоставление должно содержать символ =')
        exit(1)

    tpl_raw, spl_raw = chunks

    template = eq.Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in tpl_raw])
    sample = eq.Sample(*[c.AlphabetConst(sym) for sym in spl_raw])

    equation = eq.Equation(template, sample)
    s = solver.Solver([prefix_suffix.PrefixSuffixHeuristics(), counting.CountingHeuristics()])

    root_node = s.solve(equation)

    print_solutions_paths(root_node)

    generator = tree_image.TreeImage()
    generator.generate(f'{eq_raw}.svg', root_node)


def print_solutions_paths(node: cn.CompressionNode, path=None):
    if path is None:
        path = []

    path.append(node.equation)

    if node.equation.is_solved:
        print(' -> '.join([str(e) for e in path]))

    for child in node.children:
        print_solutions_paths(child, path)

    path.pop()


if __name__ == '__main__':
    main()
