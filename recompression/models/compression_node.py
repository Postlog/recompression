from dataclasses import dataclass

from recompression.models import actions as ac, equation as eq, option as opt, const as c


@dataclass
class CompressionNode:
    equation: eq.Equation
    option: opt.Option | None
    compression_action: tuple[ac.CompressBlockAction | ac.CompressPairAction, c.BlockConst | c.PairConst] | None
    children: list['CompressionNode']

    @staticmethod
    def empty(equation: eq.Equation) -> 'CompressionNode':
        return CompressionNode(
            equation=equation,
            option=None,
            compression_action=None,
            children=[]
        )
