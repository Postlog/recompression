import pytest

from recompression.get_most_profit_actions import get_most_profit_actions
from recompression.models import AlphabetConst, Sample, CompressPairAction, PairConst, BlockConst, \
    CompressBlockAction

a = AlphabetConst('a')
b = AlphabetConst('b')
c = AlphabetConst('c')

p_a = PairConst('a', 1)
p_b = PairConst('b', 2)
p_c = PairConst('c', 3)

b_a = BlockConst('a', 1)
b_b = BlockConst('b', 2)
b_c = BlockConst('c', 3)

test_data = [
    # единственный символ
    [[a], []],
    # один блок
    [[a, a], [CompressBlockAction(a, 2, 0)]],
    # одна пара
    [[a, b], [CompressPairAction((a, b))]],
    # две пары
    [[a, b, c], [CompressPairAction((a, b)), CompressPairAction((b, c))]],
    # пара и блок, оба выгодны
    [[a, b, b], [CompressPairAction((a, b)), CompressBlockAction(b, 2, 1)]],
    # два блока, оба выгодны
    [[b, b, b, a, a, a], [CompressBlockAction(b, 3, 0), CompressBlockAction(a, 3, 3)]],
    # два блока, один длиннее
    [[b, b, b, a, a, a, a], [CompressBlockAction(a, 4, 3)]],
    # два блока и две пары, одна пара выгоднее всех
    [[a, a, a, b, b, a, b, a, b], [CompressPairAction((a, b))]],

    # единственный символ
    [[p_a], []],
    # один блок
    [[p_a, p_a], [CompressBlockAction(p_a, 2, 0)]],
    # одна пара
    [[p_a, b], [CompressPairAction((p_a, b))]],
    # две пары
    [[p_a, b, c], [CompressPairAction((p_a, b)), CompressPairAction((b, c))]],
    # пара и блок, оба выгодны
    [[p_a, b, b], [CompressPairAction((p_a, b)), CompressBlockAction(b, 2, 1)]],
    # два блока, оба выгодны
    [[b, b, b, p_a, p_a, p_a], [CompressBlockAction(b, 3, 0), CompressBlockAction(p_a, 3, 3)]],
    # два блока, один длиннее
    [[b, b, b, p_a, p_a, p_a, p_a], [CompressBlockAction(p_a, 4, 3)]],
    # два блока и две пары, одна пара выгоднее всех
    [[p_a, p_a, p_a, b, b, p_a, b, p_a, b], [CompressPairAction((p_a, b))]],

    # единственный символ
    [[b_a], []],
    # один блок
    [[b_a, b_a], [CompressBlockAction(b_a, 2, 0)]],
    # одна пара
    [[b_a, b], [CompressPairAction((b_a, b))]],
    # две пары
    [[b_a, b, p_a], [CompressPairAction((b_a, b)), CompressPairAction((b, p_a))]],
    # пара и блок, оба выгодны
    [[b_a, b, b], [CompressPairAction((b_a, b)), CompressBlockAction(b, 2, 1)]],
    # два блока, оба выгодны
    [[b, b, b, b_a, b_a, b_a], [CompressBlockAction(b, 3, 0), CompressBlockAction(b_a, 3, 3)]],
    # два блока, один длиннее
    [[b, b, b, b_a, b_a, b_a, b_a], [CompressBlockAction(b_a, 4, 3)]],
    # два блока и две пары, одна пара выгоднее всех
    [[b_a, b_a, b_a, b, b, b_a, b, b_a, b], [CompressPairAction((b_a, b))]],
]


@pytest.mark.parametrize('sample_elements, expected_result', test_data)
def test(sample_elements, expected_result):
    result = get_most_profit_actions(Sample(*sample_elements))

    assert result == expected_result
