import typing
from dataclasses import dataclass

from recompression.models import const
from recompression.models import substitution
from recompression.models import var
from utils.symbols import EPSILON


@dataclass(frozen=True, unsafe_hash=True)
class VarNotEmpty:
    """
    Класс, описывающий ограничение на переменную: переменная не пустая
    """
    var: var.Var

    def is_substitution_satisfies(self, subst: substitution.Substitution) -> bool:
        return not isinstance(subst, substitution.EmptySubstitution) or subst.var != self.var

    def __str__(self):
        return f'{self.var}≠{EPSILON}'

    __repr__ = __str__


@dataclass(frozen=True, unsafe_hash=True)
class VarNotStartsWith:
    """
    Класс, описывающий ограничение на переменную: переменная не начинается на какую-либо константу
    """
    var: var.Var
    const: const.Const

    def is_substitution_satisfies(self, subst: substitution.Substitution) -> bool:
        return not isinstance(subst, substitution.PopLeft) or subst.var != self.var or subst.const != self.const

    def __str__(self):
        return f'{self.var}≠{self.const}{self.var}'

    __repr__ = __str__


@dataclass(frozen=True, unsafe_hash=True)
class VarNotEndsWith:
    """
    Класс, описывающий ограничение на переменную: переменная не заканчивается на какую-либо константу
    """
    var: var.Var
    const: const.Const

    def is_substitution_satisfies(self, subst: substitution.Substitution) -> bool:
        return not isinstance(subst, substitution.PopRight) or subst.var != self.var or subst.const != self.const

    def __str__(self):
        return f'{self.var}≠{self.var}{self.const}'

    __repr__ = __str__


Restriction = VarNotEmpty | VarNotStartsWith | VarNotEndsWith


@dataclass(frozen=True)
class RestrictionOR:
    left: Restriction
    right: Restriction

    def __post_init__(self):
        if self.left == self.right:
            raise ValueError(f'left {self.left} cannot be equal to the right {self.right}')

    def is_substitution_satisfies(self, subst: substitution.Substitution) -> bool:
        return self.left.is_substitution_satisfies(subst) or self.right.is_substitution_satisfies(subst)

    def __str__(self):
        return f'{self.left} ∨ {self.right}'

    __repr__ = __str__


@dataclass
class RestrictionAND:
    simple_restrictions: list[Restriction]
    restriction_or: RestrictionOR | None

    def __hash__(self):
        return sum([hash(r) for r in self.simple_restrictions]) + hash(self.restriction_or)

    def __post_init__(self):
        if self.simple_restrictions is None:
            self.simple_restrictions = []

        if len(self.simple_restrictions) == 0:
            raise ValueError('simple restrictions cannot be empty')
        elif len(self.simple_restrictions) == 1 and self.restriction_or is None:
            raise ValueError('at least 2 simple restrictions are required')

    def is_substitution_satisfies(self, subst: substitution.Substitution) -> bool:
        restriction_or_satisfies = True
        if self.restriction_or is not None:
            restriction_or_satisfies = self.restriction_or.is_substitution_satisfies(subst)

        return all(
            [restr.is_substitution_satisfies(subst) for restr in self.simple_restrictions]
        ) and restriction_or_satisfies

    def simplify(self) -> typing.Optional[typing.Union[Restriction, 'RestrictionAND', RestrictionOR]]:
        simple_restrs = list(set(self.simple_restrictions))

        if self.restriction_or is None:
            if len(simple_restrs) == 0:
                return None
            if len(simple_restrs) == 1:
                return simple_restrs[0]

            return RestrictionAND(simple_restrs, None)

        is_restriction_or_trivially_true = False
        for restr in simple_restrs:
            if self.restriction_or.left == restr or self.restriction_or.right == restr:
                is_restriction_or_trivially_true = True
                break

        if not is_restriction_or_trivially_true:
            return RestrictionAND(simple_restrs, self.restriction_or)

        if len(simple_restrs) == 0:
            return None
        if len(simple_restrs) == 1:
            return simple_restrs[0]

        return RestrictionAND(simple_restrs, None)

    def __str__(self):
        restr_or_str = ''
        if self.restriction_or is not None:
            restr_or_str = f' & ({self.restriction_or})'

        return ' & '.join(
            [str(restr) for restr in sorted(self.simple_restrictions, key=lambda x: ord(x.var.sym))],
        ) + restr_or_str

    __repr__ = __str__


def display():
    x = var.Var('X')
    y = var.Var('Y')
    z = var.Var('Z')

    not_empty = VarNotEmpty(x)
    not_starts = VarNotStartsWith(y, const.PairConst('a', 2))
    not_ends = VarNotEndsWith(z, const.AlphabetConst('b'))
    restr_or = RestrictionOR(not_starts, not_ends)
    restr_and = RestrictionAND([not_ends, not_starts, not_ends], restr_or)

    print(not_empty)
    print(not_starts)
    print(not_ends)
    print(restr_or)
    print(restr_and)


if __name__ == '__main__':
    display()
