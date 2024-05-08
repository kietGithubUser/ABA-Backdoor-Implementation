from assumption_based_argumentation_framework_classes.atom import Atom
from assumption_based_argumentation_framework_classes.rule import Rule
from assumption_based_argumentation_framework_classes.abaf import ABAF
from typing import Tuple
import random


class AbafGenerator:

    # n_s: number of atoms in the language
    # n_a: percentage of assumptions in the language
    # n_rh: number of rule head atoms
    # n_rph: number of rules per head atom
    # n_spb: number of atoms in a body given through a interval
    # n_apr: number of assumptions in a body given through a interval
    def __init__(self, n_s: int, n_a: float, n_rh: int, n_rph: int, n_spb: Tuple[int, int], n_apb: Tuple[int, int]):
        self.n_s = n_s
        self.n_a = n_a
        self.n_rh = n_rh
        self.n_rph = n_rph
        self.n_spb = n_spb
        self.n_apb = n_apb

        if n_s < 1:
            raise ValueError("The language set needs to contain at least one atom.")

        if not 0 <= n_a <= 1:
            raise ValueError("The parameter n_a has to be a number between 0 and 1.")

        if not 1 <= n_rh <= n_s - int(n_s * self.n_a):
            raise ValueError("The parameter n_rh needs to be a number between"
                             " 1 and n_s - number of assumptions(given through n_a).")
        if n_rph < 1:
            raise ValueError("Rule set should not be empty. At least one head atom has to be picked.")

        if n_apb[1] > n_spb[1]:
            raise ValueError("Picking more assumptions for a body is not allowed if the maximum number of atoms in a"
                             "body is strictly smaller than the maximum number of assumptions in a body.")

        if n_apb[1] > int(n_s * self.n_a):
            raise ValueError("The number of assumptions is smaller than the maximum number of assumptions for a body.")

    # taken from Algorithm 6.1 of the paper
    # "Argument graphs and assumption-based argumentation"
    # from Robert Craven and Francesca Toni
    def generate(self):
        language = {Atom("l" + str(i)) for i in range(1, self.n_s + 1)}

        num_assumptions_to_pick = int(len(language) * self.n_a)

        assumptions = set(random.sample(list(language), num_assumptions_to_pick))

        contraries = {assumption: random.choice(list(language.difference({assumption}))) for assumption in assumptions}

        atoms_without_assumptions = language.difference(assumptions)

        rule_head_elements = set(random.sample(list(atoms_without_assumptions), self.n_rh))

        rules = set()
        already_used_rules = set()
        i = 0
        for rule_head in rule_head_elements:
            rph = self.n_rph

            while rph > 0:
                spb = random.choice(range(self.n_spb[0], self.n_spb[1] + 1))
                # if the random number spb of the atoms per body is smaller than both interval elements of n_apb
                # then we set apb to be a number between 0 and spb
                if spb < self.n_apb[1] and spb < self.n_apb[0]:
                    apb = random.choice(range(0, spb + 1))
                elif self.n_apb[1] > spb >= self.n_apb[0]:
                    apb = random.choice(range(self.n_apb[0], spb + 1))
                else:
                    apb = random.choice(range(self.n_apb[0], self.n_apb[1] + 1))

                body = set(random.sample(list(language.difference(assumptions).difference({rule_head})), spb - apb))
                body.update(set(random.sample(list(assumptions), apb)))
                rph = rph - 1
                if (rule_head, frozenset(body)) not in already_used_rules:
                    i = i + 1
                    rules.add(Rule("r" + str(i), rule_head, body))
                    already_used_rules.add((rule_head, frozenset(body)))

        return ABAF(language, rules, assumptions, contraries)
