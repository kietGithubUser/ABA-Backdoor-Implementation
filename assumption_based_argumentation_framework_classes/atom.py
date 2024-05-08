# in this class, we implement an atom for the ABAF
class Atom:

    # name: name for the atom
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name
