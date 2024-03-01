import itertools

from recompression.models.equation import Template
from recompression.models.option import Option
from recompression.models.substitution import EmptySubstitution
from recompression.models.var_restriction import VarNotEmpty, RestrictionAND


def get_full_empty_option(template: Template, parent_option: Option) -> Option | None:
    substs = []
    for var in template.get_vars():
        subst = EmptySubstitution(var)
        if parent_option.restriction is not None and not parent_option.restriction.is_substitution_satisfies(subst):
            return None
        substs.append(subst)

    return Option(substs, parent_option.restriction)


def get_empty_options(template: Template, parent_option: Option | None = None) -> list[Option]:
    """
    Генерирует список опций с комбинацияеми пустых подстановок в переменные шаблона. Учитывает рестрикции,
    хранящиеся в parent_option.

    :param template: - шаблон, для которого нужно собрать комбинации путсых подстановок переменных
    :param parent_option: - опция, в результате применения которой был порожден шаблон
    :return: - список опций с пустыми подстановками
    """
    template_vars = template.get_vars()

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
                subst = EmptySubstitution(var)
                if parent_option is None or parent_option.restriction is None:
                    substs.append(subst)
                elif parent_option.restriction.is_substitution_satisfies(subst):
                    substs.append(subst)
                else:
                    must_skip_comb = True

            if must_skip_comb:
                continue

            for var in not_empty_vars:
                restrs.append(VarNotEmpty(var))

            restriction = None
            if len(restrs) == 1:
                restriction = restrs[0]
            elif len(restrs) > 1:
                restriction = RestrictionAND(restrs, None)

            option = Option(substs, restriction)
            if parent_option is not None:
                options.extend(parent_option.combine(option))
            else:
                options.append(option)

    return list(set(options))
