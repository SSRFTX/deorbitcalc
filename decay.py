import numpy as np
from atmosphere import get_density

MU = 3.986004418e14      
R_EARTH = 6371.0          
RE_ENTRY_ALT = 120.0

def decay_rate(a_km, Cd, A_eff, mass):
    altitude_km = a_km - R_EARTH
    if altitude_km <= RE_ENTRY_ALT:
        return 0.0
    rho = get_density(altitude_km)
    a_m = a_km * 1000.0
    drag = -rho * np.sqrt(MU * a_m) * (Cd * A_eff) / mass
    return drag / 1000.0

def simulate_decay(altitude_km, Cd, A_eff, mass, dt_hours = 1.0, max_years = 30.0):
    dt = dt_hours * 3600.0
    max_steps = int(max_years * 365.25 * 24 / dt_hours)
    a = altitude_km + R_EARTH
    t = 0.0
    altitudes = [altitude_km]
    times = [0.0]

    for _ in range(max_steps):
        alt = a - R_EARTH
        if alt <= RE_ENTRY_ALT:
            break
        k1 = decay_rate(a, Cd, A_eff, mass)
        k2 = decay_rate(a + 0.5 * dt * k1, Cd, A_eff, mass)
        k3 = decay_rate(a + 0.5 * dt * k2, Cd, A_eff, mass)
        k4 = decay_rate(a + dt * k3, Cd, A_eff, mass)
        a += (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        t += dt
        altitudes.append(a - R_EARTH)
        times.append(t / (365.25 * 24 * 3600))
    return {
        "lifetime_years": t / (365.25 * 24 * 3600),
        "altitudes": np.array(altitudes),
        "times_years": np.array(times),
    }
if __name__ == "__main__":
    result = simulate_decay(altitude_km=400,Cd=2.2,A_eff=10.0,mass=150,)
    print(f"Deorbit lifetime:  {result['lifetime_years']:.2f} years")
    print(f"Final altitude:  {result['altitudes'][-1]:.1f} km")
    print(f"Data points:  {len(result['altitudes'])}")
    result2 = simulate_decay(altitude_km=600, Cd=2.2, A_eff=10.0, mass=150)
    print(f"\n600 km test:")
    print(f"Deorbit lifetime: {result2['lifetime_years']:.2f} years")