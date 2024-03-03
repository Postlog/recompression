import z3

from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, var as v, option as opt
from utils.time import timeit


class CountingHeuristics(h.Heurisitcs):
    def __init__(self):
        self._z3 = z3.Solver()

    def get_name(self) -> str:
        return 'counting'

    @timeit("heuristic of counting consts")
    def is_satisfable(self, equation: eq.Equation, option: opt.Option) -> bool:
        self._z3.reset()

        tpl_consts = equation.template.get_consts_set()

        consts = equation.sample.get_consts_set().union(tpl_consts)
        model = []
        local_var_restrictions: dict[(v.Var, bool), any] = {}
        variables = set()
        for const in consts:
            spl_count = 0
            for element in equation.sample.elements:
                if element == const:
                    spl_count += 1

            tpl_count = 0
            for element in equation.template.elements:
                if element == const:
                    tpl_count += 1

            local_model = z3.IntVal(tpl_count)
            for element in equation.template.elements:
                if not isinstance(element, v.Var):
                    continue

                var_name = str(element) + str(const)
                var = z3.Int(var_name)
                variables.add(var)
                local_model += var
                can_be_empty = True
                if option.restriction is not None and not option.restriction.is_substitution_satisfies(
                        opt.EmptySubstitution(element),
                ):
                    can_be_empty = False

                if (element, can_be_empty) not in local_var_restrictions:
                    local_var_restrictions[(element, can_be_empty)] = var
                else:
                    local_var_restrictions[(element, can_be_empty)] += var
            model.append(local_model == z3.IntVal(spl_count))

        model_restrictions = []
        for k, val in local_var_restrictions.items():
            if k[1]:
                model_restrictions.append(val >= 0)
            else:
                model_restrictions.append(val > 0)

        for var in variables:
            model_restrictions.append(var >= 0)

        self._z3.add(*model_restrictions, *model)
        check_result = self._z3.check()

        return check_result in (z3.sat, z3.unknown)
