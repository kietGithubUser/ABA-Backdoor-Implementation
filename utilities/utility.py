from itertools import combinations
import math


# power set function using the "combinations" function from "itertools"
def get_power_set(input_set):
    input_set_list = list(input_set)
    return {frozenset(subset) for r in range(len(input_set_list) + 1) for subset in combinations(input_set_list, r)}


# a help function to collect the answer sets from an ASP solution (only use this function with clingo)
# the input variable "solutions_list" will be modified after using the function
# "solutions_list" will contain all answer sets, after executing "collect_solution"
def collect_solution(model, solutions_list):
    answer_set_str = [str(symbol.arguments[0]) if symbol.arguments
                      else str(symbol) for symbol in model.symbols(shown=True)]
    solutions_list.append(answer_set_str)


# get all maximal subsets for given input set of sets
def get_maximal_subsets(input_frozensets):
    subsets = list(input_frozensets)
    n = len(subsets)
    maximal_subsets = []
    for i in range(n):
        is_maximal = True
        for j in range(n):
            if i != j and subsets[i].issubset(subsets[j]):
                is_maximal = False
                break
        if is_maximal:
            maximal_subsets.append(subsets[i])

    return maximal_subsets


# returns the sum for a binomial coefficient for input "n" from "j" to "k"
def binom_sum(n, j, k):
    binomial_coefficient_sum = 0
    for i in range(j, k + 1):
        binomial_coefficient_sum += math.comb(n, i)
    return binomial_coefficient_sum
