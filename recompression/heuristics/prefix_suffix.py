from recompression.heuristics import heuristics as h
from recompression.models import equation as eq, option as opt


class PrefixSuffixHeuristics(h.Heurisitcs):
    def get_name(self) -> str:
        return 'prefix-sufix'

    def is_satisfable(self, equation: eq.Equation, option: opt.Option) -> bool:
        tpl_consts = equation.template.get_consts()
        if len(tpl_consts) > len(equation.sample.elements):
            return False

        if len(tpl_consts) == len(equation.sample.elements):
            for i, const in enumerate(tpl_consts):
                if equation.sample.elements[i] != const:
                    return False

            return True

        tpl_pref, tpl_suff = equation.template.get_consts_prefix_suffix()
        for i, const in enumerate(tpl_pref):
            if equation.sample.elements[i] != const:
                return False

        for i, const in enumerate(tpl_suff):
            el = equation.sample.elements[-len(tpl_suff) + i]
            if el != const:
                return False

        return True
