from recompression.models import actions as ac, equation as eq


def get_most_profit_actions(sample: eq.Sample) -> list[ac.CompressBlockAction | ac.CompressPairAction]:
    pairs = sample.get_pairs()
    blocks = sample.get_blocks()

    if len(blocks) == 0 and len(pairs) == 0:
        return []

    # Сжатие 1 блока длины 5 экономит 1*5 - 1 = 4 символа
    # Сжатие 2 блоков длины 5 экономит 2*5 - 2 = 8 символов
    blocks_profit = []  # [(profit, (SampleBlock, [index, index, ...]))]
    for block, indexes in blocks:
        blocks_profit.append((block.count * block.len - block.count, (block, indexes)))

    blocks_profit = sorted(blocks_profit, key=lambda item: item[0], reverse=True)

    # Сжатие 1 пары экономит 1 символ, двух пар 2 символа, трех пар 3 симовла, ...
    pairs_profit = sorted(pairs.items(), key=lambda item: item[1], reverse=True)

    if len(blocks_profit) == 0:
        return [ac.CompressPairAction(profit[0]) for profit in pairs_profit if profit[1] == pairs_profit[0][1]]

    if len(pairs_profit) == 0:
        return build_compress_block_actions(blocks_profit, blocks_profit[0][0])

    best_profit = max(pairs_profit[0][1], blocks_profit[0][0])

    return [ac.CompressPairAction(profit[0]) for profit in pairs_profit if profit[1] == best_profit] + \
        build_compress_block_actions(blocks_profit, best_profit)


def build_compress_block_actions(
        profits: list[tuple[int, tuple[eq.SampleBlock, list[int]]]],
        target_profit: int,
) -> list[ac.CompressBlockAction]:
    result = []
    for profit in profits:
        if profit[0] != target_profit:
            continue

        block, indexes = profit[1]
        result.append(ac.CompressBlockAction(block.const, block.len, indexes))
    return result

