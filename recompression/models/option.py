import itertools
from dataclasses import dataclass
from typing import Optional

from recompression.models import equation as eq
from recompression.models.const import AlphabetConst
from recompression.models.substitution import Substitution, PopLeft, PopRight
from recompression.models.var import Var
from recompression.models.var_restriction import RestrictionAND, Restriction, RestrictionOR, VarNotStartsWith, \
    VarNotEndsWith, VarNotEmpty


@dataclass
class Option:
    substitutions: list[Substitution]
    restriction: RestrictionAND | RestrictionOR | Restriction | None

    @property
    def is_empty(self):
        return len(self.substitutions) == 0 and self.restriction is None

    def __post_init__(self):
        if self.substitutions is None:
            self.substitutions = []

        self.substitutions = list(set(self.substitutions))

    def __hash__(self):
        return sum([hash(subst) for subst in self.substitutions]) + hash(self.restriction)

    def __str__(self):
        restrs_str = ''
        if self.restriction is not None:
            restrs_str = str(self.restriction)
            if len(self.substitutions) != 0:
                if isinstance(self.restriction, RestrictionOR):
                    restrs_str = f'({restrs_str})'

                restrs_str = ' & ' + restrs_str

        return ' & '.join([str(subst) for subst in self.substitutions]) + restrs_str

    __repr__ = __str__

    def apply_to(self, equat: eq.Equation) -> eq.Equation:
        template = equat.template
        for subst in self.substitutions:
            template = template.apply_substitution(subst)

        return eq.Equation(template, equat.sample)

    def combine(self, other: 'Option') -> list['Option']:
        substs = list(set(self.substitutions + other.substitutions))

        if self.restriction is None:
            opt = Option(substs, other.restriction).normalize()
            return [opt] if opt is not None else []

        if other.restriction is None:
            opt = Option(substs, self.restriction).normalize()
            return [opt] if opt is not None else []

        result = None
        if isinstance(self.restriction, Restriction):
            if isinstance(other.restriction, Restriction):
                if self.restriction == other.restriction:
                    result = [Option(substs, self.restriction)]
                else:
                    result = [Option(substs, RestrictionAND([self.restriction, other.restriction], None))]
            elif isinstance(other.restriction, RestrictionAND):
                result = [Option(substs, RestrictionAND(
                    [self.restriction, *other.restriction.simple_restrictions],
                    other.restriction.restriction_or,
                ))]
            elif isinstance(other.restriction, RestrictionOR):
                result = [Option(substs, RestrictionAND([self.restriction], other.restriction))]
        elif isinstance(self.restriction, RestrictionAND):
            if isinstance(other.restriction, Restriction):
                result = [Option(substs, RestrictionAND(
                    [other.restriction, *self.restriction.simple_restrictions],
                    self.restriction.restriction_or,
                ))]
            elif isinstance(other.restriction, RestrictionAND):
                if self.restriction.restriction_or is not None and other.restriction.restriction_or is not None:
                    result = [
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + other.restriction.simple_restrictions + [
                                self.restriction.restriction_or.left,
                                other.restriction.restriction_or.left
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + other.restriction.simple_restrictions + [
                                self.restriction.restriction_or.left,
                                other.restriction.restriction_or.right
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + other.restriction.simple_restrictions + [
                                self.restriction.restriction_or.right,
                                other.restriction.restriction_or.left
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + other.restriction.simple_restrictions + [
                                self.restriction.restriction_or.right,
                                other.restriction.restriction_or.right
                            ],
                            None,
                        )),
                    ]
                else:
                    restriction_or = self.restriction.restriction_or if self.restriction.restriction_or is not None else other.restriction.restriction_or

                    result = [
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + other.restriction.simple_restrictions,
                            restriction_or,
                        )),
                    ]
            elif isinstance(other.restriction, RestrictionOR):
                if self.restriction.restriction_or is not None:
                    result = [
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + [
                                self.restriction.restriction_or.left, other.restriction.left
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + [
                                self.restriction.restriction_or.left, other.restriction.right
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + [
                                self.restriction.restriction_or.right, other.restriction.left
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            self.restriction.simple_restrictions + [
                                self.restriction.restriction_or.right, other.restriction.right
                            ],
                            None,
                        )),
                    ]
                else:
                    result = [Option(substs, RestrictionAND(self.restriction.simple_restrictions, other.restriction))]
        elif isinstance(self.restriction, RestrictionOR):
            if isinstance(other.restriction, Restriction):
                result = [Option(substs, RestrictionAND([other.restriction], self.restriction))]
            elif isinstance(other.restriction, RestrictionAND):
                if other.restriction.restriction_or is not None:
                    result = [
                        Option(substs, RestrictionAND(
                            other.restriction.simple_restrictions + [
                                other.restriction.restriction_or.left, self.restriction.left
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            other.restriction.simple_restrictions + [
                                other.restriction.restriction_or.left, self.restriction.right
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            other.restriction.simple_restrictions + [
                                other.restriction.restriction_or.right, self.restriction.left
                            ],
                            None,
                        )),
                        Option(substs, RestrictionAND(
                            other.restriction.simple_restrictions + [
                                other.restriction.restriction_or.right, self.restriction.right
                            ],
                            None,
                        )),
                    ]
                else:
                    result = [Option(substs, RestrictionAND(other.restriction.simple_restrictions, self.restriction))]
            elif isinstance(other.restriction, RestrictionOR):
                self_l, self_r = self.restriction.left, self.restriction.right
                oth_l, oth_r = other.restriction.left, other.restriction.right
                result = [
                    Option(substs, RestrictionAND(
                        [self_l, oth_l],
                        None,
                    ) if self_l != oth_l else self_l),
                    Option(substs, RestrictionAND(
                        [self_l, oth_r],
                        None,
                    ) if self_l != oth_r else self_l),
                    Option(substs, RestrictionAND(
                        [self_r, oth_l],
                        None,
                    ) if self_r != oth_l else self_r),
                    Option(substs, RestrictionAND(
                        [self_r, oth_r],
                        None,
                    ) if self_r != oth_r else self_r),
                ]

        return list(filter(lambda x: x is not None, [option.normalize() for option in result]))

    def optimize(self, equation: eq.Equation) -> 'Option':
        eq_consts = equation.template.get_consts_set().union(equation.sample.get_consts_set())

        if isinstance(self.restriction, (VarNotEndsWith, VarNotStartsWith)) and self.restriction.const not in eq_consts:
            return Option(self.substitutions, None)
        if isinstance(self.restriction, RestrictionAND):
            filtered_simple_restrictions = []
            for restr in self.restriction.simple_restrictions:
                if isinstance(restr, (VarNotEndsWith, VarNotStartsWith)) and restr.const not in eq_consts:
                    continue
                filtered_simple_restrictions.append(restr)

            if self.restriction.restriction_or is None:
                if len(filtered_simple_restrictions) == 0:
                    return Option(self.substitutions, None)
                elif len(filtered_simple_restrictions) == 1:
                    return Option(self.substitutions, filtered_simple_restrictions[0])
                else:
                    return Option(self.substitutions, RestrictionAND(filtered_simple_restrictions, None))

            trivially_true = False
            if isinstance(self.restriction.restriction_or.left, (VarNotEndsWith, VarNotStartsWith)) and self.restriction.restriction_or.left.const not in eq_consts:
                trivially_true = True
            elif isinstance(self.restriction.restriction_or.left, (VarNotEndsWith, VarNotStartsWith)) and self.restriction.restriction_or.right.const not in eq_consts:
                trivially_true = True

            if trivially_true:
                if len(filtered_simple_restrictions) == 0:
                    return Option(self.substitutions, None)
                elif len(filtered_simple_restrictions) == 1:
                    return Option(self.substitutions, filtered_simple_restrictions[0])
                else:
                    return Option(self.substitutions, RestrictionAND(filtered_simple_restrictions, None))

            if len(filtered_simple_restrictions) == 0:
                return Option(self.substitutions, self.restriction.restriction_or)

            return Option(self.substitutions, RestrictionAND(filtered_simple_restrictions, self.restriction.restriction_or))

        if isinstance(self.restriction, RestrictionOR):
            trivially_true = False
            if isinstance(self.restriction.left, (VarNotEndsWith, VarNotStartsWith)) and self.restriction.left.const not in eq_consts:
                trivially_true = True
            if isinstance(self.restriction.left, (VarNotEndsWith, VarNotStartsWith)) and self.restriction.right.const not in eq_consts:
                trivially_true = True

            if trivially_true:
                return Option(self.substitutions, None)

            return Option(self.substitutions, self.restriction)

        return Option(self.substitutions, self.restriction)


    def normalize(self) -> Optional['Option']:
        substs = list(set(self.substitutions))
        restr = self.restriction

        restr = self._remove_redutant_not_eps_restriction(substs, restr)

        if restr is None:
            return Option(substs, None)

        if isinstance(restr, RestrictionAND):
            restr = restr.simplify()

        for subst in self.substitutions:
            if not restr.is_substitution_satisfies(subst):
                return None

            if isinstance(restr, RestrictionAND):
                for simple_restr in restr.simple_restrictions:
                    if not simple_restr.is_substitution_satisfies(subst):
                        return None

                if restr.restriction_or is not None:
                    is_left_contradiction = not restr.restriction_or.left.is_substitution_satisfies(subst)
                    is_right_contradiction = not restr.restriction_or.right.is_substitution_satisfies(subst)

                    if is_left_contradiction and is_right_contradiction:
                        return None

                    if is_left_contradiction:
                        restr = RestrictionAND(
                            [restr.restriction_or.right, *restr.simple_restrictions],
                            None,
                        ).simplify()

                    if is_right_contradiction:
                        restr = RestrictionAND([restr.restriction_or.left, *restr.simple_restrictions], None).simplify()
            elif isinstance(restr, RestrictionOR):
                is_left_contradiction = not restr.left.is_substitution_satisfies(subst)
                is_right_contradiction = not restr.right.is_substitution_satisfies(subst)

                if is_left_contradiction and is_right_contradiction:
                    return None

                if is_left_contradiction:
                    restr = restr.right

                if is_right_contradiction:
                    restr = restr.left

        return Option(substs, restr)

    @staticmethod
    def _remove_redutant_not_eps_restriction(
            substs: list[Substitution],
            restr: RestrictionAND | RestrictionOR | Restriction,
    ) -> RestrictionAND | RestrictionOR | Restriction | None:
        not_eps_substs = {}
        for subst in substs:
            if isinstance(subst, PopLeft) or isinstance(subst, PopRight):
                not_eps_substs[subst.var] = subst

        if isinstance(restr, VarNotEmpty) and restr.var in not_eps_substs:
            return None
        elif isinstance(restr, RestrictionOR):
            is_right_redutant = False
            if isinstance(restr.right, VarNotEmpty) and restr.right.var in not_eps_substs:
                is_right_redutant = True

            is_left_redutant = False
            if isinstance(restr.left, VarNotEmpty) and restr.left.var in not_eps_substs:
                is_right_redutant = True

            if is_left_redutant and is_right_redutant:
                return None

            if is_left_redutant or is_left_redutant:
                return restr.right if is_left_redutant else restr.left
        elif isinstance(restr, RestrictionAND):
            new_simple_restrs = []
            for simple_restr in restr.simple_restrictions:
                if isinstance(simple_restr, VarNotEmpty) and simple_restr.var in not_eps_substs:
                    continue
                new_simple_restrs.append(simple_restr)

            new_restr_or = None
            if restr.restriction_or is not None:
                new_restr_or = Option._remove_redutant_not_eps_restriction(substs, restr.restriction_or)

            if isinstance(new_restr_or, RestrictionOR):
                if len(new_simple_restrs) == 0:
                    return new_restr_or

                return RestrictionAND(new_simple_restrs, new_restr_or)

            if new_restr_or is None:
                if len(new_simple_restrs) <= 1:
                    return None if len(new_simple_restrs) == 0 else new_simple_restrs[0]

                return RestrictionAND(new_simple_restrs, None)
            else:
                return RestrictionAND([*new_simple_restrs, new_restr_or], None)

        return restr


def display():
    x = Var('X')
    y = Var('Y')
    z = Var('Z')

    a = AlphabetConst('a')
    b = AlphabetConst('b')

    options_1 = [
        Option([PopRight(x, a), PopLeft(y, b)]),
        Option([PopRight(x, a)], VarNotStartsWith(y, b)),
        Option([], VarNotEndsWith(x, a)),
        Option([], RestrictionOR(VarNotEndsWith(x, a), VarNotEndsWith(y, b))),
    ]

    options_2 = [
        Option([PopRight(z, a), PopLeft(y, b)], None),
        Option([], RestrictionOR(VarNotEndsWith(z, a), VarNotStartsWith(y, b))),
    ]

    for (o1, o2) in itertools.product(options_1, options_2):
        print(f'[{o1}] * [{o2}] = {o1.combine(o2)}')


if __name__ == '__main__':
    display()
