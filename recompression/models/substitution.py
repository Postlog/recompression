from dataclasses import dataclass

from recompression.models import const, var
from utils.symbols import EPSILON


@dataclass(frozen=True)
class PopLeft:
    var: var.Var
    const: const.Const

    def __str__(self):
        return f'{self.var}={self.const}{self.var}'

    __repr__ = __str__


@dataclass(frozen=True)
class PopRight:
    var: var.Var
    const: const.Const

    def __str__(self):
        return f'{self.var}={self.var}{self.const}'

    __repr__ = __str__


@dataclass(frozen=True)
class EmptySubstitution:
    var: var.Var

    def __str__(self):
        return f'{self.var}={EPSILON}'

    __repr__ = __str__


Substitution = PopLeft | PopLeft | EmptySubstitution
