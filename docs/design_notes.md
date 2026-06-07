# Design Notes & Lessons Learned

## Simulation Environment Notes

### ANSYS Electronics Desktop — Circuit Simulator
- Analysis type: **Linear Network Analysis (LNA)** was used (not S-parameter sweep directly). LNA in ANSYS Circuit computes S-params via nodal admittance matrix solution.
- A warning about "Z parameters invalid due to singularity" appeared for both lumped and distributed simulations — this is expected behavior when floating nodes exist at the port reference planes and does not affect S-parameter accuracy.
- Two sweep configurations were used: `LinearFrequency` (0–4 GHz) and `LinearFrequency1` (0–4 GHz with finer step). Both converged identically.

### ANSYS HFSS — Full-Wave Solver
- Boundary conditions: **PerfE** (Perfect Electric Conductor) for signal traces and ground plane; **Open1** radiation boundary (absorbing boundary condition) enclosing the airbox.
- Excitation: **Wave Ports** (P1, P2) at the SMA feed interfaces. Port field display was verified to show the quasi-TEM mode correctly.
- Mesh: Adaptive meshing with target max delta-S = 0.01 (converged in simulation).
- The 3D model geometry: FR4 substrate body as the dielectric solid, copper traces as a PEC sheet (Ind1), ground plane as a PEC sheet (Ground).

---

## Fabrication Notes

### Copper Strip Method
- A commercially available copper adhesive tape was used instead of chemical etching — this is the practical lab approach, resulting in slightly irregular trace edges.
- The wide capacitive section (W = 22.63 mm) was the most challenging to cut cleanly; any fraying at the edges will alter the effective Z_L and shift the capacitive susceptance.
- SMA edge-mount connectors were soldered at both ports. Soldering quality directly affects the S11 match — cold joints introduce series resistance and inductive discontinuities.

### Key Physical Observation
The filter footprint exhibits a characteristic **cross / plus-sign shape**: two narrow longitudinal lines (inductors, W = 0.54 mm) separated by a single wide transverse section (capacitor, W = 22.63 mm). This shape is a direct topological signature of the π-network (L–C–L) prototype.

---

## Measurement Notes — NanoVNA-F V2

### Calibration
- OSL (Open-Short-Load) calibration was performed on PORT 1 (CH0) only, before connecting the DUT.
- Sweep: 500 MHz – 3 GHz, 101 points, 25 MHz/step.
- Reference impedance: 50 Ω.

### Observed Anomalies
- The S11 curve on the NanoVNA Saver shows some ripple in the passband and an unexpected notch-like feature near ~2.7–2.9 GHz in S21. This is likely caused by:
  1. Connector-to-trace solder joint parasitics.
  2. Fringing fields at the abrupt impedance steps (junction discontinuities — not modeled in the simple stepped-impedance approximation).
  3. Substrate surface wave excitation at higher frequencies (FR4 is lossy and dispersive above ~2 GHz).
  4. Possible copper tape edge irregularities causing spurious resonances.
- The S21 minimum of −15.68 dB occurs at 2.925 GHz, which corresponds approximately to the first spurious passband resonance expected in stepped-impedance designs (typically 3–5× f_c for standard designs).

### Marker Readings from NanoVNA Saver
| Marker | Frequency | VSWR | Return Loss | S21 |
|---|---|---|---|---|
| M1 (main observation) | 975 MHz | 3.361 | −5.33 dB | −1.151 dB |
| M2 | 500 MHz | 1.419 | −15.23 dB | −0.119 dB |
| M3 | 500 MHz | 1.419 | −15.23 dB | −0.119 dB |

The best VSWR (closest to 1.0) occurs in the deep passband (500 MHz), consistent with a well-matched low-pass filter below cutoff.

---

## Discrepancies Between Simulation and Measurement

| Source | Cause | Mitigation |
|---|---|---|
| Lumped ↔ Distributed (~0.1 dB) | Stepped-impedance is an approximation valid only for βl << λ/4 | Use exact synthesis (e.g., Richards transform) for better accuracy |
| Distributed ↔ HFSS (~0.09 dB) | Fringing fields at impedance steps not in circuit model | Add junction discontinuity models in circuit sim |
| HFSS ↔ Measured (~0.01 dB at f_c) | Fabrication tolerances, connector parasitics, FR4 loss tangent variation | PCB etching instead of copper tape; calibrated SMA connectors |

---

## Possible Improvements

1. **Use PCB etching** instead of copper tape for clean trace edges — reduces fringing field irregularities and improves repeatability.
2. **Add junction discontinuity compensation** (chamfering or tapering at impedance steps) to suppress spurious reflections.
3. **Higher-order filter** (N = 5) for sharper rolloff, or switch to Chebyshev approximation for equiripple response.
4. **Replace FR4 with Rogers 4003C** (ε_r = 3.55, tan δ = 0.0027) for lower loss and better high-frequency performance.
5. **Full 2-port calibration** (SOLT) on the NanoVNA for more accurate S-parameter measurement, particularly for S21.
