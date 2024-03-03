import itertools

from recompression.models import equation as eq, option as opt


def get_full_empty_option(template: eq.Template, parent_option: opt.Option) -> opt.Option | None:
    substs = []
    for var in template.get_vars_set():
        subst = opt.EmptySubstitution(var)
        if parent_option.restriction is not None and not parent_option.restriction.is_substitution_satisfies(subst):
            return None
        substs.append(subst)

    return opt.Option(substs, parent_option.restriction)


def get_empty_options(template: eq.Template, parent_option: opt.Option | None = None) -> list[opt.Option]:
    """
    Генерирует список опций с комбинацияеми пустых подстановок в переменные шаблона. Учитывает рестрикции,
    хранящиеся в parent_option.

    :param template: - шаблон, для которого нужно собрать комбинации путсых подстановок переменных
    :param parent_option: - опция, в результате применения которой был порожден шаблон
    :return: - список опций с пустыми подстановками
    """

    if parent_option is None:
        parent_option = opt.Option([], None)

    template_vars = template.get_vars_set()

    if len(template_vars) == 0:
        return []

    options = []
    for elements_count in range(0, len(template_vars) + 1):
        for empty_vars in itertools.combinations(template_vars, r=elements_count):
            not_empty_vars = template_vars.difference(empty_vars)
            substs = []
            restrs = []

            must_skip_comb = False
            for var in empty_vars:
                subst = opt.EmptySubstitution(var)
                if parent_option.restriction is None:
                    substs.append(subst)
                elif parent_option.restriction.is_substitution_satisfies(subst):
                    substs.append(subst)
                else:
                    must_skip_comb = True

            if must_skip_comb:
                continue

            for var in not_empty_vars:
                restrs.append(opt.VarNotEmpty(var))

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
