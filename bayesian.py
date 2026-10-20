import numpy as np

def bayesian_update(prior_lifetimes, observed_decay_rate, predicted_decay_rate, uncertainty=0.2):
    n = len(prior_lifetimes)
    sigma = abs(observed_decay_rate) * uncertainty
    if sigma == 0:
        sigma = 0.1
    likelihoods = np.exp(-0.5 * ((predicted_decay_rate - observed_decay_rate) / sigma)) ** 2
    weights = likelihoods / np.sum(likelihoods)
    posterior_mean = np.average(prior_lifetimes, weights=weights)
    posterior_var = np.average((prior_lifetimes - posterior_mean) ** 2, weights=weights)
    posterior_std = np.sqrt(posterior_var)
    resample_idx = np.random.choice(n, size=n, replace=True, p=weights)
    posterior_samples = prior_lifetimes[resample_idx]
    ess = 1.0 / np.sum(weights ** 2)
    return {
        "posterior_mean": posterior_mean, 
        "posterior_std": posterior_mean, 
        "posterior_p5": np.percentile(posterior_samples, 5), 
        "posterior_p50": np.percentile(posterior_samples, 50), 
        "posterior_p95": np.percentile(posterior_samples, 95), 
        "effective_sample_size": ess, 
        "weights": weights, 
        "posterior_samples": posterior_samples,}

def print_comparison(prior_lifetimes, posterior):
    print("\n" + "=" * 55)
    print("  BAYESIAN UPDATE: PRIOR vs POSTERIOR")
    print("=" * 55)
    print(f"  {'Statistic':<25} {'Prior':>10} {'Posterior':>10}")
    print("  " + "-" * 48)
    print(f"  {'Mean (years)':<25} "
          f"{np.mean(prior_lifetimes):>10.2f} "
          f"{posterior['posterior_mean']:>10.2f}")
    print(f"  {'Std dev (years)':<25} "
          f"{np.std(prior_lifetimes):>10.2f} "
          f"{posterior['posterior_std']:>10.2f}")
    print(f"  {'5th percentile':<25} "
          f"{np.percentile(prior_lifetimes, 5):>10.2f} "
          f"{posterior['posterior_p5']:>10.2f}")
    print(f"  {'50th percentile':<25} "
          f"{np.percentile(prior_lifetimes, 50):>10.2f} "
          f"{posterior['posterior_p50']:>10.2f}")
    print(f"  {'95th percentile':<25} "
          f"{np.percentile(prior_lifetimes, 95):>10.2f} "
          f"{posterior['posterior_p95']:>10.2f}")
    print("  " + "-" * 48)
    print(f"  Effective sample size: "
          f"{posterior['effective_sample_size']:.0f} / "
          f"{len(prior_lifetimes)}")
    print("=" * 55)

if __name__ == "__main__":
    from montecarlo import run_monte_carlo
    print("Generating prior predictions (500 Monte Carlo runs)...")
    mc = run_monte_carlo(altitude_km=500, Cd_mean=2.2, A_eff=10.0, mass=150, n_runs=500)
    prior = mc["lifetimes"]
    observed_rate = 40.0
    altitude_drop = 500.0 - 120.0
    predicted_rates = altitude_drop / prior
    median_rate = np.median(predicted_rates)
    observed_rate = median_rate * 1.2
    print(f"Observed decay rate: {observed_rate:.1f} km/year")
    print("Applying Bayesian update...")
    posterior = bayesian_update(prior, observed_rate, predicted_rates, uncertainty=0.5)
    print_comparison(prior, posterior)
    print(f"\n  Observation was 20% faster than model median.")
    print("  Posterior shifted toward shorter lifetimes.")