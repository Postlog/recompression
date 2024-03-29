import copy
import itertools
from dataclasses import dataclass
from enum import Enum

from recompression.models import const as c, substitution as s, var as v
from utils.list import indexes


class VarGroupType(Enum):
    GENERIC = 1
    LEFT = 2
    RIGHT = 3
    LEFT_RIGHT = 4

    def __str__(self):
        return f'{self.name}'

    __repr__ = __str__


class Template:
    elements: list[v.Var | c.Const]

    def __init__(self, *elements: v.Var | c.Const):
        self.elements = list(elements)

    def __str__(self):
        if len(self.elements) == 0:
            return '<empty>'
        return ''.join(str(el) for el in self.elements)

    __repr__ = __str__

    def __eq__(self, other: 'Template'):
        if len(self.elements) != len(other.elements):
            return False

        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False

        return True

    def get_vars_set(self) -> set[v.Var]:
        """
        :return: множество переменных выражения
        """

        return set([var for var in self.elements if isinstance(var, v.Var)])

    def get_consts_set(self) -> set[c.AbstractConst]:
        """
        :return: множество констант выражения
        """

        return set(self.get_consts())

    def get_consts(self) -> list[c.AbstractConst]:
        return [const for const in self.elements if isinstance(const, c.AbstractConst)]

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

    def get_var_groups(self) -> list[tuple[VarGroupType, int, int]]:
        result = []
        current_group = []
        for i, el in enumerate(self.elements):
            if isinstance(el, v.Var):
                current_group.append(el)
                continue

            for (t, start, end) in self._get_max_var_subgroups_by_types(current_group):
                subgroup = current_group[start:end]
                result.append(
                    (t, i - len(current_group) + start, len(subgroup)),
                )

            current_group = []

        for (t, start, end) in self._get_max_var_subgroups_by_types(current_group):
            subgroup = current_group[start:end]
            result.append(
                (t, len(self.elements) - len(current_group) + start, len(subgroup)),
            )

        return result

    @staticmethod
    def _get_max_var_subgroups_by_types(group: list[v.Var]) -> list[tuple[VarGroupType, int, int | None]]:
        ts = []
        if len(group) > 0:
            ts.append((VarGroupType.GENERIC, 0, None))

        for i in range(len(group)):
            g = group[i:]
            if len(g) > 1 and g[0] not in g[1:]:
                ts.append((VarGroupType.LEFT, i, None))
                break

        for i in range(len(group)):
            i_end = -i if i > 0 else None
            g = group[:i_end]
            if len(g) > 1 and g[-1] not in g[:-1]:
                ts.append((VarGroupType.RIGHT, 0, i_end))
                break

        for i in range(len(group)):
            g = group[i:]
            if len(g) > 2 and g[0] == g[-1] and g[0] not in g[1:-1]:
                ts.append((VarGroupType.LEFT_RIGHT, i, None))
                break
            if len(g) > 2 and g[0] != g[-1] and g[0] not in g[1:] and g[-1] not in g[:-1]:
                ts.append((VarGroupType.LEFT_RIGHT, i, None))
                break

        for i in range(len(group)):
            i_end = -i if i > 0 else None
            g = group[:i_end]
            if len(g) > 2 and g[0] == g[-1] and g[0] not in g[1:-1]:
                ts.append((VarGroupType.LEFT_RIGHT, 0, i_end))
                break
            if len(g) > 2 and g[0] != g[-1] and g[0] not in g[1:] and g[-1] not in g[:-1]:
                ts.append((VarGroupType.LEFT_RIGHT, 0, i_end))
                break

        for i in range(len(group)):
            i_end = -i if i > 0 else None
            g = group[i:i_end]
            if len(g) > 2 and g[0] == g[-1] and g[0] not in g[1:-1]:
                ts.append((VarGroupType.LEFT_RIGHT, i, i_end))
                break
            if len(g) > 2 and g[0] != g[-1] and g[0] not in g[1:] and g[-1] not in g[:-1]:
                ts.append((VarGroupType.LEFT_RIGHT, i, i_end))
                break

        return list(set(ts))

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

    def get_consts_prefix_suffix(self) -> tuple[list[v.Var | c.Const], list[v.Var | c.Const]]:
        prefix_len = 0
        while prefix_len < len(self.elements) and not isinstance(self.elements[prefix_len], v.Var):
            prefix_len += 1

        suffix_len = 0
        while suffix_len < len(self.elements) - prefix_len and not isinstance(
                self.elements[len(self.elements) - suffix_len - 1], v.Var):
            suffix_len += 1

        return self.elements[:prefix_len], self.elements[len(self.elements) - suffix_len:]

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

    def __init__(self, *elements: c.Const):
        self.elements = list(elements)

    def __str__(self):
        if len(self.elements) == 0:
            return '<empty>'
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

    def get_consts_set(self) -> set[c.AbstractConst]:
        return set(self.elements)

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
        if len(self.template.elements) == 1 and isinstance(self.template.elements[0], v.Var):
            return True

        if len(self.sample.elements) != len(self.template.elements):
            return False

        for i, el in enumerate(self.sample.elements):
            if el != self.template.elements[i]:
                return False

        return True

    def __eq__(self, other) -> bool:
        if not isinstance(other, Equation):
            return False

        return self.template == other.template and self.sample == other.sample

    def __str__(self):
        return f'{self.template}={self.sample}'

    __repr__ = __str__


def main():
    eq_raw = 'XaXXYXX=ac'

    template = Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in eq_raw.split('=')[0]])
    sample = Sample(*[c.AlphabetConst(sym) for sym in eq_raw.split('=')[1]])

    eq = Equation(template, sample)

    print(eq)
    print(template.get_consts_prefix_suffix())
    for (t, start, l) in template.get_var_groups():
        print(t, template.elements[start:start + l])


if __name__ == '__main__':
    main()