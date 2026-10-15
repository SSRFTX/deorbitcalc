import numpy as np
from decay import simulate_decay

def run_monte_carlo(altitude_km, Cd_mean, A_eff, mass, n_runs=1000, fcc_limit=5.0):
    lifetimes = np.zeros(n_runs)

    for i in range(n_runs):
        rho_multiplier = np.random.lognormal(mean=0.0, sigma=0.3)
        Cd = np.random.normal(loc=Cd_mean, scale=0.3)
        Cd = max(Cd, 0.5)
        alt = np.random.normal(loc=altitude_km, scale=5.0)
        alt = max(alt, 150.0)
        effective_area = A_eff * rho_multiplier
        result = simulate_decay(alt, Cd, effective_area, mass)
        lifetimes[i] = result["lifetime_years"]
        if (i + 1) % (n_runs // 10) == 0:
            pct = 100 * (i + 1) / n_runs
            print(f"    {pct:.0f}% complete ({i+1}/{n_runs})")
    compliant = np.sum(lifetimes <= fcc_limit)
    compliance_pct = 100.0 * compliant / n_runs
    return {
        "lifetimes": lifetimes,
        "mean": np.mean(lifetimes),
        "median": np.median(lifetimes),
        "std": np.std(lifetimes),
        "p5": np.percentile(lifetimes, 5),
        "p50": np.percentile(lifetimes, 50),
        "p95": np.percentile(lifetimes, 95),
        "compliance_pct": compliance_pct,
        "fcc_limit": fcc_limit,
        "n_runs": n_runs,
    }

def print_results(results):
    print("\n" + "=" * 50)
    print("  MONTE CARLO DEORBIT ANALYSIS")
    print("=" * 50)
    print(f"  Simulations run:    {results['n_runs']}")
    print(f"  FCC limit:          {results['fcc_limit']} years")
    print(f"  Compliance:         {results['compliance_pct']:.1f}%")
    print("-" * 50)
    print(f"  Mean lifetime:      {results['mean']:.2f} years")
    print(f"  Median lifetime:    {results['median']:.2f} years")
    print(f"  Std deviation:      {results['std']:.2f} years")
    print("-" * 50)
    print(f"  Best case  (5th %%):  {results['p5']:.2f} years")
    print(f"  Typical   (50th %%):  {results['p50']:.2f} years")
    print(f"  Worst case (95th %%): {results['p95']:.2f} years")
    print("=" * 50)

if __name__ == "__main__":
    print("Running 1000 simulations: 600 km, 10 m^2 sail, 150 kg")
    results = run_monte_carlo(altitude_km=600, Cd_mean=2.2, A_eff=10.0, mass=150, n_runs=1000,)
    print_results(results)

    # print("Running 1000 simulations: 500 km, 10 m^2 sail, 150 kg")
    # results = run_monte_carlo(altitude_km=500, Cd_mean=2.2, A_eff=10.0, mass=150, n_runs=1000,)
   # print_results(results) 