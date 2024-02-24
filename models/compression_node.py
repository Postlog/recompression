from dataclasses import dataclass
from typing import Type

from models.const import Const
from models.equation import Equation
from models.var import Var
from models.var_restriction import AbstractVarRestriction


@dataclass(frozen=True)
class RecompressionContext:
    alphabet: set[Const]
    variables: set[Var]


@dataclass(frozen=True)
class CompressionNode:
    equation: Equation
    vars_restrictions: dict[Var, list[Type[AbstractVarRestriction]]]
