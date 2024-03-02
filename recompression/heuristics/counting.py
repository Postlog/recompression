import z3

from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, var as v, option as opt
from utils.time import timeit


class CountingHeuristics(h.Heurisitcs):
    def __init__(self):
        self._z3 = z3.Solver()

    @timeit("heuristic of counting consts")
    def is_satisfable(self, equation: eq.Equation, option: opt.Option) -> bool:
        tpl_consts = equation.template.get_consts()
        lhs_vars = []
        lhs_vars_bools = []
        not_empty_count = 0
        for element in equation.template.elements:
            if not isinstance(element, v.Var):
                continue
            var = z3.Int(str(element))
            lhs_vars.append(var)
            lhs_vars_bools.append(var >= 0)
            if option.restriction is not None and not option.restriction.is_substitution_satisfies(opt.EmptySubstitution(element)):
                not_empty_count += 1

        consts = equation.sample.get_consts().union(tpl_consts)
        for const in consts:
            self._z3.reset()

            spl_count = 0
            for element in equation.sample.elements:
                if element == const:
                    spl_count += 1

            tpl_count = 0

            for element in equation.template.elements:
                if element == const:
                    tpl_count += 1

            lhs_z3_obj = z3.IntVal(tpl_count)
            for var in lhs_vars:
                lhs_z3_obj += var

            self._z3.add(*lhs_vars_bools, lhs_z3_obj == z3.IntVal(spl_count))
            check_result = self._z3.check()
            if check_result not in (z3.sat, z3.unknown):
                return False

        return True
