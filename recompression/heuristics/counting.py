import z3

from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, var as v
from utils.time import timeit


class CountingHeuristics(h.Heurisitcs):
    def __init__(self):
        self.z3 = z3.Solver()

    @timeit("heuristic of counting consts")
    def is_satisfable(self, equation: eq.Equation) -> bool:
        results = []
        consts = equation.sample.get_consts().union(equation.template.get_consts())
        for const in consts:
            self.z3.reset()

            lhs_count = 0
            lhs_vars = []
            lhs_vars_bools = []
            for element in equation.template.elements:
                if element == const:
                    lhs_count += 1
                elif isinstance(element, v.Var):
                    var = z3.Int(str(element))
                    lhs_vars.append(var)
                    lhs_vars_bools.append(var >= 0)

            lhs_z3_obj = z3.IntVal(lhs_count)
            for var in lhs_vars:
                lhs_z3_obj += var

            rhs_count = 0
            for element in equation.sample.elements:
                if element == const:
                    rhs_count += 1

            self.z3.add(*lhs_vars_bools, lhs_z3_obj == z3.IntVal(rhs_count))
            c = self.z3.check()
            results.append(c in (z3.sat, z3.unknown))

        return all(results)
