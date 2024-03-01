from dataclasses import dataclass

from recompression.models.const import Const, Pair


@dataclass
class CompressBlockAction:
    const: Const
    len: int
    index: int

    def __str__(self):
        return f'BlockComp({self.const})'

    __repr__ = __str__


@dataclass
class CompressPairAction:
    pair: Pair

    def __str__(self):
        return f'PairComp{self.pair}'

    __repr__ = __str__
