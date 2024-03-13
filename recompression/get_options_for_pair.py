from recompression.models import const as c, equation as eq, option as opt, var as v, var_restriction as vr

from pprint import pprint

from utils.list import combinations


def is_poping_essential(template: eq.Template, pair: c.Pair, poping: opt.PopLeft | opt.PopRight):
    new_tpl = template.apply_substitution(poping)
    return new_tpl.get_pair_occourance_count(pair) > template.get_pair_occourance_count(pair)


Popings = list[tuple[opt.PopLeft | opt.PopRight] | tuple[opt.PopLeft | opt.PopRight, opt.PopLeft | opt.PopRight]]


def get_options_for_pair(
        equation: eq.Equation,
        pair: c.Pair,
        parent_option: opt.Option,
) -> list[opt.Option]:
    popings_raw = []
    a, b = pair
    for i, var in enumerate(equation.template.elements):
        if not isinstance(var, v.Var):
            continue

        left = equation.template.elements[i - 1] if i != 0 else None
        right = equation.template.elements[i + 1] if i != len(equation.template.elements) - 1 else None

        if left == a:
            popings_raw.append((opt.PopLeft(var, b),))

        if right == b:
            popings_raw.append((opt.PopRight(var, a),))

        if isinstance(left, v.Var):
            if left != var:
                popings_raw.append((opt.PopLeft(var, b), opt.PopRight(left, a)))
            else:
                popings_raw.append((opt.PopLeft(var, b), opt.PopRight(var, a)))
        if isinstance(right, v.Var):
            if right != var:
                popings_raw.append((opt.PopRight(var, a), opt.PopLeft(right, b)))
            else:
                popings_raw.append((opt.PopLeft(var, b), opt.PopRight(var, a)))

    popings = _dedup_popings(popings_raw)

    if len(popings) == 0:
        return [parent_option]

    options_raw = []

    for poping in popings:
        if len(poping) == 1:
            pop = poping[0]
            options_raw.append([
                opt.Option([pop], None),
                opt.Option([], _reverse_substitution(pop)),
            ])
            continue

        first, second = poping
        first_essential = is_poping_essential(equation.template, pair, first)
        second_essential = is_poping_essential(equation.template, pair, second)
        if first_essential and second_essential:
            options_raw.append([
                opt.Option([first, second], None),
                opt.Option([first], _reverse_substitution(second)),
                opt.Option([second], _reverse_substitution(first)),
                opt.Option([], vr.RestrictionAND([_reverse_substitution(first), _reverse_substitution(second)]))
            ])
        elif first_essential or second_essential:
            essential = first if first_essential else second
            not_essential = second if first_essential else first
            options_raw.append([
                opt.Option(list(poping), None),
                opt.Option([essential], _reverse_substitution(not_essential)),
                opt.Option([], _reverse_substitution(essential)),
            ])
        else:
            options_raw.append([
                opt.Option(list(poping), None),
                opt.Option([], opt.RestrictionOR(_reverse_substitution(first), _reverse_substitution(second)))
            ])

    if len(options_raw) == 1:
        result = []
        for o in options_raw[0]:
            result.extend(parent_option.combine(o))

        return list(set(result))

    options = []
    for comb in combinations(options_raw, len(popings)):
        acc = [opt.Option([], None)]
        for o in comb:
            local_acc = []
            for acc_el in acc:
                local_acc.extend(acc_el.combine(o))
            acc = local_acc
        options.extend(acc)

    result = []
    for o in options:
        result.extend(parent_option.combine(o))

    return list(set(result))


def _dedup_popings(popings_raw: Popings) -> Popings:
    popings = set()
    for poping in popings_raw:
        if len(poping) == 1:
            popings.add(poping)
            continue

        if (poping[1], poping[0]) not in popings:
            popings.add(poping)

    popings_cpy = popings.copy()
    for poping1 in popings_cpy:
        if len(poping1) != 1:
            continue

        pop = poping1[0]

        for poping2 in popings_cpy:
            if len(poping2) != 2:
                continue

            if pop in poping2:
                popings.remove(poping1)
                break

    return list(popings)


def _reverse_substitution(subst: opt.PopLeft | opt.PopRight) -> opt.Restriction:
    if isinstance(subst, opt.PopLeft):
        return vr.VarNotStartsWith(subst.var, subst.const)

    return vr.VarNotEndsWith(subst.var, subst.const)


if __name__ == '__main__':
    eq_raw = 'bXYamXbZY=aa'
    pair_raw = 'ab'

    tpl = eq.Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in eq_raw.split('=')[0]])
    spl = eq.Sample(*[c.AlphabetConst(sym) for sym in eq_raw.split('=')[1]])
    pr = (c.AlphabetConst(pair_raw[0]), c.AlphabetConst(pair_raw[1]))

    # print(get_options_for_pair(tpl, pr, opt.Option([], None), 0))

    pprint(combinations([
        ['1-1', '1-2'],
        ['2-1', '2-2'],
        ['3-1', '3-2'],
    ], 3))
