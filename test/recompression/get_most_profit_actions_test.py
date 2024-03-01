import pytest

from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.models import const as c, equation as eq, actions as ac

a_a = c.AlphabetConst('a')
a_b = c.AlphabetConst('b')
a_c = c.AlphabetConst('c')

p_a = c.PairConst('a', 1)
p_b = c.PairConst('b', 2)
p_c = c.PairConst('c', 3)

b_a = c.BlockConst('a', 1)
b_b = c.BlockConst('b', 2)
b_c = c.BlockConst('c', 3)

test_data = [
    # единственный символ
    [[a_a], []],
    # один блок
    [[a_a, a_a], [ac.CompressBlockAction(a_a, 2, 0)]],
    # одна пара
    [[a_a, a_b], [ac.CompressPairAction((a_a, a_b))]],
    # две пары
    [[a_a, a_b, c], [ac.CompressPairAction((a_a, a_b)), ac.CompressPairAction((a_b, c))]],
    # пара и блок, оба выгодны
    [[a_a, a_b, a_b], [ac.CompressPairAction((a_a, a_b)), ac.CompressBlockAction(a_b, 2, 1)]],
    # два блока, оба выгодны
    [[a_b, a_b, a_b, a_a, a_a, a_a], [ac.CompressBlockAction(a_b, 3, 0), ac.CompressBlockAction(a_a, 3, 3)]],
    # два блока, один длиннее
    [[a_b, a_b, a_b, a_a, a_a, a_a, a_a], [ac.CompressBlockAction(a_a, 4, 3)]],
    # два блока и две пары, одна пара выгоднее всех
    [[a_a, a_a, a_a, a_b, a_b, a_a, a_b, a_a, a_b], [ac.CompressPairAction((a_a, a_b))]],

    # единственный символ
    [[p_a], []],
    # один блок
    [[p_a, p_a], [ac.CompressBlockAction(p_a, 2, 0)]],
    # одна пара
    [[p_a, a_b], [ac.CompressPairAction((p_a, a_b))]],
    # две пары
    [[p_a, a_b, c], [ac.CompressPairAction((p_a, a_b)), ac.CompressPairAction((a_b, c))]],
    # пара и блок, оба выгодны
    [[p_a, a_b, a_b], [ac.CompressPairAction((p_a, a_b)), ac.CompressBlockAction(a_b, 2, 1)]],
    # два блока, оба выгодны
    [[a_b, a_b, a_b, p_a, p_a, p_a], [ac.CompressBlockAction(a_b, 3, 0), ac.CompressBlockAction(p_a, 3, 3)]],
    # два блока, один длиннее
    [[a_b, a_b, a_b, p_a, p_a, p_a, p_a], [ac.CompressBlockAction(p_a, 4, 3)]],
    # два блока и две пары, одна пара выгоднее всех
    [[p_a, p_a, p_a, a_b, a_b, p_a, a_b, p_a, a_b], [ac.CompressPairAction((p_a, a_b))]],

    # единственный символ
    [[b_a], []],
    # один блок
    [[b_a, b_a], [ac.CompressBlockAction(b_a, 2, 0)]],
    # одна пара
    [[b_a, a_b], [ac.CompressPairAction((b_a, a_b))]],
    # две пары
    [[b_a, a_b, p_a], [ac.CompressPairAction((b_a, a_b)), ac.CompressPairAction((a_b, p_a))]],
    # пара и блок, оба выгодны
    [[b_a, a_b, a_b], [ac.CompressPairAction((b_a, a_b)), ac.CompressBlockAction(a_b, 2, 1)]],
    # два блока, оба выгодны
    [[a_b, a_b, a_b, b_a, b_a, b_a], [ac.CompressBlockAction(a_b, 3, 0), ac.CompressBlockAction(b_a, 3, 3)]],
    # два блока, один длиннее
    [[a_b, a_b, a_b, b_a, b_a, b_a, b_a], [ac.CompressBlockAction(b_a, 4, 3)]],
    # два блока и две пары, одна пара выгоднее всех
    [[b_a, b_a, b_a, a_b, a_b, b_a, a_b, b_a, a_b], [ac.CompressPairAction((b_a, a_b))]],
]


@pytest.mark.parametrize('sample_elements, expected_result', test_data)
def test(sample_elements, expected_result):
    result = get_most_profit_actions(eq.Sample(*sample_elements))

    assert result == expected_result
