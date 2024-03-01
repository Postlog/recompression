import itertools

from recompression.models import const as c, equation as eq, option as opt, var as v, var_restriction as vr


def is_popping_essential(template: eq.Template, pair: c.Pair, popping: opt.PopLeft | opt.PopRight):
    new_tpl = template.apply_substitution(popping)
    return new_tpl.get_pair_occourance_count(pair) > template.get_pair_occourance_count(pair)


def get_options_for_pair(
        template: eq.Template,
        pair: c.Pair,
        parent_option: opt.Option,
) -> list[opt.Option]:
    popings_raw = []
    a, b = pair
    for i, var in enumerate(template.elements):
        if not isinstance(var, v.Var):
            continue

        left = template.elements[i - 1] if i != 0 else None
        right = template.elements[i + 1] if i != len(template.elements) - 1 else None

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
                popings_raw.append((opt.PopLeft(var, a), opt.PopRight(var, b)))

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

    if len(popings) == 0:
        return [opt.Option(parent_option.substitutions, parent_option.restriction)]

    options_raw = []

    for poping in popings:
        if len(poping) == 1:
            pop = poping[0]
            options_raw.append([
                opt.Option(
                    [pop],
                    None,
                ),
                opt.Option(
                    [],
                    vr.VarNotStartsWith(pop.var, pop.const) if isinstance(pop, opt.PopLeft) else vr.VarNotEndsWith(
                        pop.var, pop.const,
                    )
                ),
            ])
        elif len(poping) == 2:
            first, second = poping
            first_essential = is_popping_essential(template, pair, first)
            second_essential = is_popping_essential(template, pair, second)
            if first_essential and second_essential:
                options_raw.append([
                    opt.Option(
                        [first, second],
                        None
                    ),
                    opt.Option(
                        [first],
                        vr.VarNotStartsWith(second.var, second.const) if isinstance(second,
                                                                                    opt.PopLeft) else vr.VarNotEndsWith(
                            second.var, second.const)
                    ),
                    opt.Option(
                        [second],
                        vr.VarNotStartsWith(first.var, first.const) if isinstance(first,
                                                                                  opt.PopLeft) else vr.VarNotEndsWith(
                            first.var, first.const)
                    ),
                    opt.Option(
                        [],
                        vr.RestrictionAND([
                            vr.VarNotStartsWith(first.var, first.const) if isinstance(first,
                                                                                      opt.PopLeft) else vr.VarNotEndsWith(
                                first.var, first.const),
                            vr.VarNotStartsWith(second.var, second.const) if isinstance(second,
                                                                                        opt.PopLeft) else vr.VarNotEndsWith(
                                second.var, second.const)
                        ])
                    )
                ])
            elif first_essential or second_essential:
                essential = first if first_essential else second
                not_essential = second if first_essential else first
                options_raw.append([
                    opt.Option(
                        list(poping),
                        None
                    ),
                    opt.Option(
                        [essential],
                        vr.VarNotStartsWith(not_essential.var, not_essential.const) if isinstance(not_essential,
                                                                                                  opt.PopLeft) else vr.VarNotEndsWith(
                            not_essential.var, not_essential.const)
                    ),
                    opt.Option(
                        [],
                        vr.VarNotStartsWith(essential.var, essential.const) if isinstance(essential,
                                                                                          opt.PopLeft) else vr.VarNotEndsWith(
                            essential.var, essential.const)
                    ),
                ])
            else:
                options_raw.append([
                    opt.Option(
                        list(poping),
                        None
                    ),
                    opt.Option(
                        [],
                        opt.RestrictionOR(
                            vr.VarNotStartsWith(first.var, first.const) if isinstance(first,
                                                                                      opt.PopLeft) else vr.VarNotEndsWith(
                                first.var, first.const),
                            vr.VarNotStartsWith(second.var, second.const) if isinstance(second,
                                                                                        opt.PopLeft) else vr.VarNotEndsWith(
                                second.var, second.const)
                        )
                    )
                ])

    if len(options_raw) == 1:
        result = []
        for o in options_raw[0]:
            result.extend(parent_option.combine(o))

        return list(set(result))

    options = []
    for i in range(len(options_raw)):
        for j in range(i + 1, len(options_raw)):
            for opt_pair in itertools.product(options_raw[i], options_raw[j]):
                for o in opt_pair[0].combine(opt_pair[1]):
                    options.extend(parent_option.combine(o))

    return list(set(options))


if __name__ == '__main__':
    eq_raw = 'bXYamXbZY=aa'
    pair_raw = 'ab'

    tpl = eq.Template(*[c.AlphabetConst(sym) if sym.islower() else v.Var(sym) for sym in eq_raw.split('=')[0]])
    spl = eq.Sample(*[c.AlphabetConst(sym) for sym in eq_raw.split('=')[1]])
    pr = (c.AlphabetConst(pair_raw[0]), c.AlphabetConst(pair_raw[1]))

    print(get_options_for_pair(tpl, pr, opt.Option([], None)))
