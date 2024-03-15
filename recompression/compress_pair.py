from recompression.models import equation as eq, const as c


class PairCompressor:
    def __init__(self):
        self._version_counter = 1
        self._table = {}

    def reset(self):
        self._version_counter = 1
        self._table = {}

    def compress_pair(self, pair: c.Pair, equation: eq.Equation) -> tuple[c.Const, eq.Equation]:
        """
        Сжимает пару pair в уравнении eq.
        Пара вида a_ib_j превращается в константу a_(max(i, j)+1)
    
        :param pair: сжимаемая пара
        :param equation: уравнение
        :return: new_const - константа, полученная в результате сжатия, equation - новое уравнение
        """
        a, b = pair

        if pair not in self._table:
            self._table[pair] = c.PairConst(a.sym, self._version_counter)

        new_const = self._table[pair]

        self._version_counter += 1

        return new_const, eq.Equation(
            template=equation.template.with_replaced_pair(pair, new_const),
            sample=equation.sample.with_replaced_pair(pair, new_const),
        )
