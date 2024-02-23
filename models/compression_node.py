from dataclasses import dataclass
from typing import Type

from models.equation import Equation
from models.var_restriction import AbstractVarRestriction


@dataclass(frozen=True)
class CompressionNode:
    equation: Equation
    vars_restrictions: tuple[Type[AbstractVarRestriction]]
