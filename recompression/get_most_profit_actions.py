from recompression.models import actions as ac, equation as eq


def get_most_profit_actions(sample: eq.Sample) -> list[ac.CompressBlockAction | ac.CompressPairAction]:
    pairs = sample.get_pairs()
    blocks = sample.get_blocks()

    # Сжатие 1 блока длины 5 экономит 1*5 - 1 = 4 символа
    # Сжатие 2 блоков длины 5 экономит 2*5 - 2 = 8 символов
    blocks_profit = []  # [(profit, (SampleBlock, [index, index, ...]))]
    for block, indexes in blocks:
        blocks_profit.append((block.count * block.len - block.count, (block, indexes)))

    blocks_profit = sorted(blocks_profit, key=lambda item: item[0], reverse=True)

    # Сжатие 1 пары экономит 1 символ, двух пар 2 символа, трех пар 3 симовла, ...
    pairs_profit = sorted(pairs.items(), key=lambda item: item[1], reverse=True)

    if len(blocks_profit) == 0 and len(pairs_profit) == 0:
        return []

    if len(blocks_profit) == 0:
        return [ac.CompressPairAction(pairs_profit[0][0])]

    if len(pairs_profit) == 0:
        return [build_compress_block_action(blocks_profit)]

    return [ac.CompressPairAction(pairs_profit[0][0]), build_compress_block_action(blocks_profit)]


def build_compress_block_action(profits: list[tuple[int, tuple[eq.SampleBlock, list[int]]]]) -> ac.CompressBlockAction:
    block, indexes = profits[0][1]
    return ac.CompressBlockAction(block.const, block.len, indexes)
