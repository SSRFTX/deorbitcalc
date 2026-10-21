import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from decay import simulate_decay
from montecarlo import run_monte_carlo
from sensitivity import run_sensitivity
from bayesian import bayesian_update
from knowledge_graph import build_graph, query_by_regulator

st.set_page_config(page_title="DeorbitCalc", layout="wide")
st.title("DeorbitCalc")
st.markdown("**Satellite Deorbit Compliance Calculator**")
st.markdown("Monte Carlo uncertainty quantification for FCC 5-year " "post-mission disposal rule compliance.")
st.sidebar.header("Satellite Parameters")
altitude = st.sidebar.slider("Initial Altitude (km)", 200, 800, 500, step=10)
mass = st.sidebar.number_input("Satellite Mass (kg)", 1.0, 10000.0, 150.0, step=10.0)
area = st.sidebar.number_input("Drag Sail Area (m²)", 0.1, 100.0, 10.0, step=0.5)
Cd_mean = st.sidebar.slider("Drag Coefficient (Cd)", 1.0, 4.0, 2.2, step=0.1)
n_runs = st.sidebar.selectbox("Monte Carlo Runs", [100, 500, 1000, 2000], index=1)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Single Decay", "Monte Carlo", "Sensitivity", "Bayesian Update", "Knowledge Graph"])
with tab1:
    st.header("Deterministic Decay Simulation")
    result = simulate_decay(altitude, Cd_mean, area, mass)
    lifetime = result["lifetime_years"]
    col1, col2 = st.columns(2)
    with col1:
        if lifetime <= 5.0:
            st.success(f"Lifetime:  {lifetime:.2f} years - COMPLIANT")
        else:
            st.error(f"Lifetime:  {lifetime:.2f} years - NON-COMPLIANT")
    with col2:
        st.metric("Re-entry Time", f"{lifetime:.2f} years")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(result["times_years"], result["altitudes"], color="#2563eb")
    ax.axhline(y=120, color="red", linestyle="--", label="Re-entry (120 km)")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Altitude (km)")
    ax.set_title("Orbital Decay Over Time")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with tab2:
    st.header("Monte Carlo Uncertainty Analysis")
    if st.button("Run Monte Carlo Simulation"):
        with st.spinner(f"Running {n_runs} simulations..."):
            mc = run_monte_carlo(altitude, Cd_mean, area, mass, n_runs=n_runs)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean Lifetime", f"{mc['mean']:.2f} yr")
        with col2:
            st.metric("95th Percentile", f"{mc['p95']:.2f} yr")
        with col3:
            if mc["compliance_pct"] >= 95:
                st.metric("FCC Compliance", f"{mc['compliance_pct']:.1f}%")
            else:
                st.metric("FCC Compliance", f"{mc['compliance_pct']:.1f}%")
                st.warning("Below 95% confidence threshold")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        ax1.hist(mc["lifetimes"], bins=40, color="#2563eb",
                 edgecolor="white", alpha=0.8)
        ax1.axvline(x=5.0, color="red", linestyle="--",
                    label="FCC 5-year limit")
        ax1.axvline(x=mc["mean"], color="orange", linestyle="--",
                    label=f"Mean: {mc['mean']:.2f} yr")
        ax1.set_xlabel("Lifetime (years)")
        ax1.set_ylabel("Count")
        ax1.set_title("Lifetime Distribution")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        percentiles = [mc["p5"], mc["p50"], mc["p95"]]
        labels = ["P5", "P50", "P95"]
        colors = ["#22c55e", "#2563eb", "#ef4444"]
        ax2.barh(labels, percentiles, color=colors)
        ax2.axvline(x=5.0, color="red", linestyle="--",
                    label="FCC limit")
        ax2.set_xlabel("Lifetime (years)")
        ax2.set_title("Percentile Summary")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        st.pyplot(fig)

        st.session_state["mc_results"] = mc

with tab3:
    st.header("Sobol Sensitivity Analysis")
    N_sobol = st.selectbox("Saltelli samples (N)", [64, 128, 256], index=1)
    if st.button("Run Sensitivity Analysis"):
        with st.spinner(
            f"Running {N_sobol * 8} simulations for Sobol indices..."
        ):
            sa = run_sensitivity(altitude, area, mass, N=N_sobol)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        x = np.arange(len(sa["names"]))
        ax1.bar(x, sa["S1"], color="#2563eb")
        ax1.set_xticks(x)
        ax1.set_xticklabels(sa["names"])
        ax1.set_ylabel("First-Order Sobol Index")
        ax1.set_title("Main Effects")
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)

        ax2.bar(x, sa["ST"], color="#7c3aed")
        ax2.set_xticks(x)
        ax2.set_xticklabels(sa["names"])
        ax2.set_ylabel("Total-Order Sobol Index")
        ax2.set_title("Total Effects (incl. interactions)")
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)

        st.pyplot(fig)

        st.markdown("### Interpretation")
        dominant = sa["names"][np.argmax(sa["S1"])]
        st.write(
            f"**{dominant}** is the dominant source of uncertainty, "
            f"accounting for {sa['S1'][np.argmax(sa['S1'])]:.1%} "
            f"of total variance."
        )

with tab4:
    st.header("Bayesian Update with Observed Data")
    st.markdown(
        "Simulate observing a satellite's actual decay rate, "
        "then update the Monte Carlo predictions."
    )

    observed_rate = st.slider(
        "Observed Decay Rate (km/year)", 10.0, 500.0, 100.0, step=10.0
    )
    obs_uncertainty = st.slider(
        "Observation Uncertainty", 0.1, 1.0, 0.5, step=0.1
    )

    if st.button("Run Bayesian Update"):
        with st.spinner("Running Monte Carlo + Bayesian update..."):
            mc = run_monte_carlo(
                altitude, Cd_mean, area, mass, n_runs=500
            )
            prior = mc["lifetimes"]
            altitude_drop = altitude - 120.0
            predicted_rates = altitude_drop / prior

            posterior = bayesian_update(
                prior, observed_rate, predicted_rates,
                uncertainty=obs_uncertainty
            )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Prior (model only)")
            st.write(f"Mean: {np.mean(prior):.2f} years")
            st.write(f"Std: {np.std(prior):.2f} years")
            st.write(
                f"P5-P95: {np.percentile(prior, 5):.2f} "
                f"- {np.percentile(prior, 95):.2f} years"
            )
        with col2:
            st.markdown("### Posterior (model + observation)")
            st.write(f"Mean: {posterior['posterior_mean']:.2f} years")
            st.write(f"Std: {posterior['posterior_std']:.2f} years")
            st.write(
                f"P5-P95: {posterior['posterior_p5']:.2f} "
                f"- {posterior['posterior_p95']:.2f} years"
            )
            st.write(
                f"Effective sample size: "
                f"{posterior['effective_sample_size']:.0f} / 500"
            )

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(prior, bins=30, alpha=0.5, color="#2563eb",
                label="Prior", density=True)
        ax.hist(posterior["posterior_samples"], bins=30, alpha=0.5,
                color="#22c55e", label="Posterior", density=True)
        ax.set_xlabel("Lifetime (years)")
        ax.set_ylabel("Density")
        ax.set_title("Prior vs Posterior Lifetime Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

with tab5:
    st.header("Satellite-Regulation Knowledge Graph")
    G = build_graph()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nodes", G.number_of_nodes())
    with col2:
        st.metric("Edges", G.number_of_edges())

    regulator = st.selectbox("Select Regulator", ["FCC", "ITU", "ESA"])
    sats = query_by_regulator(G, regulator)
    rule = G.nodes[regulator].get("disposal_rule_years", "N/A")
    st.write(
        f"**{regulator}** {rule}-year disposal rule applies to:"
    )
    for sat in sats:
        attrs = G.nodes[sat]
        sail = ("with drag sail" if attrs.get("has_drag_sail")
                else "no drag sail")
        st.write(f"- {sat} ({attrs['altitude_km']} km, {sail})")

    st.markdown("### All Relationships")
    for src, tgt, data in G.edges(data=True):
        rel = data.get("relation", "?")
        st.text(f"{src} --[{rel}]--> {tgt}")