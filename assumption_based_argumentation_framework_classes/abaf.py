from assumption_based_argumentation_framework_classes.atom import Atom
from assumption_based_argumentation_framework_classes.rule import Rule
from abaf_answer_set_programming.abaf_asp import ABAF_ASP
from label_package.labeling import Label
from utilities.utility import get_power_set, get_maximal_subsets
from typing import Dict, Set, Tuple, FrozenSet, Optional, List
from pysat.formula import CNF
from pysat.solvers import Glucose42


# in this class, we implement an ABAF and have all computations of it
class ABAF:

    # language: atom set of the ABAF
    # assumptions: assumption set of the ABAF
    # rules: set of rules of the ABAF
    # contraries: contrary partial function of the ABAF
    def __init__(self, language: Set[Atom], rules: Set[Rule], assumptions: Set[Atom],
                 contraries: Dict[Atom, Optional[Atom]]):
        self.language = language
        self.rules = rules
        self.assumptions = assumptions
        self.contraries = contraries
        self.well_defined()
        self.is_flat()
        self.l_num_dict = self.l_num()
        self.rules_sat = self.prepare_rules_sat()
        self.solver = self.prepare_solver()

    # solver is prepared with the rules in CNF
    # the output will be saved in a class variable
    def prepare_solver(self):
        cnf = CNF(from_clauses=self.rules_sat[0])
        return Glucose42(bootstrap_with=cnf)

    # we map the number of an atom to its actual Atom object
    # the output will be saved in a class variable
    def l_num(self) -> Dict[int, Atom]:
        l_dict = {}
        for atom in self.language:
            l_dict[int(atom.name[1:])] = atom
        return l_dict

    # this function checks if the ABAF object is defined correctly
    def well_defined(self) -> None:
        if not self.assumptions.issubset(self.language):
            raise ValueError("Assumption set is not a subset of the language set.")
        for rule in self.rules:
            if not rule.body.union({rule.head}).issubset(self.language):
                raise ValueError("At least one atom used in the rules is not in the language set.")
        for assumption in self.assumptions:
            if not self.contraries[assumption] is None and not self.contraries[assumption] in self.language:
                raise ValueError("At least one assumption is not mapped correctly in the contrary function.")
        if not self.assumptions == self.contraries.keys():
            raise ValueError("Contraries set must be equal to the assumption set.")

    # check if the ABAF is flat
    def is_flat(self) -> None:
        for rule in self.rules:
            if rule.head in self.assumptions:
                raise ValueError("The ABAF is not flat.")

    # we define rules which are going to be used in the solver
    # facts are going to be stored separately
    # the output will be saved in a class variable
    def prepare_rules_sat(self) -> Tuple[List[List[int]], List[int]]:
        fm = []
        sol = []
        for rule in self.rules:
            if len(rule.body) != 0:
                fm.append([int(rule.head.name[1:])] + ([(-1) * int(atom.name[1:]) for atom in rule.body]))
            else:
                sol.append(int(rule.head.name[1:]))
        return fm, sol

    # computes Th(A) for some assumption set A using a SAT Solver with unit propagation
    def get_th_sat(self, assumption_set: Set[Atom]) -> Set[Atom]:
        marked_input = []

        marked_input.extend([int(assumption.name[1:]) for assumption in assumption_set])

        marked_input.extend(self.rules_sat[1])

        th_int = self.solver.propagate(assumptions=marked_input)[1]

        return {self.l_num_dict[number] for number in th_int}

    # returns a set of assumptions attacked by some assumption set
    def get_attacked_assumptions(self, assumption_set: Set[Atom]) -> Set[Atom]:
        attacked_assumptions = set()
        claims = self.get_th_sat(assumption_set)
        for assumption in self.assumptions:
            if self.contraries[assumption] in claims:
                attacked_assumptions.add(assumption)
        return attacked_assumptions

    # returns the grounded assumption set of the ABAF
    # algorithm from corollary 6 of the paper "Declarative Algorithms and Complexity Results for
    # Assumption-Based Argumentation" from Tuomo Lehtonen, Johannes P. Wallner and Matti Jaervisalo
    def get_grounded_assumption_set(self) -> Set[Atom]:
        in_set = set()
        def_set = self.get_attacked_assumptions(set())
        undef_set = self.assumptions.difference(def_set)
        temp_len = len(in_set)

        while True:
            in_set = self.assumptions.difference(self.get_attacked_assumptions(undef_set))
            def_set = self.get_attacked_assumptions(in_set)
            undef_set = self.assumptions.difference(def_set)
            if temp_len == len(in_set):
                break
            else:
                temp_len = len(in_set)

        return in_set

    # returns an ABAF object as facts for ASP
    def parse_abaf_as_facts(self) -> str:
        assumptions_facts = ""
        rules_facts = ""
        contraries_facts = ""

        for assumption in self.assumptions:
            assumptions_facts += "assumption(" + assumption.name + ").\n"
            if self.contraries[assumption] is not None:
                contraries_facts += "contrary(" + assumption.name + "," + self.contraries[assumption].name + ").\n"
        for rule in self.rules:
            rules_facts += "head(" + rule.r_id + "," + rule.head.name + ").\n"
            for atom in rule.body:
                rules_facts += "body(" + rule.r_id + "," + atom.name + ").\n"

        return assumptions_facts + rules_facts + contraries_facts

    # computes the reduct of the given ABAF
    def get_reduct(self, reduct_set: Set[Atom]) -> 'ABAF':
        reduct_language = self.language.copy()
        reduct_rules = set()
        reduct_assumptions = self.assumptions.copy()
        reduct_contraries = {}

        already_used_rules = set()

        attacked_by_reduct_set = self.get_attacked_assumptions(reduct_set)

        reduct_language.difference_update(reduct_set.union(attacked_by_reduct_set))
        reduct_assumptions.difference_update(reduct_set.union(attacked_by_reduct_set))

        for rule in self.rules:
            if len(rule.body.intersection(attacked_by_reduct_set)) == 0:
                if (rule.head, frozenset(rule.body.difference(reduct_set))) not in already_used_rules:
                    reduct_rules.add(Rule(rule.r_id + "_", rule.head, rule.body.difference(reduct_set)))
                    already_used_rules.add((rule.head, frozenset(rule.body.difference(reduct_set))))

        for assumption in reduct_assumptions:
            if self.contraries[assumption] in reduct_language:
                reduct_contraries[assumption] = self.contraries[assumption]
            else:
                reduct_contraries[assumption] = None

        return ABAF(reduct_language, reduct_rules, reduct_assumptions, reduct_contraries)

    # transform the given ABAF object in a trim form by using the "get_th_sat" function
    def trim_abaf(self) -> None:
        trim_language = self.get_th_sat(self.assumptions)
        trim_rules = set()

        for rule in self.rules:
            if rule.body.issubset(trim_language):
                trim_rules.add(rule)

        for assumption in self.assumptions:
            if not self.contraries[assumption] in trim_language:
                self.contraries[assumption] = None

        self.language = trim_language
        self.rules = trim_rules
        self.well_defined()
        self.l_num_dict = self.l_num()
        self.rules_sat = self.prepare_rules_sat()
        self.solver.delete()
        self.solver = self.prepare_solver()

    # construction based on definition 33 of the paper "Argumentation Frameworks Induced by
    # Assumption-Based Argumentation: Relating Size and Complexity"
    # from Anna Rapberger, Markus Ulbricht and Johannes P. Wallner
    # returns the full dependency graph for the ABAF
    def get_dependency_graph_full(self):
        node_facts = ""
        edge_facts = ""
        already_used_edges = set()
        for atom in self.language:
            node_facts += "node(" + atom.name + ")."
        for assumption in self.assumptions:
            node_facts += "assumption(" + assumption.name + ")."
            if not self.contraries[assumption] is None:
                edge_facts += "edge(" + self.contraries[assumption].name + "," + assumption.name + ")."
        for rule in self.rules:
            for atom in rule.body:
                if (atom, rule.head) not in already_used_edges:
                    edge_facts += "edge(" + atom.name + "," + rule.head.name + ")."
                    already_used_edges.add((atom, rule.head))

        return node_facts + edge_facts

    # returns a partial labeling setting as many assumptions as possible to IN or OUT
    def propagate_io(self, part_lab: Dict[Atom, Optional[Label]]) -> Dict[Atom, Optional[Label]]:
        partial_label = part_lab.copy()
        is_labeled = True
        in_set = {assumption for assumption in partial_label.keys() if partial_label[assumption] == Label.IN}
        already_labeled = {assumption for assumption in partial_label.keys() if partial_label[assumption]
                           in {Label.IN,
                               Label.OUT,
                               Label.UNDEC}}

        while is_labeled:
            is_labeled = False
            already_labeled_new = already_labeled.copy()
            for assumption in self.assumptions.difference(already_labeled_new):
                if self.contraries[assumption] in self.get_th_sat(in_set):
                    partial_label[assumption] = Label.OUT
                    is_labeled = True
                    already_labeled.add(assumption)
                    continue
                if self.contraries[assumption] not in self.get_th_sat(self.assumptions.difference(
                        {assumption for assumption in partial_label.keys() if partial_label[assumption] == Label.OUT}
                )):
                    partial_label[assumption] = Label.IN
                    is_labeled = True
                    already_labeled.add(assumption)
                    in_set.add(assumption)

        return partial_label

    # returns a partial labeling which is correcting the given input partial labeling
    # this function contains two additional inputs, which only works with the backdoor approach
    def propagate_undec(self, part_lab: Dict[Atom, Optional[Label]], guessed_set, bd) -> Dict[Atom, Optional[Label]]:
        partial_label = part_lab.copy()
        is_labeled = False
        in_set = {assumption for assumption in partial_label.keys() if partial_label[assumption] == Label.IN}
        labeled_in_out = {assumption for assumption in partial_label.keys() if partial_label[assumption] in {Label.IN,
                                                                                                             Label.OUT}}

        for assumption in bd:
            if partial_label[assumption] == Label.IN and self.contraries[assumption] \
                    in self.get_th_sat(self.assumptions.difference({assumption for assumption in
                                                                    partial_label.keys()
                                                                    if partial_label[assumption] == Label.OUT}
                                                                   )):
                partial_label[assumption] = Label.UNDEC
                in_set.remove(assumption)
                labeled_in_out.remove(assumption)
                is_labeled = True
                if assumption in guessed_set:
                    return partial_label

            if partial_label[assumption] == Label.OUT and self.contraries[assumption] not in self.get_th_sat(in_set):
                partial_label[assumption] = Label.UNDEC
                labeled_in_out.remove(assumption)
                is_labeled = True

        while is_labeled:
            is_labeled = False
            labeled_in_out_new = labeled_in_out.copy()
            for assumption in labeled_in_out_new:
                if partial_label[assumption] == Label.IN and self.contraries[assumption] \
                        in self.get_th_sat(self.assumptions.difference({assumption for assumption in
                                                                        partial_label.keys()
                                                                        if partial_label[assumption] == Label.OUT}
                                                                       )):
                    partial_label[assumption] = Label.UNDEC
                    in_set.remove(assumption)
                    labeled_in_out.remove(assumption)
                    is_labeled = True

                if partial_label[assumption] == Label.OUT and \
                        self.contraries[assumption] not in self.get_th_sat(in_set):
                    partial_label[assumption] = Label.UNDEC
                    labeled_in_out.remove(assumption)
                    is_labeled = True

        return partial_label

    # returns admissible candidates for preferred assumption sets
    def get_adm_candidates_for_pref(self, backdoor: Set[Atom]) -> Set[FrozenSet[Atom]]:
        candidates = set()
        pw_backdoor = get_power_set(backdoor)
        for pot_candidate in pw_backdoor:
            partial_labeling = {assumption: Label.IN for assumption in pot_candidate}
            partial_labeling.update({assumption: Label.OUT for assumption in backdoor.difference(pot_candidate)})
            partial_labeling.update({assumption: None for assumption in self.assumptions.difference(backdoor)})
            partial_labeling_io = self.propagate_io(partial_labeling)
            for assumption in partial_labeling_io.keys():
                if not partial_labeling_io[assumption] in {Label.IN, Label.OUT, Label.UNDEC}:
                    partial_labeling_io[assumption] = Label.UNDEC
            partial_labeling_undec = self.propagate_undec(partial_labeling_io, pot_candidate, backdoor)
            in_set = {assumption for assumption in partial_labeling_undec.keys() if partial_labeling_undec[assumption]
                      == Label.IN}
            if in_set.intersection(backdoor) == pot_candidate:
                candidates.add(frozenset(in_set))
        return candidates

    # returns all preferred assumption sets of the ABAF using the admissible candidates
    # by checking maximality of the candidates
    def get_preferred_assumption_sets_backdoor(self, backdoor: Set[Atom]) -> Set[FrozenSet[Atom]]:
        admissible_candidates = self.get_adm_candidates_for_pref(backdoor)
        return set(get_maximal_subsets(admissible_candidates))

    # returns a minimal ACYC_DG-backdoor with the help of ASP
    def get_acyc_backdoor(self):
        dg = self.get_dependency_graph_full()
        abaf_asp = ABAF_ASP()
        backdoor_str = abaf_asp.get_acyc_backdoor_assumptions(dg)

        backdoor = set()

        for b_assumption in backdoor_str:
            for assumption in self.assumptions:
                if b_assumption == assumption.name:
                    backdoor.add(assumption)
                    break

        if len(backdoor) != len(backdoor_str):
            raise ValueError("Not all assumptions in the backdoor are found in the assumptions of the given ABAF.")

        return backdoor
