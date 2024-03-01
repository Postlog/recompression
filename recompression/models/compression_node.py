from dataclasses import dataclass

from recompression.models import actions as ac, equation as eq, option as opt


@dataclass
class CompressionNode:
    equation: eq.Equation
    option: opt.Option
    compression_action: ac.CompressBlockAction | ac.CompressPairAction | None
    children: list['CompressionNode']

    @staticmethod
    def empty(equation: eq.Equation) -> 'CompressionNode':
        return CompressionNode(
            equation=equation,
            option=opt.Option([], None),
            compression_action=None,
            children=[]
        )
