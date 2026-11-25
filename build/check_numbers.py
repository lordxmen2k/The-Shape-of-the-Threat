#!/usr/bin/env python3
"""Check the manuscript's headline numbers against the generator.

The rule this script enforces is simple: a number that the book leans on
must be computed by ``build/compute_numbers.py`` and must appear in the
manuscript exactly as the generator renders it.  A number that was typed by
hand, carried forward from a draft, or rounded the wrong way fails here.

Each entry below names a quantity, pulls it out of the generator's JSON,
formats it the way the book writes it, and asserts that the string is
present in the manuscript.

    python3 build/check_numbers.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "build", "compute_numbers.py")


def load() -> dict:
    proc = subprocess.run([sys.executable, GEN, "--json"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit("compute_numbers.py failed")
    return json.loads(proc.stdout)


def manuscript() -> str:
    """The whole book, as one string, with the control sequences stripped."""
    parts = []
    for base in ("source", "source/chapters", "source/generated"):
        p = os.path.join(ROOT, base)
        if not os.path.isdir(p):
            continue
        for name in sorted(os.listdir(p)):
            if not name.endswith(".tex"):
                continue
            with open(os.path.join(p, name), encoding="utf-8") as fh:
                parts.append(fh.read())
    text = "\n".join(parts)
    text = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}$^_&~]", " ", text)
    return re.sub(r"\s+", " ", text)


def main() -> int:
    d = load()
    text = manuscript()

    totals = d["cneos_totals"]
    arr25 = d["cneos_arrivals_2025"]
    arr24 = d["cneos_arrivals_2024"]
    spec = d["spectrum_coverage_140m"]
    ladder = d["accountability_ladder"]
    two = d["two_station_range_error_m"]
    cent = d["interferometric_centroid_mas"]
    keyhole = d["keyhole_magnification_km"]
    cases = d["counterfactual_cases"]
    amas = d["amas_lead_time"]
    records = d["detection_records"]

    def rec(desc: str, value, *variants: str):
        """One required number, with any accepted spellings."""
        out.append((desc, [str(value)] + list(variants)))

    out: list[tuple[str, list[str]]] = []

    # ---- the catalogue ---------------------------------------------------
    rec("known near-Earth objects", f"{totals['All']:,}")
    rec("known NEAs of 140 m and more", f"{totals['140m+']:,}")
    rec("known NEAs of 1 km and more", f"{totals['1km+']:,}")
    rec("2025 arrivals, all sizes", f"{arr25['All']:,}")
    rec("2025 arrivals, 140 m and more", f"{arr25['140m+']:,}")
    rec("2024 arrivals, 140 m and more", f"{arr24['140m+']:,}")
    rec("NEAs with a measured spectrum", f"{spec['with_spectra']:,.0f}")
    rec("NEAs with no physical account", f"{spec['without']:,.0f}")

    # ---- the Earth-Moon baseline and the range it buys -------------------
    rec("Earth-Moon baseline", f"{d['earth_moon_baseline_km']:,.0f} km")
    rec("range error at YR4 discovery distance, 1 mas",
        f"{two['delta0.00554_sigma1.0mas_m']:.2f} m")
    rec("range error at 0.05 AU, 1 mas",
        f"{two['delta0.05_sigma1.0mas_m']:,.0f} m")
    rec("differential astrometry at 100 m", f"{cent['B100m']:.4f} mas")
    rec("differential astrometry at 1.5 km", f"{cent['B1500m']:.4f} mas")

    # ---- the service rate -------------------------------------------------
    rec("baseline-orientation sweep rate",
        f"{d['lunar_baseline_rotation_deg_per_day']:.3f}")
    rec("days for a 90 degree sweep", f"{d['days_for_90deg']:.2f}")
    rec("campaigns per year", f"{d['service_capacity_per_year']:.1f}")
    rec("share of the annual arrival rate",
        f"{100 * d['annual_coverage_fraction']:.1f} per cent")
    rec("years to clear the backlog", f"{d['backlog_clearance_years']:.0f}")

    # ---- the accountability ladder ---------------------------------------
    rec("energy factor, Sentry state",
        f"{ladder['Sentry tabulated state  (D 30 %, rho 30 %)']:.2f}")
    rec("energy factor, thermal spread removed",
        f"{ladder['thermal-model spread removed (D 19 %, rho 30 %)']:.2f}")
    rec("energy factor, resolved shape",
        f"{ladder['+ resolved shape (D 10 %, rho 30 %)']:.2f}")
    rec("energy factor, shape and density",
        f"{ladder['+ close-approach density (D 10 %, rho 10 %)']:.2f}")
    rec("energy factor, both at five per cent",
        f"{ladder['+ both at 5 %']:.2f}")
    rec("YR4 energy spread across the model set",
        f"{d['yr4_energy_spread_factor']:.3f}")
    rec("YR4 energy spread, thermal model alone",
        f"{d['yr4_thermal_model_only_factor']:.3f}")
    rec("YR4 energy spread, density alone",
        f"{d['yr4_energy_decomposition']['density']:.3f}",
        f"{d['yr4_energy_decomposition']['density']:.2f}")

    # ---- the keyhole ------------------------------------------------------
    rec("keyhole displacement from the diameter",
        f"{keyhole['Diameter 270 +/- 60 m']['displacement_km']:.1f} km")
    rec("keyhole magnification from the diameter",
        f"{keyhole['Diameter 270 +/- 60 m']['factor']:.1f}")
    rec("back-solved along-track dispersion",
        f"{d['sigma_zeta_2029_apophis_km']:.1f} km")

    # ---- the diameter requirement ----------------------------------------
    rec("diameter for a factor of three", f"{d['diameter_requirement']['factor3.0_rho0.3']:.1f} per cent")
    rec("diameter for a factor of two", f"{d['diameter_requirement']['factor2.0_rho0.3']:.1f} per cent")

    # ---- the CAPS re-derivation ------------------------------------------
    rec("CAPS maximum-baseline reproduction",
        f"{d['caps_rule_max_dev_pct']['b_max']:.2f} per cent")
    rec("CAPS precision reproduction",
        f"{d['caps_rule_max_dev_pct']['precision']:.2f} per cent")

    # ---- the thermal channel ---------------------------------------------
    rec("Wien peak of sunlit regolith", f"{d['wien_peak_390K_um']:.2f}")
    rec("contrast at 0.3 AU", f"{d['mir_contrast']['r0.3_vs_sunlit']:.2f}")
    rec("contrast at 1.0 AU", f"{d['mir_contrast']['r1.0_vs_sunlit']:.3f}")

    # ---- the discovery baseline ------------------------------------------
    for key, label in (("30 m  city-scale impactor", "30 m class"),
                        ("140 m potentially hazardous", "140 m class"),
                        ("1 km  global-scale impactor", "1 km class")):
        rec(f"implied ground limit, {label}",
            f"{amas[key]['implied_ground_AU']:.3f} AU")
    for r in records:
        if r.get("range_km"):
            rec(f"close-approach range, {r['des']} {r['ca_date']}",
                f"{r['range_km']:,.0f} km")

    # ---- the worked cases -------------------------------------------------
    for c in cases:
        rec(f"counterfactual angle, {c['label']}", f"{c['theta_mas']:,.1f}")

    missing = []
    for desc, variants in out:
        if not any(v in text for v in variants):
            missing.append((desc, variants[0]))

    width = max(len(d) for d, _ in missing) if missing else 0
    for desc, want in missing:
        print(f"[FAIL] {desc.ljust(width)}  expected {want!r} in the manuscript")
    print()
    print(f"{len(out) - len(missing)}/{len(out)} headline numbers verified "
          f"against the generator.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
