import copy

from models.compression_node import CompressionNode, RecompressionContext
from models.const import Const
from models.equation import Equation
from models.var import Var

Pair = tuple[Const, Const]


def get_all_uncrossings(var: Var, pair: Pair) -> list[list[Const | Var]]:
    a, b = pair

    return [
        [a, var],  # aX
        [b, var],  # bX
        [a, var, b],  # aXb
        [b, var, a],  # bXa
        [var, a],  # Xa
        [var, b],  # Xb
        []  # epsilon
    ]


def indexes(l: list, el: any) -> list[int]:
    return [i for i, val in enumerate(l) if val == el]


def uncross_pair(
        pair: Pair,
        node: CompressionNode,
        context: RecompressionContext,
) -> list[CompressionNode]:
    left = list(node.equation.left)

    new_nodes = []

    for var in context.variables:
        uncrossings = get_all_uncrossings(var, pair)
        var_indexes = indexes(left, var)
        if len(var_indexes) == 0:
            continue

        for uncrossing in uncrossings:
            new_left = copy.deepcopy(left)
            new_left.remove(var)

            for idx in var_indexes:
                for i, uncrossing_element in enumerate(uncrossing):
                    new_left.insert(idx + i, uncrossing_element)

            new_nodes.append(CompressionNode(
                equation=Equation(left=tuple(new_left), right=node.equation.right),
                vars_restrictions={},
            ))

    return new_nodes


def compress_pair(pair: Pair, eq: Equation) -> Equation:
    a, b = pair

    new_const = Const(a.sym, a.index + 1)

    new_right: list[Const] = []
    i = 0
    while i < len(eq.right):
        if i < len(eq.right) - 1 and (eq.right[i], eq.right[i + 1]) == pair:
            new_right.append(new_const)
            i += 2
        else:
            new_right.append(eq.right[i])
            i += 1

    new_left: list[Const | Var] = []
    i = 0
    while i < len(eq.left):
        if i < len(eq.left) - 1 and (eq.left[i], eq.left[i + 1]) == pair:
            new_left.append(new_const)
            i += 2
        else:
            new_left.append(eq.left[i])
            i += 1

    return Equation(left=tuple(new_left), right=tuple(new_right))


def main():
    alphabet = {Const('a'), Const('b')}
    variables = {Var('X')}
    eq = Equation(
        left=(Const('a'), Const('b'), Var('X')),
        right=(Const('a'), Const('b'), Const('a'), Const('b'))
    )
    ctx = RecompressionContext(alphabet=alphabet, variables=variables)

    nodes = [CompressionNode(eq, {})]

    pair = (Const('a'), Const('b'))

    while True:
        uncrossings = []
        for node in nodes:
            uncrossings.extend(uncross_pair(pair, node, ctx))

        nodes = []
        for uncrossing in uncrossings:
            nodes.append(CompressionNode(compress_pair(pair, uncrossing.equation), {}))

        found = False
        for node in nodes:
            if len(node.equation.left) == len(node.equation.right):
                print(node.equation)

        if found:
            break


if __name__ == '__main__':
    main()
