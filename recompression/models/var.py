from dataclasses import dataclass
from typing import TypeVar

VarRestriction = TypeVar('VarRestriction',
                         'VarNotEmpty', 'VarNotEndsWith', 'VarNotStartsWith', 'VarNotStartsOrEndsWith',
                         )


@dataclass(frozen=True)
class Var:
    sym: str

    def __str__(self):
        return f'{self.sym.upper()}'

    __repr__ = __str__
