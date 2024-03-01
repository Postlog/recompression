from abc import ABC

from recompression.models import equation as eq


class Heurisitcs(ABC):
    def is_satisfable(self, equation: eq.Equation) -> bool:
        ...
