from dataclasses import dataclass


@dataclass(frozen=True)
class Const:
    sym: str
    index: int = 0

    def __str__(self):
        return f'{self.sym.lower()}_{self.index}'


EPSILON = Const('eps')
