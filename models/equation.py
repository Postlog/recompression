from dataclasses import dataclass

from models.const import Const
from models.var import Var

EQ_LHS = tuple[Var | Const, ...]
EQ_RHS = tuple[Const, ...]


@dataclass(frozen=True)
class Equation:
    left: EQ_LHS
    right: EQ_RHS

    def __str__(self):
        left = ''.join(str(el) for el in self.left)
        right = ''.join(str(el) for el in self.right)
        return f'{left}={right}'


def parse_equation(left_raw: str, right_raw: str, symbols: set[str], variables: set[str]) -> Equation:
    intersection = symbols.intersection(variables)
    if intersection != set():
        raise ValueError(f'symbols and variables must contain different characters, intersection: {intersection}')

    left = []
    right = []

    for char in left_raw:
        if char in symbols:
            left.append(Const(char))
        elif char in variables:
            left.append(Var(char))
        else:
            raise ValueError(f'character \'{char}\' is not a symbol or variable')

    for char in right_raw:
        if char in symbols:
            right.append(Const(char))
        else:
            raise ValueError(f'character \'{char}\' is not a symbol')

    return Equation(left=tuple(left), right=tuple(right))
