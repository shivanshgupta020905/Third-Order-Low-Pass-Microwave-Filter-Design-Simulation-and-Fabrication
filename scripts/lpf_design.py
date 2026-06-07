"""
lpf_design.py
=============
3rd-Order Butterworth Stepped-Impedance Microstrip LPF Design Script
Target: f_c = 1.7 GHz, Z0 = 50 Ohm, FR4 substrate (er = 4.4, h = 1.6 mm)

Reproduces all calculations from LNMIIT Microwave Lab Experiment 7 (2025-26).
Author: Shivansh Gupta (24UEC228)
"""

import math

# ──────────────────────────────────────────────────────────────────
# 1. SPECIFICATIONS
# ──────────────────────────────────────────────────────────────────
N  = 3           # Filter order
fc = 1.7e9       # Cutoff frequency [Hz]
Z0 = 50.0        # System characteristic impedance [Ohm]
ZH = 120.0       # High-impedance line (inductive sections) [Ohm]
ZL = 10.0        # Low-impedance line (capacitive sections) [Ohm]

# Substrate parameters (FR4)
er = 4.4         # Relative permittivity
h  = 1.6e-3      # Substrate height [m]
t  = 0.035e-3    # Conductor thickness [m]

c = 3e8          # Speed of light [m/s]

# ──────────────────────────────────────────────────────────────────
# 2. BUTTERWORTH PROTOTYPE g-VALUES (N=3, from standard table)
# ──────────────────────────────────────────────────────────────────
g = [1.0, 1.0, 2.0, 1.0, 1.0]   # g0..g4

print("=" * 60)
print("3rd-Order Butterworth LPF Design — 1.7 GHz Microstrip")
print("=" * 60)
print(f"\nSpecifications:")
print(f"  N  = {N}")
print(f"  fc = {fc/1e9:.2f} GHz")
print(f"  Z0 = {Z0} Ohm")
print(f"  ZH = {ZH} Ohm (high-Z, inductive)")
print(f"  ZL = {ZL} Ohm (low-Z, capacitive)")

print(f"\nButterworth prototype g-values:")
for i, gi in enumerate(g):
    print(f"  g{i} = {gi:.4f}")

# ──────────────────────────────────────────────────────────────────
# 3. LUMPED ELEMENT SCALING
# ──────────────────────────────────────────────────────────────────
wc = 2 * math.pi * fc   # Angular cutoff frequency [rad/s]
print(f"\nAngular cutoff frequency:")
print(f"  wc = 2π × {fc/1e9:.2f}×10⁹ = {wc:.4e} rad/s")

print(f"\nLumped Element Values:")

L_vals = {}
C_vals = {}

# Topology: L1 (series) — C2 (shunt) — L3 (series)
# g1, g3 → series inductors
# g2     → shunt capacitor

for i in [1, 3]:
    L = (g[i] * Z0) / wc
    L_vals[i] = L
    print(f"  L{i} = g{i} × Z0 / wc = {g[i]} × {Z0} / {wc:.4e} = {L*1e9:.4f} nH")

for i in [2]:
    C = g[i] / (Z0 * wc)
    C_vals[i] = C
    print(f"  C{i} = g{i} / (Z0 × wc) = {g[i]} / ({Z0} × {wc:.4e}) = {C*1e12:.4f} pF")

# ──────────────────────────────────────────────────────────────────
# 4. STEPPED-IMPEDANCE ELECTRICAL LENGTHS
# ──────────────────────────────────────────────────────────────────
print(f"\nStepped-Impedance Electrical Lengths:")
print(f"  (Approximation valid for βl < 45° per section)")

bl_L = {}
for i in [1, 3]:
    argument = wc * L_vals[i] / ZH
    if abs(argument) <= 1.0:
        bl_deg = math.degrees(math.asin(argument))
    else:
        bl_deg = float('nan')
    bl_L[i] = bl_deg
    print(f"  βl(L{i}) = arcsin(wc × L{i} / ZH) = arcsin({argument:.4f}) = {bl_deg:.2f}°")

bl_C = {}
for i in [2]:
    argument = wc * C_vals[i] * ZL
    if abs(argument) <= 1.0:
        bl_deg = math.degrees(math.asin(argument))
    else:
        bl_deg = float('nan')
    bl_C[i] = bl_deg
    print(f"  βl(C{i}) = arcsin(wc × C{i} × ZL) = arcsin({argument:.4f}) = {bl_deg:.2f}°")

# Validity check
for i in [1, 3]:
    ok = bl_L[i] < 45.0
    print(f"  βl(L{i}) = {bl_L[i]:.2f}° < 45° → {'VALID ✓' if ok else 'INVALID ✗'}")
for i in [2]:
    ok = bl_C[i] < 45.0
    print(f"  βl(C{i}) = {bl_C[i]:.2f}° < 45° → {'VALID ✓' if ok else 'INVALID ✗'}")

# ──────────────────────────────────────────────────────────────────
# 5. MICROSTRIP LINE WIDTH CALCULATOR
#    Closed-form expressions (Wheeler / Hammerstad)
# ──────────────────────────────────────────────────────────────────

def microstrip_width(Z_target, er, h):
    """
    Compute microstrip width W for a given characteristic impedance Z_target.
    Uses standard closed-form synthesis (Pozar Eq. 3.196–3.197).
    Returns W in meters.
    """
    A = (Z_target / 60.0) * math.sqrt((er + 1) / 2.0) + \
        ((er - 1) / (er + 1)) * (0.23 + 0.11 / er)
    B = 377 * math.pi / (2 * Z_target * math.sqrt(er))

    W_over_h_A = 8 * math.exp(A) / (math.exp(2 * A) - 2)      # W/h < 2
    W_over_h_B = (2 / math.pi) * (B - 1 - math.log(2 * B - 1) +
                  ((er - 1) / (2 * er)) * (math.log(B - 1) + 0.39 - 0.61 / er))

    # Select correct solution
    if W_over_h_A < 2:
        W_over_h = W_over_h_A
    else:
        W_over_h = W_over_h_B

    return W_over_h * h


def microstrip_eff_er(W, er, h):
    """Effective permittivity for a microstrip line."""
    W_h = W / h
    eff = (er + 1) / 2.0 + (er - 1) / 2.0 * (1 + 12 * h / W) ** (-0.5)
    return eff


def microstrip_length(bl_deg, Z_target, er, h, fc):
    """
    Compute physical length P [m] for a given electrical length [degrees]
    on a microstrip with effective permittivity computed from Z_target.
    """
    W = microstrip_width(Z_target, er, h)
    er_eff = microstrip_eff_er(W, er, h)
    lambda_g = c / (fc * math.sqrt(er_eff))   # guided wavelength
    P = (bl_deg / 360.0) * lambda_g
    return P


print(f"\nMicrostrip Physical Dimensions (FR4: er={er}, h={h*1e3:.1f} mm):")
print(f"{'Section':<20} {'Z [Ω]':<10} {'W [mm]':<12} {'P [mm]':<12} {'βl [°]':<10}")
print("-" * 65)

sections = [
    ("L1, L3 (inductive)", ZH, bl_L[1]),
    ("C2 (capacitive)",    ZL, bl_C[2]),
    ("Port feeds (50Ω)",   Z0, None),
]

for name, Z_sec, bl in sections:
    W = microstrip_width(Z_sec, er, h)
    if bl is not None:
        P = microstrip_length(bl, Z_sec, er, h, fc)
        print(f"{name:<20} {Z_sec:<10.1f} {W*1e3:<12.4f} {P*1e3:<12.4f} {bl:<10.2f}")
    else:
        print(f"{name:<20} {Z_sec:<10.1f} {W*1e3:<12.4f} {'(feed)':12} {'—':10}")

# ──────────────────────────────────────────────────────────────────
# 6. SUMMARY TABLE (as fabricated)
# ──────────────────────────────────────────────────────────────────
print(f"""
{'='*60}
FABRICATION DIMENSIONS SUMMARY
{'='*60}
  L (series inductors):  W = 0.54 mm,  P = 8.90 mm  [ZH = 120 Ω]
  C (shunt capacitor):   W = 22.63 mm, P = 7.74 mm  [ZL = 10 Ω]
  50Ω feed ports:        W = 3.05 mm,  P = 16.07 mm [Z0 = 50 Ω]
{'='*60}
  Lumped values:   L1 = L3 = {L_vals[1]*1e9:.3f} nH,  C2 = {C_vals[2]*1e12:.3f} pF
  Cutoff target:   fc = {fc/1e9:.2f} GHz
  Expected S21 @ fc = -3.01 dB (Butterworth 3 dB definition)
{'='*60}
""")
