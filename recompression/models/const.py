from abc import ABC
from dataclasses import dataclass
from typing import TypeVar

from utils.symbols import number_to_index_mapping


@dataclass(frozen=True)
class AbstractConst(ABC):
    sym: str

    def __str__(self):
        return f'{self.sym.lower()}'

    __repr__ = __str__


@dataclass(frozen=True)
class AlphabetConst(AbstractConst):

    def __str__(self):
        return f'{self.sym.lower()}'

    __repr__ = __str__


@dataclass(frozen=True)
class PairConst(AbstractConst):
    version: int

    def __str__(self):
        version = ''.join([number_to_index_mapping[char] for char in str(self.version)])

        return f'{super().__str__()}{version}'

    __repr__ = __str__


@dataclass(frozen=True)
class BlockConst(AbstractConst):
    version: int
    compression_factor: int | None = None

    def __str__(self):
        version = ''.join([number_to_index_mapping[char] for char in str(self.version)])
        if self.compression_factor is None:
            factor = '_'
        else:
            factor = ''.join([number_to_index_mapping[char] for char in str(self.compression_factor)])
        return f'{super().__str__()}{version}.{factor}'


Const = TypeVar('Const', AlphabetConst, PairConst, BlockConst)

Pair = tuple[AlphabetConst | PairConst | BlockConst, AlphabetConst | PairConst | BlockConst]

if __name__ == '__main__':
    bc = BlockConst('B', 10, )
    print(bc)
