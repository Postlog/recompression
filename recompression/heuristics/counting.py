import z3

from recompression.models import equation as eq, var as v, option as opt

solver = z3.Solver()



def is_satisfable(equat: eq.Equation, parent_option: opt.Option):
    consts = equat.template.get_consts()

    results = []
    for const in consts:
        solver.reset()

        lhs_count = 0
        lhs_vars = []
        lhs_vars_bools = []
        for element in equat.template.elements:
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
        for element in equat.sample.elements:
            if element == const:
                rhs_count += 1

        solver.add(*lhs_vars_bools, lhs_z3_obj == z3.IntVal(rhs_count))
        c = solver.check()
        results.append(c in (z3.sat, z3.unknown))

    return all(results)
