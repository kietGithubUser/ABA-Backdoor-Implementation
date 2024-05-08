from assumption_based_argumentation_framework_classes.abaf import ABAF
from assumption_based_argumentation_framework_classes.atom import Atom
from assumption_based_argumentation_framework_classes.rule import Rule


# prints the ABAF in ASP format in an output file
def print_asp_output_file(abaf: ABAF, out_filename: str) -> None:
    with open(out_filename, 'w') as output:
        for assumption in abaf.assumptions:
            output.write(f"assumption({assumption.name}).\n")
        for assumption in abaf.assumptions:
            if abaf.contraries[assumption] is not None:
                output.write(f"contrary({assumption.name},{abaf.contraries[assumption].name}).\n")
        for rule in abaf.rules:
            output.write(f"head({rule.r_id},{rule.head.name}).\n")
            for atom in rule.body:
                output.write(f"body({rule.r_id},{atom.name}).\n")


# prints the ABAF in ICCMA format in an output file
# for more information see: https://iccma2023.github.io/rules.html
# please ensure that your ABAF has only atoms where the first letter of the name is a letter
# followed by a number (for example: r44, h749)
# also ensure that the contrary function of your ABAF is total, such that no assumption is mapped to None
def print_iccma_output_file(abaf: ABAF, out_filename: str) -> None:
    with open(out_filename, 'w') as output:
        output.write(f"p aba {len(abaf.language)}\n")
        for assumption in abaf.assumptions:
            output.write(f"a {assumption.name[1:]}\n")
        for assumption in abaf.assumptions:
            output.write(f"c {assumption.name[1:]} {abaf.contraries[assumption].name[1:]}\n")
        for rule in abaf.rules:
            output.write(f"r {rule.head.name[1:]} {' '.join({atom.name[1:] for atom in rule.body})}\n")


# parse an ABAF from iccma file to an ABAF object
def load_abaf_from_iccma_file(filename: str):
    assumptions_dict = {}
    language_dict = {}
    contraries = {}
    rules = set()
    i = 0

    with open(filename, 'r') as file:

        next(file)

        for line in file:
            parts = line.split()
            first_letter = parts[0]

            if first_letter == 'a':

                assumption = parts[1]
                assumptions_dict[assumption] = Atom("l" + assumption)
                language_dict[assumption] = assumptions_dict[assumption]
            elif first_letter == 'c':

                first_assumption = parts[1]
                second_atom = parts[2]
                if second_atom not in language_dict.keys():
                    language_dict[second_atom] = Atom("l" + second_atom)
                    contraries[assumptions_dict[first_assumption]] = language_dict[second_atom]
                else:
                    contraries[assumptions_dict[first_assumption]] = language_dict[second_atom]
            elif first_letter == 'r':

                i = i + 1
                head = parts[1]
                if head not in language_dict.keys():
                    language_dict[head] = Atom("l" + head)
                body = frozenset(parts[2:])
                for atom in body:
                    if atom not in language_dict.keys():
                        language_dict[atom] = Atom("l" + atom)
                rules.add(Rule("r" + str(i), language_dict[head], {language_dict[atom] for atom in body}))

        assumptions = {assumptions_dict[asmp_key] for asmp_key in assumptions_dict.keys()}
        language = {language_dict[asmp_key] for asmp_key in language_dict.keys()}
        return ABAF(language, rules, assumptions, contraries)
