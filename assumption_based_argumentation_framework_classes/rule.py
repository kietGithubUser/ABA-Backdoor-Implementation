from assumption_based_argumentation_framework_classes.atom import Atom
from typing import Set


# in this class, we implement a rule for the ABAF
class Rule:

    # r_id: unique id for the Rule object
    # head: head atom of a rule
    # body: atom set of a rule
    def __init__(self, r_id: str, head: Atom, body: Set[Atom]):
        self.r_id = r_id
        self.head = head
        self.body = body

    def __str__(self):
        return self.rule_to_string()

    def __eq__(self, other):
        return self.r_id == other.r_id

    def __hash__(self):
        return hash(self.r_id)

    # returns rule in readable form string form
    def rule_to_string(self) -> str:
        return "Rule " + self.r_id + ": " + str(self.head) + " <- " + ','.join(str(atom) for atom in self.body)
