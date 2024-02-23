from abc import ABC
from dataclasses import dataclass

from models.const import Const
from models.var import Var


@dataclass(frozen=True)
class AbstractVarRestriction(ABC):
    var: Var


@dataclass(frozen=True)
class VarNotEmpty(AbstractVarRestriction):
    """
    Класс, описывающий ограничение на переменную: переменная не пустая
    """

    def __str__(self):
        return f'{self.var} is not empty'


@dataclass(frozen=True)
class VarNotStartsWith(AbstractVarRestriction):
    """
    Класс, описывающий ограничение на переменную: переменная не начинается на какую-либо константу
    """
    const: Const

    def __str__(self):
        return f'{self.var} is not starts with {self.const}'


@dataclass(frozen=True)
class VarNotEndsWith(AbstractVarRestriction):
    """
    Класс, описывающий ограничение на переменную: переменная не заканчивается на какую-либо константу
    """
    const: Const

    def __str__(self):
        return f'{self.var} is not ends with {self.const}'


@dataclass(frozen=True)
class VarNotStartsAndEndsWith(AbstractVarRestriction):
    """
    Класс, описывающий ограничение на переменную: переменная не начинается на какую-либо константу
    и не заканчивается на какую-либо константу
    """
    not_starts_with: Const
    not_ends_with: Const

    def __str__(self):
        return f'{self.var} is not starts with {self.not_starts_with} and not ends with {self.not_ends_with}'
