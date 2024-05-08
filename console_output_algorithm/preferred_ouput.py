from assumption_based_argumentation_framework_classes.abaf import ABAF
import time


# prints all preferred assumption sets using backdoor approach
def preferred_assumption_sets_acyc(abaf: ABAF) -> None:
    start_time = time.perf_counter()
    grounded_assumption_set = abaf.get_grounded_assumption_set()
    gr_reduct = abaf.get_reduct(grounded_assumption_set)
    abaf.solver.delete()
    gr_reduct.trim_abaf()
    start_time_bd = time.perf_counter()
    backdoor = gr_reduct.get_acyc_backdoor()
    end_time_bd = time.perf_counter()
    print("It took", end_time_bd - start_time_bd, "seconds to generate a minimal ACYC_DG-backdoor.")
    print("Backdoor:", [assumption.name for assumption in backdoor], ", Size:", len(backdoor))
    pr_educt = gr_reduct.get_preferred_assumption_sets_backdoor(backdoor)
    end_time = time.perf_counter()
    gr_reduct.solver.delete()
    preferred_assumption_sets = set()
    for prefset in pr_educt:
        preferred_assumption_sets.add(frozenset(grounded_assumption_set.union(prefset)))
    for prefset in preferred_assumption_sets:
        print([assumption.name for assumption in prefset])
    print(len(preferred_assumption_sets), "is the number of preferred assumption sets (using backdoor approach).")
    print("It took", end_time - start_time, "seconds to generate all preferred assumption sets.")
