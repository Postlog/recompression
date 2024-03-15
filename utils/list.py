import itertools


def indexes(lst: list, el: any) -> list[int]:
    return [i for i, val in enumerate(lst) if val == el]


def flatten(xss):
    return [x for xs in xss for x in xs]


def combinations(l, n):
    result = []
    for i in range(len(l)):
        ptr = l[i]
        other_prod = list(itertools.combinations(flatten(l[i+1:i + n + 1]), r=n-1))
        for el in ptr:
            result.extend([(el,) + p for p in other_prod])

    return result