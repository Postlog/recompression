from anytree import Node
from anytree.exporter import DotExporter

from recompression.compress_pair import compress_pair
from recompression.get_empty_substitutions import get_empty_options, get_full_empty_option
from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.get_options_for_pair import get_options_for_pair
from recompression.heuristics.counting import is_satisfable
from recompression.models import compression_node as cn, equation as eq, actions as ac, const as c, var as v, \
    option as opt, substitution as s
from utils.time import timeit


def convert_to_anytree_node(node: cn.CompressionNode):
    name = f'{node.option}\n' if node.option.restriction is not None or len(node.option.substitutions) != 0 else ''
    name += f'{node.compression_action}\n' if node.compression_action is not None else ''

    name += f'{node.equation}'

    attrs = {}
    if node.equation.is_solved:
        attrs["is_solution"] = True
    elif len(node.children) == 0:
        attrs["is_bad"] = True

    anytree_node = Node(name, **attrs)

    for child in node.children:
        anytree_child = convert_to_anytree_node(child)
        anytree_child.parent = anytree_node
    return anytree_node


def is_duplicate(root: cn.CompressionNode, target_equation: eq.Equation) -> bool:
    if root.equation == target_equation:
        return True

    for child in root.children:
        if is_duplicate(child, target_equation):
            return True

    return False


def get_eps_all_option(node: cn.CompressionNode) -> opt.Option | None:
    substs = []
    if node.option is not None:
        for var in node.equation.template.get_vars():
            subst = s.EmptySubstitution(var)
            if node.option.restriction is not None and not node.option.restriction.is_substitution_satisfies(subst):
                return None
            substs.append(subst)

    return opt.Option(substs, None)


# @timeit
def solve(root_node: cn.CompressionNode, node: cn.CompressionNode):
    node_eq = node.equation
    actions = get_most_profit_actions(node_eq.sample)

    empty_options = get_empty_options(node_eq.template, node.option)

    for action in actions:
        if not isinstance(action, ac.CompressPairAction):
            print(f'ERROR: unknown action {action}')
            continue

        for empty_option in empty_options:
            empty_eq = empty_option.apply_to(node_eq)

            for option in get_options_for_pair(empty_eq.template, action.pair, empty_option):
                new_const, new_eq = compress_pair(
                    action.pair,
                    option.apply_to(empty_eq)
                )

                new_node = cn.CompressionNode(new_eq, option, action, [])
                node.children.append(new_node)

                if new_eq.is_solved:
                    continue

                if not is_satisfable(new_eq, option):
                    continue

                if len(new_eq.sample.elements) == 1:
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

                solve(root_node, new_node)


@timeit
def main():
    eq_raw = 'abXY=abbab'

    template = eq.Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in eq_raw.split('=')[0]])
    sample = eq.Sample(*[c.AlphabetConst(sym) for sym in eq_raw.split('=')[1]])

    equat = eq.Equation(template, sample)
    tree_root = cn.CompressionNode.empty(equat)
    solve(tree_root, tree_root)
    print('solve finished')
    print_solutions(tree_root)

    anytree_root = convert_to_anytree_node(tree_root)
    DotExporter(anytree_root, nodeattrfunc=node_attr_func).to_picture(f'{eq_raw}.png')


def node_attr_func(node: Node) -> str | None:
    if hasattr(node, 'is_solution'):
        return 'color=green'
    elif hasattr(node, 'is_bad'):
        return 'color=red'

    return None


def print_solutions(node: cn.CompressionNode, path=None):
    if path is None:
        path = []

    path.append(node.equation)

    if node.equation.is_solved:
        print(' -> '.join([str(eq) for eq in path]))

    for child in node.children:
        print_solutions(child, path)

    path.pop()


if __name__ == '__main__':
    main()

"""
На данном моменте я генерирую все возможные доставания констант из каждой переменной шаблона,
например PairComp(a, b) на шаблоне XabY порождает извлеченя: X -> bX, X -> Xa, X -> X, X -> eps, аналогично для Y
а далее собираю все возможные комбинации этих извлечений:

1. X -> bX
2. X -> Xa
3. X -> X
4. X -> eps
5. Y -> bY
6. Y -> Ya
7. Y -> Y
8. Y -> eps
9. X -> bX, Y -> bY
10. X -> bX, Y -> bY
и тд и тп

 


"""

"""
Перед извлечением рассматриваем случай когда переменные обращаются в eps:
X -> eps
X !-> eps
Y -> eps
Y !-> eps
"""
