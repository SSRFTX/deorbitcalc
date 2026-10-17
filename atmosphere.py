import numpy as np

ATMOSPHERE_TABLE = [
    (0,    1.225,         7.249),
    (100,  5.297e-7,      5.877),
    (150,  2.070e-9,      7.263),
    (200,  2.789e-10,    11.397),
    (250,  7.248e-11,    16.045),
    (300,  2.418e-11,    22.523),
    (350,  9.518e-12,    29.740),
    (400,  3.725e-12,    37.105),
    (450,  1.585e-12,    45.546),
    (500,  6.967e-13,    53.628),
    (600,  1.454e-13,    53.298),
    (700,  3.614e-14,    58.515),
    (800,  1.170e-14,    60.828),
    (900,  5.245e-15,    63.822),
    (1000, 3.019e-15,    71.835),
]

def get_density(altitude_km):
    if altitude_km < 0:
        raise ValueError("Altitude cannot be negative")
    if altitude_km > 1000:
        return 0.0
    for i in range(len(ATMOSPHERE_TABLE) - 1):
        alt_base, rho_base, H = ATMOSPHERE_TABLE[i]
        alt_next = ATMOSPHERE_TABLE[i+1][0]
        if altitude_km < alt_next:
            return rho_base * np.exp(-(altitude_km - alt_base) / H)
    alt_base, rho_base, H = ATMOSPHERE_TABLE[-1]
    return rho_base
if __name__ == "__main__":
    test_altitudes = [200, 300, 400, 500, 600]
    print("Altitude (km) | Density (kg/m^3)")
    print("-" * 38)
    for alt in test_altitudes:
        rho = get_density(alt)
        print(f"    {alt:>6}        |   {rho:.4e}")