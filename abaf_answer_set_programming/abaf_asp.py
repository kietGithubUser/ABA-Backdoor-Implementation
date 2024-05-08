import clingo
import os
from typing import List
from utilities.utility import collect_solution


# in this class, we do all ASP computations for an ABAF using the solver Clingo
class ABAF_ASP:

    # ctl: empty attribute, which is only defined when using the implemented class functions
    def __init__(self):
        self.ctl = None

    # returns exactly one minimal ACYC_DG backdoor for the given dependency graph
    def get_acyc_backdoor_assumptions(self, dependency_graphs_as_facts: str) -> List[str]:
        self.ctl = clingo.Control()
        with open(os.path.join('abaf_asp_encodings', 'acyc_backdoor_dg.dl'), 'r') as file:
            acyc_backdoor_encoding = file.read()
        self.ctl.add('acyc_backdoor', [], acyc_backdoor_encoding + dependency_graphs_as_facts)
        self.ctl.ground([('acyc_backdoor', [])])
        self.ctl.configuration.solve.models = 0
        solutions_list = []

        self.ctl.solve(on_model=lambda model: collect_solution(model, solutions_list))

        minimal_solution = min(solutions_list, key=lambda sublist: len(sublist))
        return minimal_solution
