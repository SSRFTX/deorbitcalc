import numpy as np
from SALib.sample import saltelli
from SALib.analyze import sobol
from decay import simulate_decay

PROBLEM = {"num_vars": 3, "names": ["rho_multiplier", "Cd", "altitude_offset",], "bounds": [[0.5, 2.0], [1.5, 3.0], [-15.0, 15.0],],}

def run_sensitivity(altitude_km, A_eff, mass, N=256):
    param_values = saltelli.sample(PROBLEM, N)
    total_runs = len(param_values)
    print(f"Running {total_runs} simulations for Sobol analysis...")
    lifetimes = np.zeros(total_runs)
    for i, params in enumerate(param_values):
        rho_mult, Cd, alt_offset = params
        alt = altitude_km + alt_offset
        alt = max(alt, 150.0)
        effective_area = A_eff * rho_mult
        result = simulate_decay(alt, Cd, effective_area, mass)
        lifetimes[i] = result["lifetime_years"]
        if (i + 1) % (total_runs // 4) == 0:
            pct = 100 * (i + 1) / total_runs
            print(f" {pct:.0f}% complete ({i + 1}/{total_runs})")
    Si = sobol.analyze(PROBLEM, lifetimes)
    return {"S1": Si["S1"], "ST": Si["ST"], "names": PROBLEM["names"], "lifetimes": lifetimes, "n_runs": total_runs,}

def print_results(results):
    print("\n" + "=" * 55)
    print("  SOBOL SENSITIVITY ANALYSIS")
    print("=" * 55)
    print(f"  Total simulations: {results['n_runs']}")
    print()
    print(f"  {'Parameter':<22} {'First-Order':>12} {'Total':>12}")
    print("  " + "-" * 48)

    for name, s1, st in zip(results["names"], results["S1"], results["ST"]):
        print(f"    {name:<22} {s1:>11.3f} {st:>11.3f}")
    print()
    print("  First-order: direct contribution to variance")
    print("  Total-order: direct + all interactions")
    print("=" * 55)
    dominant = results["names"][np.argmax(results["S1"])]
    print(f"\n  Dominant factor:  {dominant}")

if __name__ == "__main__":
    print("Sobol analysis: 500 km, 10 m^2 sail, 150 kg\n")
    results = run_sensitivity(altitude_km=500, A_eff=10.0, mass=150, N=256,)
    print_results(results)