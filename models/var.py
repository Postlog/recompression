from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    sym: str

    def __str__(self):
        return self.sym.upper()