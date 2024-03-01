import copy
import itertools
from dataclasses import dataclass

from recompression.models import const as c, substitution as s, var as v
from utils.list import indexes


class Template:
    elements: list[v.Var | c.Const]

    def __init__(self, *elements: v.Var | c.Const):
        self.elements = list(elements)

    def __str__(self):
        return ''.join(str(el) for el in self.elements)

    __repr__ = __str__

    def __eq__(self, other: 'Template'):
        if len(self.elements) != len(other.elements):
            return False

        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False

        return True

    def get_vars(self) -> set[v.Var]:
        """
        :return: множество переменных выражения
        """

        return set([var for var in self.elements if isinstance(var, v.Var)])

    def get_consts(self) -> list[c.AbstractConst]:
        """
        :return: множество констант выражения
        """

        dedup = set()
        result = []
        for element in self.elements:
            if isinstance(element, c.AbstractConst) and element not in dedup:
                result.append(element)
                dedup.add(element)

        return result

    def get_pair_uncrossings(self, var: v.Var, pair: c.Pair) -> list:
        pass

    def apply_substitution(self, subst: s.Substitution) -> 'Template':
        elements_cpy = copy.deepcopy(self.elements)

        var_indexes = indexes(self.elements, subst.var)
        if len(var_indexes) == 0:
            return Template(*elements_cpy)
        
        elements_cpy = [el for el in elements_cpy if el != subst.var]

        replacement = None
        if isinstance(subst, s.PopLeft):
            replacement = [subst.const, subst.var]
        elif isinstance(subst, s.PopRight):
            replacement = [subst.var, subst.const]
        elif isinstance(subst, s.EmptySubstitution):
            replacement = []

        for j, index in enumerate(var_indexes):
            for i, replacer in enumerate(replacement):
                elements_cpy.insert(j + index + i, replacer)

        return Template(*elements_cpy)

    def with_replaced_pair(self, pair: c.Pair, const: c.Const) -> 'Template':
        """
        Создает новый экземпляр Template, в котором пара pair заменена на константу const

        :param pair: пара для замены
        :param const: константа, на которую будет заменена пара
        :return: новый экзепляр Template с замененной парой
        """

        compressed_elements = []

        i = 0
        while i < len(self.elements):
            if i < len(self.elements) - 1 and (self.elements[i], self.elements[i + 1]) == pair:
                compressed_elements.append(const)
                i += 2
            else:
                compressed_elements.append(self.elements[i])
                i += 1

        return Template(*compressed_elements)

    def get_pair_occourance_count(self, pair: c.Pair):
        """
        Считает число вхождений пары pair в выражение

        :param pair: - пара
        :return: int - число вхождений пары в выражение
        """
        count = 0

        for i in range(len(self.elements) - 1):
            if self.elements[i] == pair[0] and self.elements[i + 1] == pair[1]:
                count += 1

        return count


@dataclass
class SampleBlock:
    const: c.Const
    len: int
    count: int


class Sample:
    elements: list[c.Const]

    def __init__(self, *elements: v.Var | c.Const):
        self.elements = list(elements)

    def __str__(self):
        return ''.join(str(el) for el in self.elements)

    __repr__ = __str__

    def __eq__(self, other: 'Template'):
        if len(self.elements) != len(other.elements):
            return False

        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False

        return True

    def get_pairs(self) -> dict[c.Pair, int]:
        pairs = {}
        for i in range(len(self.elements) - 1):
            a, b = self.elements[i], self.elements[i + 1]
            if a != b:
                pair = (a, b)
                if pair not in pairs:
                    pairs[pair] = 1
                else:
                    pairs[pair] += 1

        return pairs

    def get_blocks(self) -> list[tuple[SampleBlock, list[int]]]:
        blocks = {}  # {(const, len): count}
        blocks_indexes = {}  # {(const, len): [index, index]}
        i = 0
        for const, g in itertools.groupby(self.elements):
            block_len = len(list(g))
            if block_len < 2:
                i += block_len
                continue

            key = (const, block_len)
            if key not in blocks:
                blocks[key] = 1
                blocks_indexes[key] = [i]
            else:
                blocks[key] += 1
                blocks_indexes[key].append(i)

            i += block_len

        result = []
        for key, count in blocks.items():
            result.append(
                (SampleBlock(const=key[0], len=key[1], count=count), blocks_indexes[key]),
            )

        return result

    def get_consts(self) -> list[c.AbstractConst]:
        dedup = set()
        result = []
        for element in self.elements:
            if isinstance(element, c.AbstractConst) and element not in dedup:
                result.append(element)
                dedup.add(element)

        return result

    def with_replaced_pair(self, pair: c.Pair, const: c.Const) -> 'Sample':
        """
        Создает новый экземпляр Sample, в котором пара pair заменена на константу const

        :param pair: пара для замены
        :param const: константа, на которую будет заменена пара
        :return: новый экзепляр Sample с замененной парой
        """

        compressed_elements = []

        i = 0
        while i < len(self.elements):
            if i < len(self.elements) - 1 and (self.elements[i], self.elements[i + 1]) == pair:
                compressed_elements.append(const)
                i += 2
            else:
                compressed_elements.append(self.elements[i])
                i += 1

        return Sample(*compressed_elements)


@dataclass(frozen=True)
class Equation:
    template: Template
    sample: Sample

    @property
    def is_solved(self) -> bool:
        if len(self.sample.elements) == 1:
            return len(self.template.elements) == 1 and self.template.elements[0] == self.sample.elements[0]

        return len(self.sample.elements) == 0 and len(self.template.elements) == 0

    def normalize(self) -> 'Equation':
        tpl_els = self.template.elements
        spl_els = self.sample.elements

        prefix_len = 0
        min_len = min(len(tpl_els), len(spl_els))
        while prefix_len < min_len and tpl_els[prefix_len] == spl_els[prefix_len]:
            prefix_len += 1

        suffix_len = 0
        while suffix_len < min_len - prefix_len and tpl_els[-(suffix_len + 1)] == spl_els[-(suffix_len + 1)]:
            suffix_len += 1

        return Equation(
            Template(*tpl_els[prefix_len:len(tpl_els) - suffix_len]),
            Sample(*spl_els[prefix_len:len(spl_els) - suffix_len]),
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Equation):
            return False

        return self.template == other.template and self.sample == other.sample

    def __str__(self):
        if len(self.template.elements) == 0 or len(self.sample.elements) == 0:
            return f'<empty equation>'

        return f'{self.template} ＝ {self.sample}'

    __repr__ = __str__


if __name__ == '__main__':
    eq_raw = 'abab=abab'

    template = Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in eq_raw.split('=')[0]])
    sample = Sample(*[c.AlphabetConst(sym) for sym in eq_raw.split('=')[1]])

    eq = Equation(template, sample)

    print(eq.normalize())
    print(eq.normalize())
    print(eq.normalize().is_solved)
