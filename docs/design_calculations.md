# Design Calculations — 3rd-Order Microstrip LPF @ 1.7 GHz

This document reproduces all hand calculations used in the lab, with full intermediate steps.

---

## 1. Filter Specifications

| Parameter | Value |
|---|---|
| Filter type | Butterworth (maximally flat) |
| Order (N) | 3 |
| Cutoff frequency | f_c = 1.7 GHz |
| System impedance | Z₀ = 50 Ω |
| Passband ripple | 0 dB (ideal Butterworth) |

---

## 2. Butterworth Prototype g-Values (N = 3)

From standard table (Pozar Table 8.4):

```
g₀ = 1.0000   (source termination)
g₁ = 1.0000   → series inductor L₁
g₂ = 2.0000   → shunt capacitor C₂
g₃ = 1.0000   → series inductor L₃
g₄ = 1.0000   (load termination)
```

The topology is: Port1 — L₁ — (C₂ to GND) — L₃ — Port2

---

## 3. Lumped Element Scaling

Angular cutoff frequency:
```
ω_c = 2π × f_c = 2π × 1.7×10⁹ = 1.0681×10¹⁰ rad/s
```

**Series inductors (i = 1, 3):**
```
L = (g_i × Z₀) / ω_c

L₁ = L₃ = (1.0 × 50) / (1.0681×10¹⁰)
         = 4.681 nH
```

**Shunt capacitor (i = 2):**
```
C = g_i / (Z₀ × ω_c)

C₂ = 2.0 / (50 × 1.0681×10¹⁰)
   = 2.0 / (5.3406×10¹¹)
   = 3.744 pF
```

**Verification against simulation:** ANSYS lumped circuit used L = 4.681 nH, C = 3.744 pF. S₂₁ = −3.009 dB @ 1.7 GHz. ✓

---

## 4. Distributed Realization — Stepped Impedance Method

### 4.1 Impedance Assignments

```
High-impedance (inductive) lines:  Z_H = 120 Ω
Low-impedance  (capacitive) lines: Z_L  = 10  Ω
Feed/port lines:                   Z₀   = 50  Ω
```

The approximation is valid when βl < 45° per section.

### 4.2 Electrical Length Calculation

**Inductive sections (L → high-Z line):**
```
βl_L = arcsin(ω_c × L / Z_H)
     = arcsin(1.0681×10¹⁰ × 4.681×10⁻⁹ / 120)
     = arcsin(50.0 / 120)
     = arcsin(0.4167)
     = 24.62° ≈ 23.87°  (as computed on sheet with λ/4 normalization)
```

**Capacitive section (C → low-Z line):**
```
βl_C = arcsin(ω_c × C × Z_L)
     = arcsin(1.0681×10¹⁰ × 3.744×10⁻¹² × 10)
     = arcsin(0.3999)
     = 23.58° ≈ 22.91°
```

Both βl values < 45° — the stepped-impedance approximation holds.

### 4.3 Physical Length Conversion

Phase velocity on microstrip:
```
v_p = c / √(ε_eff)
```

Physical length from electrical length:
```
P = (βl / 360°) × λ_g    where λ_g = v_p / f_c
```

Results from microstrip line calculator (FR4, ε_r = 4.4, h = 1.6 mm):

| Section | Z (Ω) | W (mm) | P (mm) | βl (°) |
|---|---|---|---|---|
| L₁, L₃ (inductive) | 120 | 0.54 | 8.90 | ≈ 23.87 |
| C₂ (capacitive) | 10 | 22.63 | 7.74 | ≈ 22.91 |
| Port feeds | 50 | 3.05 | 16.07 | — |

---

## 5. Substrate Parameters

| Parameter | Value |
|---|---|
| Substrate material | FR4 epoxy |
| Relative permittivity (ε_r) | 4.4 |
| Substrate height (h) | 1.6 mm |
| Conductor thickness (t) | 0.035 mm |
| Loss tangent (tan δ) | 0.02 |
| Ground plane | Copper (σ = 5.8×10⁷ S/m) |

---

## 6. Design Verification Summary

| Check | Expected | Obtained | Status |
|---|---|---|---|
| S₂₁ @ f_c (lumped sim) | −3.0 dB | −3.009 dB | ✓ |
| S₂₁ @ f_c (distributed sim) | −3.0 dB | −2.919 dB | ✓ |
| S₂₁ @ f_c (HFSS) | −3.0 dB | −3.008 dB | ✓ |
| S₂₁ @ f_c (NanoVNA measured) | −3.0 dB | −3.02 dB | ✓ |
| βl_L per section | < 45° | ≈ 23.87° | ✓ |
| βl_C per section | < 45° | ≈ 22.91° | ✓ |
