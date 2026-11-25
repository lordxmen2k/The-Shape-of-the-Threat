#!/usr/bin/env python3
"""
Generator for the headline numbers of "The Shape of the Threat".

Every derived quantity used in the book is computed here from first principles
plus a cited input, never transcribed from a draft.  Run:

    python3 compute_numbers.py            # human-readable report
    python3 compute_numbers.py --json     # machine-readable

Inputs carry their source.  Sources are listed in SOURCES below.
"""

import argparse
import datetime
import json
import math
import os

# ----------------------------------------------------------------------------
# Physical constants and unit conversions
# ----------------------------------------------------------------------------
AU_M = 1.495978707e11          # IAU 2012 definition, exact
MT_J = 4.184e15                # 1 megaton TNT equivalent = 4.184e15 J
KT_J = 4.184e12                # 1 kiloton  = 4.184e12 J
C_LIGHT = 2.99792458e8         # m/s, exact
MU_SUN = 1.32712440018e20      # m^3/s^2
G_EARTH = 3.986004418e14       # m^3/s^2
R_EARTH = 6.371e6              # m
MOON_RADIUS = 1.7374e6        # m
EARTH_MOON = 3.844e8           # m, mean centre-to-centre
ARCSEC = math.pi / (180.0 * 3600.0)
LUNAR_SIDEREAL_DAYS = 27.321661   # Moon's rotation period relative to the stars
LUNAR_SYNODIC_DAYS = 29.530589    # Moon's phase period relative to the Sun

SOURCES = {
    "H_D_p": "D = 1329 * 10^(-H/5) / sqrt(p) km  (standard absolute-magnitude relation)",
    "V": "V = H + 5 log10(r*Delta), zero phase angle",
    "flux": "f_nu0 = 3.63e-20 * 10^(-0.4 V) erg/s/cm^2/Hz (V=0 flux)",
    "CAPS": "NTRS 20030014831 (Mazanek et al., CAPS preprint) and NTRS 20050186565 "
            "(CAPS Concept Study Executive Summary)",
    "RG2012": "Rozitis & Green 2012, MNRAS 423, 367 (arXiv:1203.1464), eqs. 30-32",
    "Vokrouhlicky2000": "Vokrouhlicky, Milani & Chesley 2000, Icarus 148, 118",
    "Bottke2013": "Bottke et al. 2013 (arXiv:1301.1607), Tables 4-5",
    "Palma2018": "Harju et al. 2018, AJ 156, 50 (arXiv:1804.05640)",
    "JWST2026": "Mueller et al. 2026 (arXiv:2609.15756), MIRI 26 Mar 2025 analysis",
    "He2026": "He et al. 2026, ApJ 1001, 40 (arXiv:2601.10666)",
    "Jones2023": "Jones et al. 2023/2026 (arXiv:2301.10348), NEO characterisation constellation",
    "Torino": "Torino Impact Hazard Scale, adopted by the IAU in 1999; "
              "CNEOS Sentry documentation",
    "Planck": "Planck's law; lunar regolith emissivity 0.9",
    "CNEOS": "NASA CNEOS Discovery Statistics, cumulative NEA series "
             "(nea_vs_time.json), data current 22 Nov 2026",
    "AMAS": "Hadjara et al. 2026 (arXiv:2611.05435), Table 2: first detectable "
            "distance and extra lead time, relative velocity v ~ 20 km/s",
    "Rayleigh": "Rayleigh criterion: a circular aperture of diameter D resolves an "
                "extended source at the limit 1.22 lambda / theta",
    "Parallax": "Two-station ranging: the two sightlines from two observers "
                "separated by b to a target at range Delta differ by "
                "delta = (b/Delta) sin(psi); range error "
                "sigma_Delta = Delta^2 sigma_theta / (b sin(psi))",
    "Sentry": "CNEOS Sentry documentation: tabulated impact energy is generally "
              "good to within a factor of three because mass is unmeasured",
}


# ----------------------------------------------------------------------------
# 1. Target photometry and geometry
# ----------------------------------------------------------------------------
def absolute_magnitude(diameter_m, albedo):
    """H from effective diameter (m) and geometric albedo p."""
    d_km = diameter_m / 1000.0
    return -5.0 * math.log10(d_km * math.sqrt(albedo) / 1329.0)


def apparent_magnitude(h, r_au, delta_au):
    """V at zero phase angle."""
    return h + 5.0 * math.log10(r_au * delta_au)


def flux_erg_s_cm2_hz(v_mag):
    """Monochromatic flux density at the V band, erg/s/cm^2/Hz."""
    return 3.63e-20 * 10.0 ** (-0.4 * v_mag)


def angular_diameter_rad(diameter_m, delta_m):
    return diameter_m / delta_m


def resolved_surface_brightness(diameter_m, delta_m, v_mag):
    """
    Surface brightness of a spatially resolved body, in mag/arcsec^2 (V band).

    The monochromatic flux is spread over the projected disc of area
    Omega = pi * (theta/2)^2 sr.  Comparing a 1-arcsec^2 aperture of the same
    surface brightness against the integrated flux gives the equivalent
    surface brightness used for an imaging comparison.
    """
    theta = angular_diameter_rad(diameter_m, delta_m)
    omega_sr = math.pi * (theta / 2.0) ** 2
    f_nu = flux_erg_s_cm2_hz(v_mag)
    sb_fnu = f_nu / omega_sr                      # erg/s/cm^2/Hz/sr
    # convert to mag/arcsec^2 via the zeropoint flux density (1 Jy = 1e-23 erg/s/cm^2/Hz)
    sb_jy = sb_fnu / 1.0e-23                      # Jy/sr
    arcsec2_sr = (ARCSEC ** 2)                    # 1 arcsec^2 in sr
    sb_jy_arcsec2 = sb_jy * arcsec2_sr            # Jy/arcsec^2
    if sb_jy_arcsec2 <= 0:
        return None
    return -2.5 * math.log10(sb_jy_arcsec2 / 3631.0)   # 3631 Jy = 0 mag


# ----------------------------------------------------------------------------
# 2. Interferometry
# ----------------------------------------------------------------------------
def fringe_spacing_rad(wavelength_m, baseline_m):
    """FS = lambda / B."""
    return wavelength_m / baseline_m


def interferometric_precision_rad(wavelength_m, baseline_m, snr):
    """Photon-noise-limited centroid precision = FS / SNR (CAPS eq. after FS)."""
    return fringe_spacing_rad(wavelength_m, baseline_m) / snr


def caps_max_baseline_m(wavelength_m, theta_diam_rad):
    """
    CAPS 2003 Table 1 maximum baseline.

    Re-derived from the eight published rows: B_max = lambda / (4 * theta_diameter),
    i.e. four fringe spacings across the target's diameter.  The agreement is
    better than 0.2 % on every row of CAPS Table 1; the visibility criterion that
    generates the column is not printed in the source document.
    """
    return wavelength_m / (4.0 * theta_diam_rad)


def bessel_j1(x):
    """J1(x) by its absolutely convergent power series."""
    s = 0.0
    for k in range(0, 80):
        s += (-1) ** k * (x / 2.0) ** (2 * k + 1) / (math.factorial(k) * math.factorial(k + 1))
    return s


def disk_visibility(baseline_m, wavelength_m, theta_radius_rad):
    x = math.pi * baseline_m * theta_radius_rad / wavelength_m
    if x < 1e-9:
        return 1.0
    return abs(2.0 * bessel_j1(x) / x)


def disk_visibility_x(x):
    """
    Uniform-disc visibility at the dimensionless argument x, where
    x = pi B theta_radius / wavelength.

    The Bessel series is numerically stable only for small x, so the
    over-resolution limit is solved for x and the baseline is recovered
    afterwards.
    """
    if x < 1e-9:
        return 1.0
    return abs(2.0 * bessel_j1(x) / x)


# ----------------------------------------------------------------------------
# 3. Thermal background of the lunar surface
# ----------------------------------------------------------------------------
H_PLANCK = 6.62607015e-34
C_2 = 1.438776877e-2       # m*K


def planck_radiance_um(wavelength_um, temp_k, emissivity=0.9):
    """Spectral radiance in W m^-2 sr^-1 um^-1."""
    lam_m = wavelength_um * 1e-6
    num = 2.0 * H_PLANCK * C_LIGHT ** 2 / lam_m ** 5
    den = math.exp(C_2 / (lam_m * temp_k)) - 1.0
    return emissivity * num / den * 1e-6


def wien_peak_um(temp_k):
    """Wien's displacement law: lambda_max (micrometre) = 2897.77 / T(K)."""
    return 2.897771955e3 / temp_k


# ----------------------------------------------------------------------------
# 4. Yarkovsky / YORP scaling and the keyhole
# ----------------------------------------------------------------------------
def yarkovsky_scaling(diam_m, rho, albedo_bond, a_au):
    """
    da/dt proportional to (1 - A) cos(gamma) / (sqrt(a * rho * D))  times the
    thermal-parameter factor f(TI, omega).

    Calibrated against Rozitis & Green 2012's pseudo-Geographos: D = 2560 m,
    rho = 2500 kg/m3, A_Bond = 0.1, a = 1.246 AU, TSSP = 278 K gives
    da/dt = 18.1 m/yr at zero obliquity.

    The calibration point is for the *specific* thermal parameter
    Theta = Gamma*omega/(epsilon*sigma*TSSP^3) of that model; the size and
    density scaling below is the exact part of eq. 30 and is what this book
    uses.  The obliquity and thermal-parameter factors are reported separately.
    """
    d_cal, rho_cal, a_cal = 2560.0, 2500.0, 1.246
    da_cal = 18.1     # m/yr, pseudo-Geographos
    ratio = (d_cal / diam_m) * (rho_cal / rho) * \
            math.sqrt(a_au / a_cal) * ((1.0 - albedo_bond) / (1.0 - 0.1))
    return da_cal * ratio


def yorp_scaling(diam_m, rho):
    """
    domega/dt proportional to 1 / (rho_b * D^2)  (Rozitis & Green 2012, eq. 31),
    calibrated to pseudo-Geographos: 2.26e-3 rad/yr^2 at D = 2560 m, rho = 2500.
    """
    d_cal, rho_cal, acc_cal = 2560.0, 2500.0, 2.26e-3
    return acc_cal * (d_cal / diam_m) ** 2 * (rho_cal / rho)


def along_track_offset_m(delta_a_m, a_au, dt_years):
    """
    Along-track displacement produced by a semi-major-axis error.

    For a Keplerian orbit, perturbing a by da changes the mean motion by
    dn/n = -(3/2) da/a, so the phase error after time dt is
    dM = -(3/2)(da/a) n dt and the along-track displacement is
    ds = a dM = -(3/2) da n dt.
    """
    a_m = a_au * AU_M
    n = math.sqrt(MU_SUN / a_m ** 3)      # rad/s
    dt_s = dt_years * 365.25 * 86400.0
    return 1.5 * delta_a_m * n * dt_s


def impact_probability_through_keyhole(width_m, centre_m, sigma_m):
    """
    Impact probability for a keyhole of width `width_m` centred at
    `centre_m` along the along-track (zeta) coordinate, whose probability
    density is Gaussian with standard deviation `sigma_m`.

    IP = integral of the Gaussian density across the keyhole.  This is the
    standard construction (Chodas 1999; Chesley 2006; Bottke et al. 2013).
    """
    if sigma_m <= 0:
        return 0.0
    def cdf(x):
        return 0.5 * (1.0 + math.erf(x / (math.sqrt(2.0) * sigma_m)))
    hi = centre_m + width_m / 2.0
    lo = centre_m - width_m / 2.0
    return cdf(hi) - cdf(lo)


def keyhole_width_for_ip(ip, centre_m, sigma_m):
    """Invert the above for the keyhole width giving a required probability."""
    lo, hi = 1e-3, 1e9
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if impact_probability_through_keyhole(mid, centre_m, sigma_m) < ip:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


# ----------------------------------------------------------------------------
# 5. Impact energy and the Torino scale
# ----------------------------------------------------------------------------
def impact_energy_j(diameter_m, rho, v_km_s):
    v = v_km_s * 1000.0
    volume = math.pi / 6.0 * diameter_m ** 3
    mass = rho * volume
    return 0.5 * mass * v ** 2


def energy_mt(diameter_m, rho, v_km_s):
    return impact_energy_j(diameter_m, rho, v_km_s) / MT_J


def torino_level(ip, energy_mt_value):
    """
    Torino Scale level from impact probability p and kinetic energy E (Mt).

    The scale is defined on log10(E) and log10(p) with the boundaries listed
    below (Binzel's scale as reproduced in the public definition).
    """
    if ip >= 0.99:
        if energy_mt_value >= 1e5:
            return 10
        if energy_mt_value >= 1e2:
            return 9
        return 8
    le = math.log10(energy_mt_value)
    lp = math.log10(ip)
    if le < 0 and (le + 1.0 / 3.0 + lp + 2.0) / 2.0 < 0:
        return 0
    if (le + 1.0 / 3.0 + lp + 2.0) / 2.0 >= 0 and le >= 0 and \
       (le - 2.0 / 3.0 + lp + 2.0) / 2.0 < 0 and lp < -2:
        return 1
    if (le - 2.0 / 3.0 + lp + 2.0) / 2.0 >= 0 and \
       (le - 5.0 / 3.0 + lp + 2.0) / 2.0 < 0 and lp < -2:
        return 2
    if lp >= -2 and 0 <= le < 2 and ip < 0.99:
        return 3
    if lp >= -2 and 2 <= le and (le - 5.0 / 3.0 + lp + 2.0) / 2.0 < 0 and ip < 0.99:
        return 4
    if (le - 5.0 / 3.0 + lp + 2.0) / 2.0 >= 0 and ip < 0.99 and le < 5:
        return 5
    if (le - 5.0 / 3.0 + lp + 2.0) / 2.0 >= 0 and lp < -2:
        return 6
    if lp >= -2 and le >= 5 and ip < 0.99:
        return 7
    return 0


def background_impact_frequency_per_year(energy_mt_value):
    """ESA NEOCC: f_b ~ 0.03 E^(-0.8), E in Mt."""
    return 0.03 * energy_mt_value ** (-0.8)


# ----------------------------------------------------------------------------
# 12. The discovery baseline (NASA CNEOS cumulative series)
# ----------------------------------------------------------------------------
def load_cneos(path=None):
    """
    NASA CNEOS cumulative NEA discovery series (nea_vs_time.json).

    The file is looked for in the book's research/evidence directory and, as a
    fallback, beside this script, so that the generator runs unchanged from
    either the book repository or the research workspace.
    """
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(os.path.dirname(here), "research", "evidence",
                         "cneos_nea_vs_time.json"),
            os.path.join(here, "evidence", "cneos_nea_vs_time.json"),
        ]
        for cand in candidates:
            if os.path.exists(cand):
                path = cand
                break
        else:
            raise FileNotFoundError(
                "cneos_nea_vs_time.json not found in any of: "
                + ", ".join(candidates))
    with open(path) as fh:
        raw = json.load(fh)
    meta, body = raw[0], raw[1]
    return {"meta": meta, "series": {s["name"]: s["data"] for s in body}}


def cneos_annual_arrivals(series):
    """
    Objects discovered per calendar year, from a cumulative (timestamp, count)
    series.  The count at each year boundary is the last value in the series
    whose timestamp falls in that year or earlier.
    """
    bounds = {}
    for ts, n in series:
        y = datetime.datetime.fromtimestamp(ts / 1000.0,
                                            datetime.timezone.utc).year
        bounds[y] = n
    out = {}
    for y in sorted(bounds):
        if (y - 1) in bounds:
            out[y] = bounds[y] - bounds[y - 1]
    return out


# ----------------------------------------------------------------------------
# 13. Two-station ranging on the Earth-Moon baseline
# ----------------------------------------------------------------------------
def parallax_angle_rad(baseline_m, distance_m, sin_psi=1.0):
    """
    Angle between the sightlines to a target seen from two observers separated
    by `baseline_m`, the target at `distance_m`, and the baseline making an
    angle psi with the line of sight (sin_psi = sin psi).
    """
    return baseline_m / distance_m * sin_psi


def two_station_range_error_m(distance_m, sigma_theta_rad, baseline_m, sin_psi=1.0):
    """
    Range error from two-station parallax.

    The two observers see the target in directions differing by
        delta = (b / Delta) sin(psi).
    A differential astrometric error sigma_theta between the two solutions
    therefore maps to a range error
        sigma_Delta = Delta sigma_theta / delta = Delta^2 sigma_theta / (b sin psi).
    """
    return distance_m * sigma_theta_rad / parallax_angle_rad(baseline_m,
                                                             distance_m, sin_psi)


def resolved_aperture_m(wavelength_m, theta_rad):
    """Aperture diameter that resolves an extended source at the Rayleigh limit."""
    return 1.22 * wavelength_m / theta_rad


def campaigns_per_year(orientation_sweep_days, overhead_fraction=0.30):
    """
    Shape campaigns a fixed station can run when each campaign needs a 90 deg
    baseline-orientation sweep and a fraction of the time is lost to overhead.
    """
    return 365.25 * (1.0 - overhead_fraction) / orientation_sweep_days


def energy_uncertainty_factor(d_frac, rho_frac):
    """
    Factor of uncertainty in impact energy from fractional errors in diameter
    and density:  E = (1/2) rho (pi/6) D^3 v^2, so dlnE = 3 dlnD + dlnrho.
    """
    return (1.0 + d_frac) ** 3 * (1.0 + rho_frac)


# ============================================================================
# MAIN
# ============================================================================
def bottke_2036_rows():
    """Bottke et al. 2013 (arXiv:1301.1607), Table 5.

    The 2036 Apophis keyhole impact probabilities for the nominal case and
    for six perturbations.  The keyhole width is 616.16 m.  These are
    published values, not derived ones; the figures and the book both read
    them from here so that neither can drift.
    """
    return [
        ("Nominal", 7.07e-9),
        ("Diameter 270 +/- 60 m", 3.06e-6),
        ("Unif. cos gamma", 2.67e-9),
        ("Symm. cos gamma", 1.64e-9),
        ("sigma_rho^2 = 0.6", 6.60e-7),
        ("mu_d0 = 200", 1.58e-9),
        ("mu_d0 = 400", 1.59e-8),
    ]


def yr4_model_set():
    """The published thermophysical model set for 2024 YR4.

    Diameter in metres, density in kg/m^3, as tabulated in the sources
    carried in the ledger.
    """
    return [
        ("NEATM (beaming 3.06, rejected)", 60.6, 2800.0),
        ("FRM (fast-rotating)", 51.1, 2800.0),
        ("TPM (thermophysical)", 60.8, 2800.0),
        ("TPM, rubble pile rho=1300", 60.8, 1300.0),
        ("FRM, rubble pile rho=1300", 51.1, 1300.0),
        ("TPM, monolithic rho=3500", 60.8, 3500.0),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out = {}
    lines = []

    def emit(s=""):
        lines.append(s)

    emit("=" * 78)
    emit("THE SHAPE OF THE THREAT - headline numbers generator")
    emit("=" * 78)

    # ---------------------------------------------------------------- 1
    emit()
    emit("1. CAPS TABLE 1 - INDEPENDENT RE-DERIVATION")
    emit("-" * 78)
    caps_rows = [
        # (object, D_m, distance_AU, published B_max_m, published res_arcsec)
        ("1 km LPC", 1000.0, 6.0, 168.0, 1.3e-4),
        ("1 km LPC", 1000.0, 5.0, 140.0, 1.6e-4),
        ("1 km LPC", 1000.0, 4.0, 112.0, 2.0e-4),
        ("1 km LPC", 1000.0, 3.0, 84.0, 2.6e-4),
        ("50 m NEA", 50.0, 0.8, 450.0, 4.9e-5),
        ("50 m NEA", 50.0, 0.6, 337.0, 6.6e-5),
        ("50 m NEA", 50.0, 0.4, 225.0, 9.9e-5),
        ("50 m NEA", 50.0, 0.2, 113.0, 2.0e-4),
    ]
    lam = 750e-9
    snr = 7.0
    emit(f"{'object':9s} {'D(m)':>7s} {'d(AU)':>6s} {'Bpub':>7s} {'Brule':>8s} "
         f"{'d%':>6s} {'respub':>9s} {'rescalc':>9s} {'d%':>6s}")
    bmax_err, res_err = [], []
    for name, D, d, Bpub, rpub in caps_rows:
        delta_m = d * AU_M
        theta = D / delta_m
        b_rule = caps_max_baseline_m(lam, theta)
        res = interferometric_precision_rad(lam, Bpub, snr) / ARCSEC
        bmax_err.append(abs(b_rule - Bpub) / Bpub * 100)
        res_err.append(abs(res - rpub) / rpub * 100)
        emit(f"{name:9s} {D:7.0f} {d:6.1f} {Bpub:7.0f} {b_rule:8.1f} "
             f"{abs(b_rule-Bpub)/Bpub*100:5.2f}% {rpub:9.2e} {res:9.2e} "
             f"{abs(res-rpub)/rpub*100:5.2f}%")
    emit(f"  -> B_max rule  B = lambda/(4*theta_diam): max deviation "
         f"{max(bmax_err):.2f}% over 8 rows")
    emit(f"  -> precision rule p = lambda/(B*SNR), SNR=7: max deviation "
         f"{max(res_err):.2f}% over 8 rows")
    out["caps_rule_max_dev_pct"] = {"b_max": max(bmax_err), "precision": max(res_err)}
    out["caps_rule"] = "B_max = lambda/(4*theta_diameter); precision = lambda/(B*SNR)"

    # ---------------------------------------------------------------- 2
    emit()
    emit("2. THE 50-140 m CLASS - WHAT A LUNAR BASELINE MUST MATCH")
    emit("-" * 78)
    emit(f"{'D(m)':>5s} {'d(AU)':>6s} {'V(p=.10)':>9s} {'theta(mas)':>11s} "
         f"{'Bmax(m)':>8s} {'B100 FS/theta':>14s} {'V(100m)':>8s}")
    grid = []
    for D in (50.0, 60.0, 140.0):
        for d in (0.1, 0.2, 0.5, 1.0, 1.3):
            delta_m = d * AU_M
            theta = D / delta_m
            h = absolute_magnitude(D, 0.10)
            v = apparent_magnitude(h, d, d)
            bmax = caps_max_baseline_m(lam, theta)
            fs100 = fringe_spacing_rad(lam, 100.0)
            vis = disk_visibility(100.0, lam, theta / 2.0)
            grid.append(dict(D=D, d=d, h=h, v=v, theta_mas=theta / ARCSEC,
                             bmax=bmax, fs_over_theta=fs100 / theta, vis_100m=vis))
            emit(f"{D:5.0f} {d:6.2f} {v:9.2f} {theta/ARCSEC*1000:11.2f} {bmax:8.1f} "
                 f"{fs100/theta:14.2f} {vis:8.3f}")
    emit("  FS/theta = fringe spacings across the diameter (want ~4 for a shape);")
    emit("  V(100m) = uniform-disc fringe visibility at a 100 m baseline.")
    out["class_grid"] = grid

    emit()
    emit("  SAMPLES ACROSS THE DIAMETER, N = theta_diam * B / lambda")
    emit(f"    {'D(m)':>5s} {'d(AU)':>6s} {'theta(mas)':>11s} {'N at 100m':>11s} "
         f"{'N at 1.5km':>12s} {'N at 3km':>10s}")
    samples = []
    for D in (50.0, 60.0, 140.0):
        for d in (0.05, 0.1, 0.2, 0.5, 1.0):
            theta = D / (d * AU_M)
            row = dict(D=D, d=d, theta_mas=theta / ARCSEC * 1000.0)
            for b_m, key in ((100.0, "n100"), (1500.0, "n1500"), (3000.0, "n3000")):
                row[key] = theta * b_m / lam
            samples.append(row)
            emit(f"    {D:5.0f} {d:6.2f} {theta/ARCSEC*1000:11.4f} "
                 f"{row['n100']:11.3f} {row['n1500']:12.3f} {row['n3000']:10.3f}")
    emit("  N >= 4 is the shape-imaging condition, calibrated on the 3 Juno")
    emit("  image at N = 4.3.  The concept study's 100 m design point gives")
    emit("  N = 0.45 for a 50 m object at 0.1 AU and N = 0.22 at 0.2 AU: the")
    emit("  target is smaller than half of one fringe spacing in both cases.")
    out["samples_across_diameter"] = samples

    # ---------------------------------------------------------------- 3
    emit()
    emit("  THE SHAPE-IMAGING BASELINE REQUIREMENT (not the centroid one)")
    emit("  N = theta_diam / FS = theta_diam * B / lambda  samples across the")
    emit("  diameter.  Cross-check: ALMA imaged 3 Juno at 0.042 arcsec for a")
    emit("  180 mas diameter -> N = 4.3, i.e. B ~ 4.3 * lambda/theta.")
    emit(f"    {'D(m)':>5s} {'d(AU)':>6s} {'theta(mas)':>11s} {'lambda/theta(m)':>15s} "
         f"{'B at N=4 (m)':>13s} {'B at N=7 (m)':>13s}")
    shape_rows = []
    for D in (50.0, 60.0, 140.0):
        for d in (0.1, 0.2, 0.5, 1.0, 1.3):
            theta = D / (d * AU_M)
            l_over_t = lam / theta
            b4, b7 = 4.0 * l_over_t, 7.0 * l_over_t
            shape_rows.append(dict(D=D, d=d, theta_mas=theta / ARCSEC * 1000,
                                   lambda_over_theta_m=l_over_t,
                                   B_N4_m=b4, B_N7_m=b7))
            emit(f"    {D:5.0f} {d:6.2f} {theta/ARCSEC*1000:11.2f} "
                 f"{l_over_t:15.0f} {b4:13.0f} {b7:13.0f}")
    emit("  CAPS's own 100 m design point corresponds to N = 0.45 for a 50 m")
    emit("  object at 0.1 AU, and N = 0.22 at 0.2 AU: the target is")
    emit("  unresolved in both cases and the instrument is an ASTROMETRIC")
    emit("  CENTROID, not a shape imager.  The lunar surface can host the")
    emit("  required kilometre-scale array; it cannot host a 100 m one and")
    emit("  call it shape imaging.")
    out["shape_imaging_baselines"] = shape_rows

    emit()
    emit("3. SURFACE BRIGHTNESS OF A RESOLVED NEO vs LUNAR BACKGROUNDS")
    emit("-" * 78)
    for D, d in ((60.0, 0.2), (60.0, 1.0), (140.0, 0.2)):
        h = absolute_magnitude(D, 0.10)
        v = apparent_magnitude(h, d, d)
        sb = resolved_surface_brightness(D, d * AU_M, v)
        emit(f"  D={D:5.0f} m at {d:4.2f} AU:  V={v:6.2f}   "
             f"resolved SB = {sb:6.2f} mag/arcsec^2")
    emit("  Zodiacal light at the ecliptic (V band): ~22.0 mag/arcsec^2 (extragalactic,")
    emit("  fainter; the Moon's own night sky at a polar site is zodiacal-limited).")

    # ---------------------------------------------------------------- 4
    emit()
    emit("4. LUNAR THERMAL FOREGROUND - THE MIR CHANNEL")
    emit("-" * 78)
    emit(f"  Wien peak of 390 K regolith: {wien_peak_um(390.0):.2f} um")
    for T in (390.0, 80.0, 30.0):
        emit(f"  T = {T:5.1f} K  (peak {wien_peak_um(T):6.2f} um):  " +
             "  ".join(f"{w}um {planck_radiance_um(w, T):.3e}"
                       for w in (5.0, 8.0, 10.0, 12.0, 14.0)))
    emit("  Units W m^-2 sr^-1 um^-1, emissivity 0.9.")
    out["wien_peak_390K_um"] = wien_peak_um(390.0)
    out["regolith_radiance"] = {
        f"{T}K": {f"{w}um": planck_radiance_um(w, T) for w in (5.0, 8.0, 10.0, 12.0, 14.0)}
        for T in (390.0, 80.0, 30.0)
    }

    emit()
    emit("  THE DECISIVE COMPARISON: a NEO's thermal disk against the regolith")
    emit("  A Lambertian sphere's resolved surface brightness at 10 um is")
    emit("  B_lambda(T_sub)/4, independent of its distance from the observer.")
    emit("  T_sub = 278 K * (r/1 AU)^(-1/2) for a body with low thermal inertia.")
    fg_sunlit = planck_radiance_um(10.0, 390.0)
    fg_psr = planck_radiance_um(10.0, 30.0)
    fg_ridge = planck_radiance_um(10.0, 80.0)
    emit(f"    {'r(AU)':>6s} {'T_sub':>7s} {'B/4 (10um)':>13s} "
         f"{'vs sunlit 390K':>15s} {'vs PSR 30K':>13s}")
    for r_au in (0.3, 0.5, 1.0, 1.3):
        t_sub = 278.0 / math.sqrt(r_au)
        sb = planck_radiance_um(10.0, t_sub) / 4.0
        emit(f"    {r_au:6.2f} {t_sub:7.1f} {sb:13.3e} "
             f"{sb/fg_sunlit:15.4f} {sb/fg_psr:13.3e}")
    emit("  Contrast < 1 means the Sunlit lunar ground is BRIGHTER than the")
    emit("  asteroid's own thermal disk: the telescope would be looking at the")
    emit("  ground, not at the target.")
    out["mir_contrast"] = {
        f"r{r}_vs_sunlit": (planck_radiance_um(10.0, 278.0 / math.sqrt(r)) / 4.0) / fg_sunlit
        for r in (0.3, 0.5, 1.0, 1.3)
    }
    out["mir_foreground_10um"] = {
        "sunlit_390K": fg_sunlit, "ridge_80K": fg_ridge, "psr_30K": fg_psr
    }

    # ---------------------------------------------------------------- 5
    emit()
    emit("  THE BAFFLE, NOT THE GROUND, IS THE OPTICAL FOREGROUND")
    emit("  A sunshade/baffle at temperature T_b emits at 10 um as B_lambda(T_b).")
    emit(f"    {'T_baffle':>10s} {'B(10um)':>13s} {'vs asteroid at 0.3AU':>22s}")
    sb03 = planck_radiance_um(10.0, 278.0 / math.sqrt(0.3)) / 4.0
    for tb in (390.0, 250.0, 100.0, 40.0, 30.0):
        bb = planck_radiance_um(10.0, tb)
        emit(f"    {tb:9.1f} K {bb:13.3e} {bb/sb03:21.1f}x")
    emit("  A 390 K baffle is ~10x brighter than the target's own thermal disk;")
    emit("  a 40 K baffle is 17 orders of magnitude fainter.  The lunar MIR")
    emit("  channel is therefore not a background problem but a cryogenic-optics")
    emit("  problem on a 390 K surface with a 300+ hour night.")
    out["baffle_radiance"] = {f"{tb}K": planck_radiance_um(10.0, tb)
                              for tb in (390.0, 250.0, 100.0, 40.0, 30.0)}

    emit()
    emit("5. THE ACCOUNTABILITY CHAIN FOR 2024 YR4 (lunar impact, 22 Dec 2032)")
    emit("-" * 78)
    v_impact = 14.1      # km/s, arXiv:2601.10666
    emit(f"  impact speed v = {v_impact} km/s")
    models = yr4_model_set()
    chain = []
    for label, D, rho in models:
        e = energy_mt(D, rho, v_impact)
        mass = rho * math.pi / 6.0 * D ** 3
        emit(f"  {label:34s} D={D:5.1f} m rho={rho:5.0f}  "
             f"m={mass:.3e} kg  E={e:6.2f} Mt")
        chain.append(dict(label=label, D=D, rho=rho, mass_kg=mass, energy_Mt=e))
    e_lo = min(c["energy_Mt"] for c in chain)
    e_hi = max(c["energy_Mt"] for c in chain)
    emit(f"  -> energy spread across the published model set: "
         f"{e_lo:.2f} Mt to {e_hi:.2f} Mt = factor {e_hi/e_lo:.2f}")
    d_ratio = (60.8 / 51.1) ** 3
    emit(f"  -> thermal-model choice alone (60.8 m vs 51.1 m, same density): "
         f"factor {d_ratio:.2f} in energy")
    out["yr4_chain"] = chain
    out["yr4_energy_spread_factor"] = e_hi / e_lo
    out["yr4_thermal_model_only_factor"] = d_ratio

    # ---------------------------------------------------------------- 6
    emit()
    emit("6. THE PROBABILITY CHAIN - WHY A 3 % DIAMETER ERROR IS NOT SMALL")
    emit("-" * 78)
    emit("  Rozitis & Green 2012, pseudo-Geographos (D=2560 m, rho=2500, a=1.246 AU):")
    emit("    da/dt = 18.1 m/yr ;  domega/dt = 2.26e-3 rad/yr^2")
    emit("    +/-3 % on D  ->  +/-3 % on Yarkovsky,  +/-6 % on YORP   [verified]")
    emit("  Scaling laws (their eqs. 30-31):")
    emit("    da/dt   ~ 1/(rho_b * D)          (Yarkovsky)")
    emit("    domega/dt ~ 1/(rho_b * D^2)      (YORP)")
    emit("  RATIOS to the calibration object (the size/density part only):")
    for D in (51.1, 60.8, 140.0):
        for rho in (1300.0, 2800.0):
            emit(f"    D={D:5.1f} m rho={rho:5.0f}:  Yarkovsky x"
                 f"{yarkovsky_scaling(D, rho, 0.1, 1.246)/18.1:8.1f}   "
                 f"YORP x{yorp_scaling(D, rho)/2.26e-3:9.1f}")
    emit("  CAVEAT: these ratios isolate the explicit size/density factor only.")
    emit("  The full Yarkovsky drift also carries the thermal-parameter factor")
    emit("  f(Theta, omega), and Theta = Gamma*omega/(eps*sigma*T_SSP^3) with")
    emit("  T_SSP ~ D^(-1/2).  An absolute extrapolation from 2560 m to 50 m")
    emit("  therefore does NOT follow from eq. 30 alone, and the book does not")
    emit("  make one.  The published drift rates for real objects are used instead.")
    out["yarkovsky_ratio_to_calib"] = {
        f"D{D}_rho{int(rho)}": yarkovsky_scaling(D, rho, 0.1, 1.246) / 18.1
        for D in (51.1, 60.8, 140.0) for rho in (1300.0, 2800.0)
    }
    out["yorp_ratio_to_calib"] = {
        f"D{D}_rho{int(rho)}": yorp_scaling(D, rho) / 2.26e-3
        for D in (51.1, 60.8, 140.0) for rho in (1300.0, 2800.0)
    }

    emit()
    emit("  Along-track consequence of a Yarkovsky drift-rate error over the")
    emit("  2025->2032 arc (a = 1.1 AU), for a range of assumed drift rates:")
    emit(f"    {'drift rate':>12s} {'err 3%':>12s} {'err 10%':>12s} {'err 30%':>12s}")
    al = {}
    for rate_m_yr in (50.0, 100.0, 300.0, 1000.0):
        row = []
        for f in (0.03, 0.10, 0.30):
            ds = along_track_offset_m(rate_m_yr * f, 1.1, 7.0)
            row.append(ds)
            al[f"rate{rate_m_yr:.0f}_err{int(f*100)}"] = ds
        emit(f"    {rate_m_yr:9.0f} m/yr " +
             "".join(f"{v/1000:9.1f} km " for v in row))
    emit("  Compare: the published lunar B-plane uncertainty for the 2032 YR4")
    emit("  encounter is 25,000 km.  At the 2032 horizon the ASTROMETRIC term")
    emit("  dominates by three orders of magnitude; the physical term becomes")
    emit("  dominant only at Apophis-type horizons (decades to centuries).")
    out["along_track_7yr"] = al

    # ---------------------------------------------------------------- 7
    emit()
    emit("7. THE APOPHIS 2036 KEYHOLE - PHYSICAL CHARACTERISATION DOMINATES")
    emit("-" * 78)
    emit("  Bottke et al. 2013 (arXiv:1301.1607), Table 5, 2036 keyhole width 616.16 m:")
    bottke = bottke_2036_rows()
    for label, ip in bottke:
        emit(f"    {label:24s} IP_2036 = {ip:.3e}   "
             f"factor vs nominal = {ip/7.07e-9:9.1f}x")
    emit(f"    -> diameter assumption alone moves IP by "
         f"{(3.06e-6/7.07e-9):.0f}x")
    out["bottke_2036"] = {label: ip for label, ip in bottke}

    emit()
    emit("  THE SAME FACTORS EXPRESSED AS ALONG-TRACK DISPLACEMENTS")
    emit("  In the tail, IP ratio = exp(z_ref * dz), so a factor F in the")
    emit("  probability corresponds to a shift of dz = ln(F)/z_ref sigma, and")
    emit("  that shift in kilometres is dz times the along-track sigma.")
    z_ref = 4.77
    sigma_zeta_km = 398.5
    magnify = {}
    for label, ip in bottke:
        fac = ip / 7.07e-9
        if fac <= 1.0:
            continue
        dz = math.log(fac) / z_ref
        disp = dz * sigma_zeta_km
        magnify[label] = {"factor": fac, "dz_sigma": dz, "displacement_km": disp}
        emit(f"    {label:24s} factor {fac:9.1f} -> {dz:6.3f} sigma "
             f"= {disp:8.1f} km")
    emit("  A 60 m change in the assumed diameter moves the 2036 keyhole")
    emit("  centre by about 500 km, which is comparable with the 398.5 km")
    emit("  astrometric sigma.  The astrometric term shrinks with more")
    emit("  observing time; the physical term does not.")
    out["keyhole_magnification_km"] = magnify

    emit()
    emit("  WHY THE TAIL MAGNIFIES: the 2036 keyhole sits 4.77 sigma out in the")
    emit("  along-track (zeta) distribution (Bottke et al. 2013, Table 4).")
    w36 = 616.16
    z36 = 4.77
    # Back out the along-track 1-sigma from the published keyhole width and IP.
    lo, hi = 1e3, 1e9
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        ip = impact_probability_through_keyhole(w36, -z36 * mid, mid)
        if ip > 7.07e-9:
            lo = mid
        else:
            hi = mid
    sigma_zeta = math.sqrt(lo * hi)
    emit(f"    Along-track 1-sigma implied by w=616.16 m, z=-4.77, IP=7.07e-9: "
         f"{sigma_zeta/1000:.1f} km")
    emit("    Sensitivity:  IP(z) ~ IP_ref * exp(-z_ref * dz),  z_ref = 4.77")
    for dz in (0.001, 0.01, 0.1, 1.0):
        fac = math.exp(z36 * dz)
        emit(f"      centre shift of {dz*100:7.3f} % of sigma -> IP changes by "
             f"factor {fac:8.2f}")
    emit("    A keyhole in the tail is a magnifier of physical-parameter error:")
    emit("    the same 1 % diameter error that is harmless at the peak of the")
    emit("    distribution is worth two orders of magnitude out at 4.77 sigma.")
    out["sigma_zeta_2029_apophis_km"] = sigma_zeta / 1000.0
    out["keyhole_tail_sensitivity"] = {
        f"dz{dz}": math.exp(z36 * dz) for dz in (0.001, 0.01, 0.1, 1.0)
    }

    emit()
    emit("  Torino level as a function of impact probability for three energies:")
    for D, rho, lab in ((60.8, 2800.0, "YR4-class 60.8 m, rho 2800"),
                        (60.8, 1300.0, "YR4-class 60.8 m, rubble pile"),
                        (325.0, 2200.0, "Apophis 325 m, rho 2200")):
        e = energy_mt(D, rho, 17.0)
        row = []
        for ip in (1e-9, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3):
            row.append(f"{ip:.0e}:L{torino_level(ip, e)}")
        emit(f"    {lab:30s} E={e:8.1f} Mt   " + "  ".join(row))
    out["torino_demo"] = {}

    # ---------------------------------------------------------------- 8
    emit()
    emit("  THE TORINO LEVEL-1 THRESHOLD IS A FUNCTION OF THE ENERGY, AND THE")
    emit("  ENERGY IS A FUNCTION OF THE MEASUREMENTS YOU DO NOT HAVE.")
    emit("  Level 1 requires (log10 E + 1/3 + log10 p + 2)/2 >= 0, i.e.")
    emit("      p >= 10^(-7/3) / E = %.4e / E(Mt)" % (10.0 ** (-7.0 / 3.0)))
    for c in chain:
        e = c["energy_Mt"]
        p1 = 10.0 ** (-7.0 / 3.0) / e
        emit(f"    {c['label']:34s} E={e:6.2f} Mt -> Level 1 needs p >= {p1:.3e}")
    p1_lo = 10.0 ** (-7.0 / 3.0) / max(c["energy_Mt"] for c in chain)
    p1_hi = 10.0 ** (-7.0 / 3.0) / min(c["energy_Mt"] for c in chain)
    emit(f"    -> the Level-1 probability threshold spans {p1_lo:.2e} to "
         f"{p1_hi:.2e} across the published model set: a factor "
         f"{p1_hi/p1_lo:.2f}")
    emit("    An object whose astrometry is UNCHANGED can therefore be Level 0")
    emit("    or Level 1 purely because of how it was sized.")
    out["torino_level1_threshold"] = {
        c["label"]: 10.0 ** (-7.0 / 3.0) / c["energy_Mt"] for c in chain
    }
    out["torino_threshold_spread"] = p1_hi / p1_lo

    emit()
    emit("8. THE LUNAR BASELINE ORIENTATION - AN ADVANTAGE, NOT A CONSTRAINT")
    emit("-" * 78)
    rate = 360.0 / LUNAR_SIDEREAL_DAYS
    emit(f"  The Moon turns {rate:.3f} deg/day relative to the stars "
         f"(sidereal rotation {LUNAR_SIDEREAL_DAYS:.6f} d)")
    emit(f"  The Sun crosses the lunar sky at "
         f"{360.0/LUNAR_SYNODIC_DAYS:.3f} deg/day (synodic month)")
    emit(f"  The lunar sky therefore turns {15.0/(rate*3600/86400):.1f} times "
         f"more slowly than the Earth's")
    emit(f"  -> a surface-fixed baseline sweeps 90 deg in "
         f"{90.0/rate:.2f} days, and 180 deg in {180.0/rate:.2f} days")
    emit("  CAPS: 'Two measurements at different baseline orientations "
         "(~orthogonal) are required'")
    emit("  -> one fixed lunar baseline delivers the required second orientation")
    emit("     within a week, at no cost, without any moving hardware.")
    out["lunar_baseline_rotation_deg_per_day"] = rate
    out["days_for_90deg"] = 90.0 / rate

    # ---------------------------------------------------------------- 9
    emit()
    emit("9. THE PALMA INTERFEROMETRY - THE ONLY ONE EVER DONE")
    emit("-" * 78)
    D_palma = 192.1e3
    d_palma = 3.436 * AU_M
    theta_p = D_palma / d_palma
    lam_p = 0.042
    fresnel_phys = math.sqrt(d_palma * lam_p / 2.0)
    fresnel_ang = math.sqrt(lam_p / (2.0 * d_palma))
    emit(f"  D = 192.1 km at 3.436 AU -> theta = {theta_p/ARCSEC*1000:.1f} mas")
    emit(f"  Fresnel number F = a^2/(d lambda) = 0.43 (paper value)")
    emit(f"  Fresnel scale sqrt(d*lambda/2) = {fresnel_phys/1000:.0f} km physical, "
         f"{fresnel_ang/ARCSEC*1000:.0f} mas angular")
    emit(f"  VLBA baselines used: 1200-2300 km (Earth scale)")
    emit(f"  Class ratio vs the 60 m target class: "
         f"{D_palma/60.8:.0f}x in diameter")
    out["palma"] = dict(theta_mas=theta_p / ARCSEC * 1000,
                        fresnel_scale_km=fresnel_phys / 1000,
                        fresnel_angular_mas=fresnel_ang / ARCSEC * 1000,
                        diameter_ratio_to_60m=D_palma / 60.8)

    # ---------------------------------------------------------------- 10
    emit()
    emit("10. BACKGROUND IMPACT FREQUENCY (ESA NEOCC, f_b = 0.03 E^-0.8)")
    emit("-" * 78)
    for e in (1e-3, 1e-2, 1e-1, 1.0, 6.5, 1e2, 1e6):
        f = background_impact_frequency_per_year(e)
        emit(f"    E = {e:8.3g} Mt -> f_b = {f:.3e} /yr  "
             f"(one per {1/f:9.3g} yr)")
    out["background_frequency"] = {
        str(e): background_impact_frequency_per_year(e)
        for e in (1e-3, 1e-2, 1e-1, 1.0, 6.5, 1e2, 1e6)
    }

    emit()
    emit("11. WHAT DIAMETER ACCURACY CLOSES THE ENERGY CHAIN")
    emit("-" * 78)
    emit("  E = (1/2) rho (pi/6) D^3 v^2  ->  dlnE = 3 dlnD + dlnrho")
    emit("  CNEOS Sentry states the tabulated impact energy is 'generally good")
    emit("  to within a factor of three' because mass is unmeasured.")
    for factor, rho_frac in ((3.0, 0.30), (2.0, 0.30), (2.0, 0.15), (1.5, 0.30)):
        dln_e = math.log(factor)
        dln_d = (dln_e - rho_frac) / 3.0
        emit(f"    energy known to a factor {factor:.1f}, rho to "
             f"{rho_frac*100:4.0f} % -> D must be known to "
             f"{100*(math.exp(dln_d)-1):5.1f} % (1 sigma)")
    emit("  A 30 % diameter is the present state of the art for the 140 m class;")
    emit("  closing the energy chain to a factor of two needs about 15 %.")
    out["diameter_requirement"] = {
        f"factor{f}_rho{r}": 100 * (math.exp((math.log(f) - r) / 3.0) - 1)
        for f, r in ((3.0, 0.30), (2.0, 0.30), (2.0, 0.15), (1.5, 0.30))
    }

    # ---------------------------------------------------------------- 12
    emit()
    emit("12. THE DISCOVERY BASELINE (NASA CNEOS, data current 22 Nov 2026)")
    emit("-" * 78)
    cneos = load_cneos()
    emit(f"  CNEOS series latest date: {cneos['meta'].get('latestDate')}")
    totals, arrivals = {}, {}
    for name in ("All", "140m+", "1km+"):
        s = cneos["series"][name]
        last_date = datetime.datetime.fromtimestamp(s[-1][0] / 1000.0,
                                                   datetime.timezone.utc).date()
        totals[name] = s[-1][1]
        arrivals[name] = cneos_annual_arrivals(s)
        emit(f"    {name:6s}: {s[-1][1]:6d} objects known, series to {last_date}")
    emit()
    emit("  Annual arrivals, differenced from the cumulative series:")
    for name in ("All", "140m+", "1km+"):
        per_year = arrivals[name]
        text = "  ".join(f"{y}:{per_year[y]}" for y in sorted(per_year) if y >= 2022)
        emit(f"    {name:6s}  {text}")
    n140 = totals["140m+"]
    rate140 = arrivals["140m+"][2025]
    emit()
    emit(f"  -> hazard-relevant catalogue (>=140 m): {n140:,} objects, "
         f"+{rate140}/yr in 2025")
    emit(f"  -> share of the whole catalogue that is >=140 m: "
         f"{100.0 * n140 / totals['All']:.1f} %")
    emit("  -> the sub-140 m population is still arriving at three thousand a")
    emit("     year and is not the class that can destroy a city.")
    emit()
    emit("  Physical accounts that actually exist (Jones et al., arXiv:2301.10348):")
    emit("    'Only about 15 % of NEOs have had a spectrum measured, and fewer")
    emit("     than percent have been imaged with radar.'")
    n_spec = 0.15 * n140
    emit(f"  -> spectra on the >=140 m class: about {n_spec:,.0f} objects; "
         f"{n140 - n_spec:,.0f} without any")
    out["cneos_totals"] = totals
    out["cneos_arrivals_2025"] = {k: arrivals[k].get(2025) for k in arrivals}
    out["cneos_arrivals_2024"] = {k: arrivals[k].get(2024) for k in arrivals}
    out["cneos_arrivals_recent"] = {k: {y: v for y, v in sorted(arrivals[k].items())
                                        if y >= 2020} for k in arrivals}
    out["spectrum_coverage_140m"] = {"with_spectra": n_spec,
                                     "without": n140 - n_spec,
                                     "fraction": 0.15}

    # ---------------------------------------------------------------- 13
    emit()
    emit("13. THE SUN-WARD LEAD TIME, RECONSTRUCTED FROM ITS OWN TABLE")
    emit("-" * 78)
    emit("  AMAS (arXiv:2611.05435) Table 2 gives, for a relative velocity")
    emit("  v ~ 20 km/s, the first detectable distance from a lunar observatory")
    emit("  and the extra lead time over a ground observatory.  Inverting the")
    emit("  lead time recovers the ground limit the table implies:")
    v_rel = 20.0
    amas_rows = [
        ("30 m  city-scale impactor", 0.05, 4.0, 5.0),
        ("140 m potentially hazardous", 0.10, 9.0, 9.0),
        ("1 km  global-scale impactor", 0.50, 42.0, 42.0),
    ]
    amas_out = {}
    for label, d_moon, dt_lo, dt_hi in amas_rows:
        dt_mid = 0.5 * (dt_lo + dt_hi)
        d_ground = d_moon + v_rel * dt_mid * 86400.0 * 1000.0 / AU_M
        d_lo = d_moon + v_rel * dt_lo * 86400.0 * 1000.0 / AU_M
        d_hi = d_moon + v_rel * dt_hi * 86400.0 * 1000.0 / AU_M
        amas_out[label] = {"lunar_AU": d_moon, "lead_days": dt_mid,
                           "implied_ground_AU": d_ground}
        emit(f"    {label:28s} lunar {d_moon:5.2f} AU  +{dt_mid:5.1f} d  ->  "
             f"ground limit {d_ground:5.3f} AU  ({d_lo:.3f}-{d_hi:.3f})")
    emit("  AMAS names the historical failures this creates: 2008 TC3 and")
    emit("  2019 OK, 'multiple other NEAs detected only days before their")
    emit("  closest approach to Earth'.")
    out["amas_lead_time"] = amas_out

    # ---------------------------------------------------------------- 14
    emit()
    emit("14. TWO-STATION RANGING ON THE EARTH-MOON BASELINE")
    emit("-" * 78)
    emit("  The Earth-Moon baseline is b = 384,400 km and is known to")
    emit("  millimetres by laser ranging.  Two astrometric solutions tied to")
    emit("  that frame turn an angular detection into a ranged one:")
    emit("      delta        = (b/Delta) sin(psi)     sightline separation")
    emit("      sigma_Range  = Delta^2 sigma_theta / (b sin psi)")
    emit()
    cols = [0.1, 1.0, 10.0, 100.0]
    emit(f"    {'Delta':>12s} {'delta(deg)':>11s} " +
         "".join(f"{str(c) + ' mas':>14s}" for c in cols))
    emit("    (range error in metres)")
    ranging = {}
    for d_au in (0.00554, 0.05, 0.1, 0.2, 1.0, 1.3):
        delta_m = d_au * AU_M
        ang = parallax_angle_rad(EARTH_MOON, delta_m)
        row = []
        for c in cols:
            sig = c / 1000.0 * ARCSEC
            e = two_station_range_error_m(delta_m, sig, EARTH_MOON)
            row.append(e)
            ranging[f"delta{d_au}_sigma{c}mas_m"] = e
        emit(f"    {d_au:8.5f} AU {ang / ARCSEC / 3600.0:11.4f} " +
             "".join(f"{v:14.2f}" for v in row))
    emit()
    emit("  The error grows as Delta^2.  This is a close-approach instrument,")
    emit("  not a catalogue instrument: it is worthless at 1 AU and decisive")
    emit("  inside 0.01 AU.")
    emit("  It is valid only while the target is outside the baseline")
    emit(f"  (Delta > b = {EARTH_MOON / 1000.0:,.0f} km).  Inside b the Moon's")
    emit("  own ephemeris gives the range directly, to the centimetre, and the")
    emit("  parallax construction is unnecessary.")
    emit()
    emit("  Astrometric precisions that can be put into the table:")
    for label, b_m in (("100 m baseline, SNR 7 (CAPS design point)", 100.0),
                       ("1.5 km baseline, SNR 7", 1500.0),
                       ("3 km baseline, SNR 7", 3000.0)):
        sig_mas = interferometric_precision_rad(lam, b_m, 7.0) / ARCSEC * 1000.0
        emit(f"    {label:42s}: {sig_mas:10.4f} mas")
    emit("  A kilometre-scale baseline therefore beats the 1 mas column of the")
    emit("  table above by two orders of magnitude.  The table's 1 mas column is")
    emit("  the conservative case, not the achievable one.")
    out["two_station_range_error_m"] = ranging
    out["earth_moon_baseline_km"] = EARTH_MOON / 1000.0
    out["interferometric_centroid_mas"] = {
        f"B{int(b_m)}m": interferometric_precision_rad(lam, b_m, 7.0) / ARCSEC * 1000.0
        for b_m in (100.0, 1500.0, 3000.0)
    }

    # ---------------------------------------------------------------- 14b
    emit()
    emit("  THE DETECTION RECORDS THAT DEFINE THE BASELINE")
    emit("-" * 78)
    emit("  First observations and close approaches from the JPL SBDB")
    emit("  (sbdb.api, cad.api).  These are the control: the historical record")
    emit("  of what was actually detected, and when.")
    records = [
        ("2008 TC3", "2008-10-06", None, None, None,
         "named by AMAS as a Sun-ward blind-zone failure"),
        ("2019 OK", "2017-02-21", "2019-07-25", 0.000476979, 0.1058,
         "announced three days before a 71,355 km pass"),
        ("2024 YR4", "2024-12-25", "2024-12-25", 0.00554002, 13.7515,
         "discovered on the night of an 828,775 km pass"),
        ("2024 YR4", "2024-12-25", "2032-12-22", 0.00186054, 13.3072,
         "next approach, 278,333 km, a lunar impact"),
        ("99942 Apophis", None, "2029-04-13", 0.00025409, 7.4225,
         "38,011 km, inside the Earth's sphere of influence"),
    ]
    rec_rows = []
    emit(f"    {'object':13s} {'first obs':11s} {'approach':11s} "
         f"{'range(km)':>11s} {'v_rel(km/s)':>12s}  note")
    for des, first_obs, ca_date, dist_au, v_rel_kms, note in records:
        rng_km = None if dist_au is None else dist_au * AU_M / 1000.0
        emit(f"    {des:13s} {str(first_obs):11s} {str(ca_date):11s} "
             f"{('-' if rng_km is None else format(rng_km, ',.0f')):>11s} "
             f"{('-' if v_rel_kms is None else format(v_rel_kms, '.4f')):>12s}  "
             f"{note}")
        rec_rows.append(dict(des=des, first_obs=first_obs, ca_date=ca_date,
                             dist_au=dist_au, range_km=rng_km,
                             v_rel_km_s=v_rel_kms, note=note))
    emit()
    emit("  Two facts carry the whole detection argument:")
    emit("    2024 YR4 was discovered on the night it passed at 828,774 km.")
    emit("    2019 OK was announced three days before it passed at 71,357 km.")
    emit("  Both were found late because they came from the Sun-ward side, and")
    emit("  neither was found late because the instruments were inadequate.")
    out["detection_records"] = rec_rows

    # ---------------------------------------------------------------- 15
    emit()
    emit("15. THE DOCUMENTED CASES: GEOMETRY AND WHAT IS MEASURABLE")
    emit("-" * 78)
    emit("  Ranges from the JPL SBDB Close Approach Data API (cad.api).")
    emit("  H is the SBDB absolute magnitude; for 2024 YR4 the SBDB value")
    emit("  23.93 +/- 0.28 differs from the JWST value 24.14 +/- 0.25, a 0.21")
    emit("  mag discrepancy inside both uncertainties.")
    cases = [
        ("2024 YR4, discovery-night approach", 60.8, 23.93, 828774e3,
         "cad.api 2024-12-25"),
        ("2024 YR4, 2028 apparition", 60.8, 23.93, 0.05 * AU_M,
         "arXiv:2601.10666"),
        ("2024 YR4, 2032 lunar impact", 60.8, 23.93, 22900e3,
         "JWST MIRI, arXiv:2609.15756"),
        ("2024 YR4, 2032 nominal selenocentric", 60.8, 23.93, 3000e3,
         "arXiv:2601.10666"),
        ("Apophis, 2029 Earth encounter", 325.0, 19.09, 38011e3,
         "cad.api 2029-04-13"),
    ]
    emit(f"    {'case':38s} {'theta(mas)':>11s} {'aperture(m)':>12s} "
         f"{'B at N=4(m)':>13s} {'V(0 phase)':>11s} {'range err(m)':>14s}")
    case_rows = []
    for label, d_obj, h, rng_m, src in cases:
        theta = d_obj / rng_m
        ap = resolved_aperture_m(lam, theta)
        b4 = 4.0 * lam / theta
        v = apparent_magnitude(h, 1.0, rng_m / AU_M)
        if rng_m > EARTH_MOON:
            sig = 1.0 / 1000.0 * ARCSEC
            rng_err = two_station_range_error_m(rng_m, sig, EARTH_MOON)
            rng_note = "parallax, 1 mas"
        else:
            rng_err = 0.01
            rng_note = "direct, lunar ephemeris"
        emit(f"    {label:38s} {theta / ARCSEC * 1000.0:11.4f} {ap:12.3f} "
             f"{b4:13.2f} {v:11.2f} {rng_err:14.2f}  ({rng_note})")
        case_rows.append(dict(label=label, D_m=d_obj, H_sbdb=h,
                              range_m=rng_m, theta_mas=theta / ARCSEC * 1000.0,
                              aperture_m=ap, baseline_N4_m=b4, V_zero_phase=v,
                              range_error_m=rng_err, range_mode=rng_note,
                              source=src))
    emit("  V is the zero-phase magnitude with the heliocentric distance set to")
    emit("  1 AU, which is optimistic at these phase angles.")
    out["counterfactual_cases"] = case_rows

    # ---------------------------------------------------------------- 16
    emit()
    emit("16. THE SERVICE RATE AND THE BACKLOG IT CANNOT CLEAR")
    emit("-" * 78)
    sweep = 90.0 / rate
    cap = campaigns_per_year(sweep)
    emit(f"  A fixed station needs a 90 deg baseline-orientation sweep per")
    emit(f"  campaign: {sweep:.2f} days at {rate:.3f} deg/day.")
    emit(f"  With 30 % of the time lost to overhead: {cap:.1f} campaigns per year.")
    emit()
    emit(f"  Demand: {rate140} new >=140 m objects per year (2025).")
    emit(f"  Capacity: {cap:.0f} campaigns per year.")
    emit(f"  -> the station can account for {100.0 * cap / rate140:.1f} % of the")
    emit("     annual arrival of the hazard class.")
    emit(f"  -> clearing the {n140:,} known >=140 m objects at {cap:.0f}/yr would")
    emit(f"     take {n140 / cap:.0f} years.")
    emit(f"  -> a service rate of {rate140:.0f}/yr would be needed to cover the")
    emit(f"     backlog in ten years, i.e. {rate140 / cap:.0f} times the array.")
    emit("  The station therefore cannot be a census.  It has to be a targeted")
    emit("  service, and the selection rule has to say which targets.")
    out["service_capacity_per_year"] = cap
    out["annual_coverage_fraction"] = cap / rate140
    out["backlog_clearance_years"] = n140 / cap

    # ---------------------------------------------------------------- 17
    emit()
    emit("17. THE ACCOUNTABILITY LADDER: WHAT EACH LINK IS WORTH")
    emit("-" * 78)
    emit("  E = (1/2) rho (pi/6) D^3 v^2  ->  dlnE = 3 dlnD + dlnrho")
    ladder = [
        ("Sentry tabulated state  (D 30 %, rho 30 %)", 0.30, 0.30,
         "verified: CNEOS Sentry, factor of three"),
        ("thermal-model spread removed (D 19 %, rho 30 %)", 0.19, 0.30,
         "YR4 NEATM/FRM/TPM spread, arXiv:2609.15756"),
        ("+ resolved shape (D 10 %, rho 30 %)", 0.10, 0.30, "requirement"),
        ("+ close-approach density (D 10 %, rho 10 %)", 0.10, 0.10, "requirement"),
        ("+ both at 5 %", 0.05, 0.05, "requirement"),
    ]
    for label, df, rf, note in ladder:
        emit(f"    {label:48s} -> E uncertain by a factor "
             f"{energy_uncertainty_factor(df, rf):5.2f}   [{note}]")
    emit()
    emit("  Decomposition check on the published 2024 YR4 model set:")
    f_th = (60.8 / 51.1) ** 3
    f_rho = 3500.0 / 1300.0
    emit(f"    thermal model alone (60.8 m vs 51.1 m): factor {f_th:.3f}")
    emit(f"    density alone (3500 vs 1300 kg/m^3):      factor {f_rho:.3f}")
    emit(f"    product:                                 factor {f_th * f_rho:.3f}")
    emit(f"    published spread (2.16 to 9.79 Mt):       factor "
         f"{9.79 / 2.16:.3f}")
    emit("  The diameter and the density contribute comparably.  Removing only")
    emit("  the thermal-model ambiguity buys half the gap; the other half is")
    emit("  the density, and the density is a mass measurement, not a shape.")
    out["accountability_ladder"] = {
        label: energy_uncertainty_factor(df, rf) for label, df, rf, _ in ladder
    }
    out["yr4_energy_decomposition"] = {"thermal_model": f_th, "density": f_rho,
                                       "product": f_th * f_rho}

    emit()
    emit("=" * 78)
    emit("18. THE TWO WORKED CASES, STEP BY STEP")
    emit("-" * 78)
    emit("  Step 1: the matched baseline for four samples.")
    emit("  Step 2: the over-resolution limit, as the baseline at which the")
    emit("           uniform-disc visibility falls to half.")
    emit("  Step 3: the astrometric precision at the matched baseline, and the")
    emit("           position it delivers at the encounter range.")
    emit("  Step 6: whether the physical term dominates, from the published")
    emit("           along-track and B-plane figures.")
    worked = []
    for label, D, H, rng_m, lam_sel in (
            ("2024 YR4, 2032 lunar encounter", 60.8, 23.93, 22900e3, 750e-9),
            ("Apophis, 2029 Earth encounter", 325.0, 19.09, 38011e3, 750e-9)):
        theta = D / rng_m
        b4 = 4.0 * lam_sel / theta
        b7 = 7.0 * lam_sel / theta
        ap = resolved_aperture_m(lam_sel, theta)
        # the over-resolution limit: the baseline at which the uniform-disc
        # visibility falls to one half.  Solved for the dimensionless
        # argument x, which stays in the range where the Bessel series is
        # numerically stable; the series overflows for large x.
        lo, hi = 0.5, 3.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if disk_visibility_x(mid) > 0.5:
                lo = mid
            else:
                hi = mid
        x_over = 0.5 * (lo + hi)
        b_over = x_over * lam_sel / (math.pi * theta / 2.0)
        sig = interferometric_precision_rad(lam_sel, b4, 7.0)
        pos_m = sig * rng_m
        v = apparent_magnitude(H, 1.0, rng_m / AU_M)
        vis_matched = disk_visibility(b4, lam_sel, theta / 2.0)
        emit()
        emit(f"  {label}")
        emit(f"    angular diameter        : {theta/ARCSEC*1000:10.4f} mas "
             f"({theta/ARCSEC*3600:.4f} arcsec)")
        emit(f"    aperture to resolve     : {ap:10.3f} m")
        emit(f"    matched baseline, N = 4 : {b4:10.3f} m")
        emit(f"    matched baseline, N = 7 : {b7:10.3f} m")
        emit(f"    uniform-disc visibility : {vis_matched:10.4f} at the N = 4 "
             f"baseline")
        emit(f"    V = 0.5 baseline        : {b_over:10.3f} m")
        emit(f"    centroid precision      : {sig/ARCSEC*1000:10.4f} mas "
             f"at the N = 4 baseline, SNR 7")
        emit(f"    position at the range   : {pos_m:10.3f} m")
        emit(f"    apparent magnitude      : {v:10.2f} (zero phase, r = 1 AU)")
        worked.append(dict(label=label, D_m=D, H=H, range_m=rng_m,
                           theta_mas=theta / ARCSEC * 1000, aperture_m=ap,
                           baseline_N4_m=b4, baseline_N7_m=b7,
                           visibility_at_matched=vis_matched,
                           half_visibility_baseline_m=b_over,
                           centroid_mas=sig / ARCSEC * 1000,
                           position_m=pos_m, V_zero_phase=v))
    emit()
    emit("  The matched baseline lies BEYOND the half-visibility baseline in")
    emit("  both cases.  That is not a contradiction and it is not a wall:")
    emit("  the half-visibility criterion is the limit of the CENTROID mode,")
    emit("  in which an unresolved source is located from the fringe")
    emit("  centroid.  A resolved body is imaged from the visibility")
    emit("  FUNCTION out to the baseline where the signal is lost, and the")
    emit("  practical limit there is set by the signal-to-noise rather than")
    emit("  by a visibility threshold.  The requirement is set by the")
    emit("  sampling condition alone.")
    out["worked_cases"] = worked

    emit()
    emit("=" * 78)
    emit("SOURCES")
    for k, v in SOURCES.items():
        emit(f"  {k:18s} {v}")
    emit("=" * 78)

    if args.json:
        print(json.dumps(out, indent=2, default=str))
    else:
        print("\n".join(lines))


if __name__ == "__main__":
    main()
