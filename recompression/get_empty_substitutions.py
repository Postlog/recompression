import itertools

from recompression.models import equation as eq, option as opt, const as c, substitution as sb


def get_empty_options(pair: c.Pair, template: eq.Template, parent_option: opt.Option | None = None):
    if parent_option is None:
        parent_option = opt.Option([], None)

    var_groups = template.get_var_groups()

    a, b = pair

    maybe_empty_vars = set()
    for (g_type, start, g_len) in var_groups:
        subgroup = template.elements[start:start+g_len]
        left = template.elements[start - 1] if start - 1 >= 0 else None
        right = template.elements[start+g_len] if start + g_len < len(template.elements) else None

        if g_type == eq.VarGroupType.GENERIC and left == a and right == b:
            maybe_empty_vars.update(subgroup)
        elif g_type == eq.VarGroupType.LEFT and right == b:
            maybe_empty_vars.update(subgroup[1:])
        elif g_type == eq.VarGroupType.RIGHT and left == a:
            maybe_empty_vars.update(subgroup[:-1])
        elif g_type == eq.VarGroupType.LEFT_RIGHT:
            maybe_empty_vars.update(subgroup[1:-1])

    empty_vars = set()
    for var in maybe_empty_vars:
        subst = sb.EmptySubstitution(var)
        if parent_option.restriction is None or parent_option.restriction.is_substitution_satisfies(subst):
            empty_vars.add(var)

    options = []
    for elements_count in range(0, len(empty_vars) + 1):
        for empty_vars_combination in itertools.combinations(empty_vars, r=elements_count):
            not_empty_vars = empty_vars.difference(empty_vars_combination)

            substs = [sb.EmptySubstitution(var) for var in empty_vars_combination]
            restrs = [opt.VarNotEmpty(var) for var in not_empty_vars]

            restriction = None
            if len(restrs) == 1:
                restriction = restrs[0]
            elif len(restrs) > 1:
                restriction = opt.RestrictionAND(restrs, None)

            option = opt.Option(substs, restriction)
            options.extend([
                opt.Option(option.substitutions, comb.restriction) for comb in parent_option.combine(option)
            ])

    return list(set(options))


def get_full_empty_option(template: eq.Template, parent_option: opt.Option) -> opt.Option | None:
    substs = []
    for var in template.get_vars_set():
        subst = sb.EmptySubstitution(var)
        if parent_option.restriction is not None and not parent_option.restriction.is_substitution_satisfies(subst):
            return None
        substs.append(subst)

    return opt.Option(substs, parent_option.restriction)
