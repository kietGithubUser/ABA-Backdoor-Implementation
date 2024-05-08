import os
from generators.abaf_generator import AbafGenerator
from io_files.abaf_io import load_abaf_from_iccma_file
from console_output_algorithm.preferred_ouput import preferred_assumption_sets_acyc

# in this main.py, we test our backdoor approach with some ABAFs in three different ways:
# 1. using a generator, 2. using one ABAF of the 400 test instances, 3. using an own ABAF
# the output and the time (in seconds) will be printed on the console
# we can easily adapt the main.py, if we want to change anything
# we also included a simple loop iterating through all 400 ABAFs from the "iccma23_aba_benchmarks" directory
# (but we only included it as a comment, since it will be not possible for all of them to terminate)
# if not already done: "clingo" package and "python-sat" package should be installed

if __name__ == '__main__':
    #####################################################
    # 1. example generator
    # just change the parameters for other ABAFs (see "generators" directory)
    # we can read this example generator as follow:
    # 20 atoms, 25% of 20 atoms are assumptions, 15 non-assumptions out of 20 atoms are occurring in a head of a rule
    # 2 rules for each head atom (in this case 30 rules, though it could be less if a duplicate rule is generated)
    # 0-4 atoms occur in the body of a rule, 0-4 assumptions occur in the body of a rule
    print("Example with the ABAF generator:")
    abaf_gen = AbafGenerator(20, 0.25, 15, 2, (0, 3), (0, 3))
    abaf = abaf_gen.generate()
    preferred_assumption_sets_acyc(abaf)
    print()

    #####################################################
    # 2. example with one of the 400 test instances
    # we can test one of the other 400 ABAFs, just change the name (of the second parameter) when using
    # the "load_abaf_from_iccma_file" function
    print("Example with one of the 400 ABAF instances:")
    abaf_iccma = load_abaf_from_iccma_file(os.path.join("iccma23_aba_benchmarks", "aba_25_0.3_5_5_6.aba"))
    preferred_assumption_sets_acyc(abaf_iccma)
    print()

    #####################################################
    # 3. example with one ABAF from the "own_abafs" directory
    # we can test our own ABAFs as long as we use the ICCMA format
    # for more information see: https://iccma2023.github.io/rules.html
    # just put them in the "own_abafs" directory and
    # change the name (of the second parameter) when using the "load_abaf_from_iccma_file" function
    print("Example with one of our own ABAFs:")
    abaf_own = load_abaf_from_iccma_file(os.path.join("own_abafs", "abaf2.aba"))
    preferred_assumption_sets_acyc(abaf_own)
    print()

    ####################################################
    # this part can be used if you remove all those "#"
    # here we simply iterate through all 400 test instances
    # CAREFUL: Not all instances will terminate, since many backdoors are too big for testing purposes
    # we also included a variable for a maximum number of iterations, max_iterations can be changed to a natural number between 1 and 400

    # script_directory = r"iccma23_aba_benchmarks"
    # iccma_files = os.listdir(script_directory)
    # sorted_iccma_files = sorted(iccma_files, key=lambda x: x.lower())
    # counter = 1
    # max_iterations = 40
    # for abaf_iccma_file in sorted_iccma_files:
    #   print(f"{counter}. ABAF: {abaf_iccma_file}")
    #   counter = counter + 1
    #   abaf_iccma_loop = load_abaf_from_iccma_file((os.path.join("iccma23_aba_benchmarks", abaf_iccma_file)))
    #   preferred_assumption_sets_acyc(abaf_iccma_loop)
    #   print()
    #   if(counter > max_iterations):
    #       break
