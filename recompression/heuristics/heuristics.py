from abc import ABC

from recompression.models import equation as eq, option as opt


class Heurisitcs(ABC):
    def is_satisfable(self, equation: eq.Equation, option: opt.Option) -> bool:
        ...
