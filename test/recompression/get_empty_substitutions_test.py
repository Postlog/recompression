import pytest

from recompression.get_empty_substitutions import get_empty_options
from recompression.models.const import PairConst, BlockConst, AlphabetConst
from recompression.models.equation import Template
from recompression.models.option import Option
from recompression.models.substitution import EmptySubstitution
from recompression.models.var import Var
from recompression.models.var_restriction import VarNotEmpty, RestrictionAND

X = Var('X')
Y = Var('Y')
Z = Var('Z')

a = AlphabetConst('a')
c = BlockConst('c', 2)
b = PairConst('b', 1)

test_data = [
    [[], None, []],

    [[X], None, [
        Option([], VarNotEmpty(X)),
        Option([EmptySubstitution(X)], None),
    ]],

    [[c, X, b, Y, a], None, [
        Option([], RestrictionAND([VarNotEmpty(X), VarNotEmpty(Y)], None)),
        Option([EmptySubstitution(X)], VarNotEmpty(Y)),
        Option([EmptySubstitution(Y)], VarNotEmpty(X)),
        Option([EmptySubstitution(X), EmptySubstitution(Y)], None),
    ]],

    [[c, X, b, Y, a, Z], None, [
        Option([], RestrictionAND([VarNotEmpty(X), VarNotEmpty(Y), VarNotEmpty(Z)], None)),
        Option([EmptySubstitution(X)], RestrictionAND([VarNotEmpty(Y), VarNotEmpty(Z)], None)),
        Option([EmptySubstitution(Y)], RestrictionAND([VarNotEmpty(X), VarNotEmpty(Z)], None)),
        Option([EmptySubstitution(Z)], RestrictionAND([VarNotEmpty(X), VarNotEmpty(Y)], None)),
        Option([EmptySubstitution(X), EmptySubstitution(Y)], VarNotEmpty(Z)),
        Option([EmptySubstitution(X), EmptySubstitution(Z)], VarNotEmpty(Y)),
        Option([EmptySubstitution(Y), EmptySubstitution(Z)], VarNotEmpty(X)),
        Option([EmptySubstitution(X), EmptySubstitution(Y), EmptySubstitution(Z)], None),
    ]],

    [[X], Option(restriction=VarNotEmpty(X)), [
        Option(restriction=VarNotEmpty(X)),
    ]],
    [[X, Y], Option(restriction=VarNotEmpty(X)), [
        Option(restriction=RestrictionAND([VarNotEmpty(X), VarNotEmpty(Y)])),
        Option(substitutions=[EmptySubstitution(Y)], restriction=VarNotEmpty(X)),
    ]],
]


@pytest.mark.parametrize('template_elements,parent_option,expected_options', test_data)
def test(template_elements, parent_option: Option | None, expected_options: list[Option]):
    tpl = Template(*template_elements)
    result = get_empty_options(tpl, parent_option)

    if len(result) != len(expected_options):
        assert result == expected_options

    for option in expected_options:
        if option not in result:
            assert result == expected_options
