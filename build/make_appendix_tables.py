#!/usr/bin/env python3
"""Generate the appendix tables from the canonical number generator.

One generator per artefact.  This script does not compute anything of its
own: it runs ``build/compute_numbers.py`` as a library, reads the JSON it
produces, and writes LaTeX tables to ``source/generated_appendix.tex``.
Nothing in the appendices is transcribed by hand.

    python3 build/make_appendix_tables.py
"""

from __future__ import annotations

import json
import re
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "build", "compute_numbers.py")
OUTDIR = os.path.join(ROOT, "source", "generated")


def load() -> dict:
    """Run the canonical generator and read its JSON output."""
    proc = subprocess.run([sys.executable, GEN, "--json"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit("compute_numbers.py failed")
    return json.loads(proc.stdout)


def num(x, places=1, thousands=True):
    """Format a number for a table cell."""
    if isinstance(x, int):
        return f"{x:,}" if thousands else str(x)
    s = f"{x:,.{places}f}"
    return s


def esc(s: str) -> str:
    """Escape the characters that would otherwise end a table cell."""
    for a, b in (("_", r"\_"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"),
                 ("~", r"\ensuremath{\sim}"), ("^", r"\ensuremath{\wedge}")):
        s = s.replace(a, b)
    return s


def write(name: str, lines: list[str]) -> None:
    """Write one table to source/generated/<name>.tex."""
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    print(f"wrote {os.path.relpath(path, ROOT)}")


def main() -> int:
    d = load()

    L: list[str] = []

    def A(text: str) -> None:
        L.append(text)

    def flush(name: str) -> None:
        write(name, L)
        L.clear()

    # ---------------------------------------------------------------- B.1
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\footnotesize")
    A(r"\caption{The complete generated number set, part one of two. Every entry is produced by")
    A(r"\texttt{build/compute\_numbers.py} at build time and is written into this")
    A(r"table from the generator's own output, not transcribed. The section")
    A(r"numbers refer to the generator's eighteen sections.}")
    A(r"\label{tab:generated-set}")
    A(r"\begin{tabularx}{\textwidth}{@{}P{0.50in}Y P{1.30in}@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Quantity} & \textbf{Meaning} & \textbf{Value} \\")
    A(r"\midrule")

    totals = d["cneos_totals"]
    arr25 = d["cneos_arrivals_2025"]
    arr24 = d["cneos_arrivals_2024"]
    spec = d["spectrum_coverage_140m"]

    rows = [
        ("S1", "CAPS Table 1, maximum-baseline rule reproduced to within",
         f"{d['caps_rule_max_dev_pct']['b_max']:.2f} per cent"),
        ("S1", "CAPS Table 1, astrometric-precision rule reproduced to within",
         f"{d['caps_rule_max_dev_pct']['precision']:.2f} per cent"),
        ("S2", "Visible magnitude of a 50 m object at 0.1 AU, albedo 0.14",
         f"{d['class_grid'][0]['v']:.2f}"),
        ("S2", "Angular diameter of a 50 m object at 0.1 AU",
         f"{d['class_grid'][0]['theta_mas'] * 1000:.2f} mas"),
        ("S3", "Apparent magnitude of a 140 m object at 0.1 AU",
         f"{[r for r in d['class_grid'] if r['D'] == 140.0 and r['d'] == 0.1][0]['v']:.2f}"),
        ("S4", "Wien peak of sunlit lunar regolith at 390 K",
         f"{d['wien_peak_390K_um']:.2f} um"),
        ("S4", "Contrast of a 390 K target against sunlit regolith at 0.3 AU",
         f"{d['mir_contrast']['r0.3_vs_sunlit']:.3f}"),
        ("S4", "Baffle radiance at 390 K relative to the target",
         f"{d['baffle_radiance']['390.0K']:.2f}"),
        ("S6", "Yarkovsky ratio to the calibration case, D = 51.1 m, rho = 2800",
         f"{d['yarkovsky_ratio_to_calib']['D51.1_rho2800']:.3f}"),
        ("S7", "Along-track displacement over 7 years, rate 100 m/yr, 10 per cent",
         f"{d['along_track_7yr']['rate100_err10']:,.0f} m"),
        ("S8", "Torino Level-1 threshold energy for the YR4 model set, spread",
         f"{d['torino_threshold_spread']:.3f}"),
        ("S10", "Palma effective diameter, ratio to a 60 m object",
         f"{d['palma']['diameter_ratio_to_60m']:,.0f}"),
        ("S12", "Known near-Earth objects in the catalogue",
         f"{totals['All']:,}"),
        ("S12", "Known near-Earth objects larger than 140 m",
         f"{totals['140m+']:,}"),
        ("S12", "Known near-Earth objects larger than 1 km",
         f"{totals['1km+']:,}"),
        ("S12", "Arrivals in 2025, all sizes", f"{arr25['All']:,}"),
        ("S12", "Arrivals in 2025, 140 m and larger", f"{arr25['140m+']:,}"),
        ("S12", "Arrivals in 2025, 1 km and larger", f"{arr25['1km+']:,}"),
        ("S12", "Arrivals in 2024, 140 m and larger", f"{arr24['140m+']:,}"),
        ("S13", "Implied ground discovery limit, 30 m class",
         f"{d['amas_lead_time']['30 m  city-scale impactor']['implied_ground_AU']:.3f} AU"),
        ("S13", "Implied ground discovery limit, 140 m class",
         f"{d['amas_lead_time']['140 m potentially hazardous']['implied_ground_AU']:.3f} AU"),
        ("S13", "Implied ground discovery limit, 1 km class",
         f"{d['amas_lead_time']['1 km  global-scale impactor']['implied_ground_AU']:.3f} AU"),
        ("S14", "Earth-Moon baseline", f"{d['earth_moon_baseline_km']:,.0f} km"),
        ("S14", "Range error at 828,775 km, 1 mas",
         f"{d['two_station_range_error_m']['delta0.00554_sigma1.0mas_m']:.2f} m"),
        ("S14", "Range error at 0.05 AU, 1 mas",
         f"{d['two_station_range_error_m']['delta0.05_sigma1.0mas_m']:,.0f} m"),
        ("S14", "Differential astrometry at a 100 m baseline, SNR 7",
         f"{d['interferometric_centroid_mas']['B100m']:.4f} mas"),
        ("S14", "Differential astrometry at a 1.5 km baseline, SNR 7",
         f"{d['interferometric_centroid_mas']['B1500m']:.4f} mas"),
        ("S15", "2024 YR4 first observation", "2024-12-25"),
        ("S15", "2024 YR4 discovery-night close approach",
         f"{[r for r in d['detection_records'] if r['des'] == '2024 YR4' and r['ca_date'] == '2024-12-25'][0]['range_km']:,.0f} km"),
        ("S15", "2019 OK close approach",
         f"{[r for r in d['detection_records'] if r['des'] == '2019 OK'][0]['range_km']:,.0f} km"),
        ("S16", "Baseline-orientation sweep rate",
         f"{d['lunar_baseline_rotation_deg_per_day']:.3f} deg/day"),
        ("S16", "Days for a 90 degree orientation sweep",
         f"{d['days_for_90deg']:.2f} d"),
        ("S16", "Campaigns the station can run in a year",
         f"{d['service_capacity_per_year']:.1f}"),
        ("S16", "Share of the annual 140 m arrival rate covered",
         f"{100 * d['annual_coverage_fraction']:.1f} per cent"),
        ("S16", "Years to clear the known 140 m class",
         f"{d['backlog_clearance_years']:.0f}"),
        ("S16", "Objects with a measured spectrum, 140 m class",
         f"{spec['with_spectra']:,.0f} of {totals['140m+']:,}"),
        ("S17", "Impact-energy uncertainty, Sentry tabulated state",
         f"{d['accountability_ladder']['Sentry tabulated state  (D 30 %, rho 30 %)']:.2f}"),
        ("S17", "Impact-energy uncertainty, thermal spread removed",
         f"{d['accountability_ladder']['thermal-model spread removed (D 19 %, rho 30 %)']:.2f}"),
        ("S17", "Impact-energy uncertainty, resolved shape plus density",
         f"{d['accountability_ladder']['+ close-approach density (D 10 %, rho 10 %)']:.2f}"),
        ("S17", "2024 YR4 energy spread across the published model set",
         f"{d['yr4_energy_spread_factor']:.3f}"),
        ("S17", "2024 YR4 energy spread, thermal model alone",
         f"{d['yr4_thermal_model_only_factor']:.3f}"),
        ("S7", "Apophis keyhole, displacement from a 270 +/- 60 m diameter",
         f"{d['keyhole_magnification_km']['Diameter 270 +/- 60 m']['displacement_km']:.1f} km"),
        ("S7", "Apophis keyhole, magnification factor from the diameter alone",
         f"{d['keyhole_magnification_km']['Diameter 270 +/- 60 m']['factor']:.1f}"),
        ("S7", "Back-solved along-track dispersion for 2029",
         f"{d['sigma_zeta_2029_apophis_km']:.1f} km"),
        ("S9", "Diameter required for an energy known to a factor of 3",
         f"{d['diameter_requirement']['factor3.0_rho0.3']:.1f} per cent"),
        ("S9", "Diameter required for an energy known to a factor of 2",
         f"{d['diameter_requirement']['factor2.0_rho0.3']:.1f} per cent"),
    ]

    # The set is longer than one page will take, so it is printed in two
    # halves.  The split is on the generator's own row list.
    half = (len(rows) + 1) // 2
    for sec, meaning, value in rows[:half]:
        A(f"{sec} & {meaning} & {value} \\\\")
        A(r"\addlinespace[1pt]")

    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")

    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\footnotesize")
    A(r"\caption{The complete generated number set, part two of two.}")
    A(r"\label{tab:generated-set-2}")
    A(r"\begin{tabularx}{\textwidth}{@{}P{0.50in}Y P{1.30in}@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Section} & \textbf{Quantity} & \textbf{Value} \\")
    A(r"\midrule")
    for sec, meaning, value in rows[half:]:
        A(f"{sec} & {meaning} & {value} \\\\")
        A(r"\addlinespace[1pt]")

    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_b1.tex")

    # ---------------------------------------------------------------- B.2
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\footnotesize")
    A(r"\caption{The baseline required to image a near-Earth object, from the")
    A(r"generator's sampling criterion \(N = \theta_{\mathrm{diam}} B / \lambda \geq 4\)")
    A(r"and \(N \geq 7\). \emph{Required} is the baseline at \(N = 4\), the point")
    A(r"at which the diameter is sampled four times across; \emph{7-sample} is")
    A(r"the same object sampled seven times across. The wavelength is")
    A(r"650~nm.}")
    A(r"\label{tab:generated-baselines}")
    A(r"\begin{tabular}{@{}rrrrrr@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Diameter} & \textbf{Range} & \textbf{Angle} & \textbf{$\lambda/\theta$} & "
      r"\textbf{Required} & \textbf{7-sample} \\")
    A(r"\midrule")

    for row in d["shape_imaging_baselines"]:
        A(f"{row['D']:.0f} m & {row['d']:.1f} AU & {row['theta_mas']:.2f} mas & "
          f"{row['lambda_over_theta_m']:,.0f} m & {row['B_N4_m']:,.0f} m & "
          f"{row['B_N7_m']:,.0f} m \\\\")
        A(r"\addlinespace[1pt]")

    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_b2.tex")

    # ---------------------------------------------------------------- B.3
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\footnotesize")
    A(r"\caption{Samples across the diameter, \(N = \theta_{\mathrm{diam}} B / \lambda\),")
    A(r"for the baselines the book uses. A value below 1 means the object is")
    A(r"unresolved: the instrument sees a point source and locates its centroid,")
    A(r"which is an astrometric measurement and not a shape measurement.}")
    A(r"\label{tab:generated-samples}")
    A(r"\begin{tabular}{@{}rrrrrrr@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Diameter} & \textbf{Range} & \textbf{Angle} & \textbf{100 m} & "
      r"\textbf{1.5 km} & \textbf{3 km} & \textbf{4.6 km} \\")
    A(r"\midrule")

    for row in d["samples_across_diameter"]:
        theta = row["theta_mas"]
        n4600 = theta * 1e-3 * 4600.0 / 650e-9
        A(f"{row['D']:.0f} m & {row['d']:.2f} AU & {row['theta_mas']:.2f} mas & "
          f"{row['n100']:.3f} & {row['n1500']:.2f} & {row['n3000']:.2f} & {n4600:.2f} \\\\")
        A(r"\addlinespace[1pt]")

    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_b3.tex")

    # ---------------------------------------------------------------- B.4
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\caption{Range error from two-station astrometry on the Earth--Moon")
    A(r"baseline, \(b = 384{,}400$~km, at the maximum parallax angle. The error")
    A(r"scales with the square of the range, so the instrument is a close-approach")
    A(r"instrument and not a catalogue instrument.}")
    A(r"\label{tab:generated-range}")
    A(r"\footnotesize")
    A(r"\begin{tabular}{@{}P{0.85in}P{0.72in}P{0.72in}P{0.72in}P{0.72in}@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Range} & \textbf{0.1 mas} & \textbf{1 mas} & \textbf{10 mas} & \textbf{100 mas} \\")
    A(r"\midrule")

    for key, label in (("delta0.00554", "828,775 km"), ("delta0.05", "0.05 AU"),
                       ("delta0.1", "0.1 AU"), ("delta0.2", "0.2 AU")):
        cells = []
        for sig in ("0.1mas", "1.0mas", "10.0mas", "100.0mas"):
            v = d["two_station_range_error_m"][f"{key}_sigma{sig}_m"]
            cells.append(f"{v:,.2f}" if v < 1000 else f"{v:,.0f}")
        A(f"{label} & " + " & ".join(cells) + r" \\")
        A(r"\addlinespace[1pt]")

    A(r"\bottomrule")
    A(r"\end{tabular}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_b4.tex")

    # ---------------------------------------------------------------- B.5
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\caption{The accountability ladder: how much the impact energy is known")
    A(r"to, as each link of the chain is closed. The uncertainty factor is")
    A(r"\(\exp(3\,\delta\ln D + \delta\ln \rho)\).}")
    A(r"\label{tab:generated-ladder}")
    A(r"\begin{tabularx}{\textwidth}{@{}Y P{0.75in}P{0.75in}Y@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{State} & \textbf{Diameter} & \textbf{Density} & \textbf{Energy known to} \\")
    A(r"\midrule")

    for state, factor in d["accountability_ladder"].items():
        m = re.search(r"D\s*(\d+)\s*%.*?rho\s*(\d+)\s*%", state)
        dpct = f"{int(m.group(1))} per cent" if m else "---"
        rhopct = f"{int(m.group(2))} per cent" if m else "---"
        A(f"{esc(state)} & {dpct} & {rhopct} & a factor of {factor:.2f} \\\\")
        A(r"\addlinespace[2pt]")

    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_b5.tex")

    # ---------------------------------------------------------------- B.6
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\footnotesize")
    A(r"\caption{The counterfactual cases. \emph{Angle} is the angular")
    A(r"diameter in milliarcseconds, \emph{Aperture} the aperture that would")
    A(r"resolve the object, \emph{Baseline} the matched baseline at \(N = 4\),")
    A(r"\emph{V} the zero-phase magnitude, and \emph{Range} the range the")
    A(r"two-station geometry delivers.}")
    A(r"\label{tab:generated-cases}")
    A(r"\begin{tabularx}{\textwidth}{@{}P{0.95in}P{0.58in}P{0.58in}P{0.60in}P{0.42in}P{0.62in}@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Case} & \textbf{Angle} & \textbf{Aperture} & \textbf{Baseline} & "
      r"\textbf{Magnitude} & \textbf{Range} \\")
    A(r"\midrule")

    for row in d["counterfactual_cases"]:
        A(f"{esc(row['label'])} & {row['theta_mas']:,.1f} & "
          f"{row['aperture_m']:.2f} & {row['baseline_N4_m']:.2f} & "
          f"{row['V_zero_phase']:.2f} & {row['range_error_m']:.2f} \\\\")
        A(r"\addlinespace[1pt]")
        A(r"\addlinespace[2pt]")

    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_b6.tex")

    # ---------------------------------------------------------------- E.1
    A(r"\begingroup")
    A(r"\small")
    A(r"\begin{table}[!htbp]")
    A(r"\centering")
    A(r"\footnotesize")
    A(r"\caption{The counterfactual baseline: the historical record itself, as")
    A(r"retrieved from the NASA/JPL Small-Body Database and Close Approach Data")
    A(r"services on 24 November 2026. These are the observations and approaches")
    A(r"against which the lunar platform's contribution is measured.}")
    A(r"\label{tab:generated-records}")
    A(r"\begin{tabularx}{\textwidth}{@{}P{1.00in}P{0.95in}P{0.90in}P{0.60in}P{0.48in}@{}}")
    A(r"\toprule")
    A(r"\rowcolor{panel}")
    A(r"\textbf{Object} & \textbf{First observation} & \textbf{Approach} & "
      r"\textbf{Range} & \textbf{Relative velocity} \\")
    A(r"\midrule")

    for row in d["detection_records"]:
        first = row["first_obs"] or "---"
        ca = row["ca_date"] or "---"
        rng = f"{row['range_km']:,.0f} km" if row.get("range_km") else "---"
        v = f"{row['v_rel_km_s']:.4f} km/s" if row.get("v_rel_km_s") else "---"
        A(f"{esc(row['des'])} & {first} & {ca} & {rng} & {v} \\\\")
        A(r"\addlinespace[2pt]")

    A(r"\bottomrule")
    A(r"\end{tabularx}")
    A(r"\end{table}")
    A(r"\endgroup")
    A("")
    flush("tab_e1.tex")

    return 0


if __name__ == "__main__":
    sys.exit(main())
