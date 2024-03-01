from recompression.models import equation as eq, const as c


def compress_pair(pair: c.Pair, equat: eq.Equation) -> tuple[c.Const, eq.Equation]:
    """
    Сжимает пару pair в уравнении eq.
    Пара вида a_ib_j превращается в константу a_(max(i, j)+1)

    :param pair: сжимаемая пара
    :param equat: уравнение
    :return: new_const - константа, полученная в результате сжатия, equation - новое уравнение
    """
    a, b = pair

    original_version_a = a.version if not isinstance(a, c.AlphabetConst) else 0
    original_version_b = b.version if not isinstance(b, c.AlphabetConst) else 0

    new_const = c.PairConst(a.sym, max(original_version_a, original_version_b) + 1)

    return new_const, eq.Equation(
        template=equat.template.with_replaced_pair(pair, new_const),
        sample=equat.sample.with_replaced_pair(pair, new_const),
    )
