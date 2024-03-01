def indexes(lst: list, el: any) -> list[int]:
    return [i for i, val in enumerate(lst) if val == el]
