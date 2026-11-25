#!/usr/bin/env python3
"""
Computed figures for "The Shape of the Threat: Characterising Near-Earth Objects
for Impact Accountability, and the Case for a Lunar Surface Array".

This script owns the computed charts.  The schematic diagrams are drawn by
make_diagrams.py, which owns them; one generator per figure.

EVERY NUMBER PLOTTED HERE COMES FROM compute_numbers.py, WHICH IS THE BOOK'S
SINGLE SOURCE OF DERIVED QUANTITIES.  Nothing is transcribed from prose, and
no value is taken from a figure of another book.  Where a chart needs a
published input, that input is quoted in compute_numbers.py with its source.

THE THREE FIGURES THAT CARRY THE ARGUMENT

  fig_shape_baseline.png
      The baseline a shape measurement requires, against the baseline the
      concept literature proposes.  This is the figure that changes the
      architecture.

  fig_two_station.png
      The range error of an Earth-Moon two-station measurement, against the
      distances at which the documented close approaches occur.  This is the
      figure that makes the Moon's contribution measurable rather than
      rhetorical.

  fig_accountability.png
      The size of the population that is discovered but not accounted for,
      against the rate at which a single station could service it.  This is
      the figure that says what the platform is and is not for.

Output: vector PDF into ../figures/
"""
import json
import pathlib
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE.parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

import compute_numbers as CN            # noqa: E402  the single numbers source

BG = "#080B14"
PANEL = "#121828"
EDGE = "#27324C"
ACCENT = "#E8B85C"
ACCENTDIM = "#8A7238"
TXT = "#E6E9F0"
TXTDIM = "#939BAB"
AMBER = "#6FA3D6"
RED = "#C9705A"
GREEN = "#7FB08A"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "text.color": TXT,
    "axes.labelcolor": TXTDIM,
    "xtick.color": TXTDIM,
    "ytick.color": TXTDIM,
    "axes.edgecolor": EDGE,
    "grid.color": EDGE,
    "font.family": "DejaVu Sans",
    "font.size": 7.6,
    "axes.titlesize": 8.8,
    "axes.titleweight": "bold",
    "axes.titlecolor": TXT,
    "figure.dpi": 200,
    "pdf.fonttype": 42,
})

W = 4.6
LAM = 750e-9
AU = CN.AU_M

# When SAVE is False the figures are built but not written, which is how
# build/check_fig_overlaps.py inspects them without touching the output.
SAVE = True
BUILT = []          # (figure, filename) pairs, for the overlap checker


def finish(fig, name):
    BUILT.append((fig, name))
    if SAVE:
        path = OUT / name
        fig.savefig(path, format="pdf", bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
        print("wrote", path.name)
    return fig


def style(ax, title, xlabel, ylabel, grid_axis="both"):
    ax.set_title(title, pad=7)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis=grid_axis, lw=0.4, alpha=0.55)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def tight(fig, pad=0.6, rect=None):
    """tight_layout, with matplotlib's gridspec warning silenced.

    Several figures set wspace on their gridspec, because the panels need
    a wider gap than matplotlib's default.  That makes matplotlib decline
    to lay the figure out itself and warn about it.  The layout is not
    assumed here: build/check_fig_overlaps.py measures every figure
    geometrically and fails the build on a collision.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message=".*not compatible with tight_layout.*")
        if rect is None:
            fig.tight_layout(pad=pad)
        else:
            fig.tight_layout(pad=pad, rect=rect)


# =====================================================================
#  1.  The catalogue: what is known, and how fast it grows
# =====================================================================
def fig_catalogue():
    raw = json.loads((HERE.parent / "research" / "evidence" /
                      "cneos_nea_vs_time.json").read_text())
    series = {s["name"]: s["data"] for s in raw[1]}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.5),
                                  gridspec_kw={"wspace": 0.34})

    for name, colour, label in (("All", TXTDIM, "All NEAs"),
                                ("140m+", ACCENT, "140 m and larger"),
                                ("1km+", AMBER, "1 km and larger")):
        data = series[name]
        t = np.array([p[0] for p in data]) / 8.64e7 / 365.25 + 1970.0
        n = np.array([p[1] for p in data], dtype=float)
        ax.plot(t, n, lw=1.3, color=colour, label=label)

    style(ax, "Known near-Earth objects", "year of discovery", "objects known")
    ax.legend(frameon=False, fontsize=6.4, loc="upper left")
    ax.set_ylim(0, 46000)

    years = list(range(2015, 2027))
    allr = CN.cneos_annual_arrivals(series["All"])
    big = CN.cneos_annual_arrivals(series["140m+"])
    x = np.arange(len(years))
    ax2.bar(x - 0.19, [allr.get(y, 0) for y in years], width=0.36,
            color=TXTDIM, label="All sizes")
    ax2.bar(x + 0.19, [big.get(y, 0) for y in years], width=0.36,
            color=ACCENT, label="140 m and larger")
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(y)[2:] for y in years], rotation=90, fontsize=6.2)
    style(ax2, "Discovered per year", "year", "discoveries")
    ax2.legend(frameon=False, fontsize=6.4)
    ax2.set_ylim(0, 3800)

    tight(fig, pad=0.6)
    finish(fig, "fig_catalogue.pdf")


# =====================================================================
#  2.  The accountability gap and the service rate
# =====================================================================
def fig_accountability():
    cneos = CN.load_cneos()
    n140 = cneos["series"]["140m+"][-1][1]
    with_spec = 0.15 * n140
    without = n140 - with_spec
    rate = CN.cneos_annual_arrivals(cneos["series"]["140m+"])[2025]
    sweep = 90.0 / (360.0 / CN.LUNAR_SIDEREAL_DAYS)
    cap = CN.campaigns_per_year(sweep)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.6),
                                  gridspec_kw={"wspace": 0.62,
                                               "width_ratios": [1.0, 1.1]})

    ax.barh([0], [with_spec], color=AMBER, height=0.38)
    ax.barh([0], [without], left=[with_spec], color=PANEL, height=0.38,
            edgecolor=EDGE)
    ax.set_xlim(0, n140 * 1.02)
    ax.set_ylim(-0.62, 0.72)
    ax.set_yticks([])
    style(ax, f"The 140 m class: {n140:,} objects", "objects in the catalogue",
          "", grid_axis="x")
    # The counts and the two accounts are carried by the legend rather than
    # by labels on the bar: the spectrum segment is too narrow to hold them.
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=AMBER),
        plt.Rectangle((0, 0), 1, 1, facecolor=PANEL, edgecolor=EDGE),
    ]
    ax.legend(handles,
              [f"{with_spec:,.0f} with a spectrum",
               f"{without:,.0f} with no account"],
              frameon=False, fontsize=6.0, loc="upper center",
              bbox_to_anchor=(0.5, 1.0), labelspacing=0.45,
              handlelength=1.2, handleheight=0.8)
    ax.text(0.02, 0.03, "under 1 % imaged with radar",
            transform=ax.transAxes, color=RED, fontsize=6.0)

    labels = ["new objects\nper year", "station\ncampaigns", "objects to\naccount for"]
    values = [rate, cap, n140]
    bars = ax2.bar([0, 1, 2], [rate, cap, n140], width=0.5,
                   color=[ACCENT, GREEN, TXTDIM])
    ax2.set_yscale("log")
    ax2.set_ylim(10, n140 * 6)
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(labels, fontsize=5.9)
    style(ax2, "Demand against capacity", "", "objects or campaigns")
    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width() / 2, val * 1.5,
                 f"{val:,.0f}", ha="center", color=TXT, fontsize=6.8)
    ax2.annotate("", xy=(1.34, cap), xytext=(1.34, n140),
                 arrowprops=dict(arrowstyle="<->", color=AMBER, lw=0.8))
    ax2.text(1.44, np.sqrt(cap * n140), f"{n140 / cap:.0f} years",
             color=AMBER, fontsize=6.4, va="center", rotation=90)

    tight(fig, pad=0.6)
    finish(fig, "fig_accountability.pdf")


# =====================================================================
#  3.  The baseline a shape measurement requires
# =====================================================================
def fig_shape_baseline():
    fig, ax = plt.subplots(figsize=(W, 2.7))
    d_au = np.logspace(np.log10(0.02), np.log10(1.5), 200)
    for D, colour in ((50.0, TXTDIM), (60.0, ACCENT), (140.0, AMBER)):
        theta = D / (d_au * AU)
        ax.plot(d_au, 4.0 * LAM / theta, lw=1.4, color=colour,
                label=f"{D:.0f} m diameter")
        ax.plot(d_au, 7.0 * LAM / theta, lw=0.7, color=colour, ls=":", alpha=0.7)
    ax.axhline(100.0, color=RED, lw=1.0, ls="--")
    ax.text(1.42, 118, "100 m: the baseline in the concept literature",
            color=RED, fontsize=6.4, ha="right", va="bottom")
    ax.axhline(300.0, color=GREEN, lw=1.0, ls="--")
    ax.text(1.45, 340, "300 m: the lower end of the lunar array",
            color=GREEN, fontsize=6.4, ha="right", va="bottom")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.02, 1.5)
    ax.set_ylim(20, 20000)
    style(ax, "Baseline required for four samples across the diameter",
          "geocentric distance (AU)", "baseline (m)")
    ax.legend(frameon=False, fontsize=6.6, loc="upper left")
    ax.text(0.9, 26, "dotted: seven samples", color=TXTDIM, fontsize=6.2)

    tight(fig, pad=0.5)
    finish(fig, "fig_shape_baseline.pdf")


# =====================================================================
#  4.  Samples across the diameter against baseline
# =====================================================================
def fig_samples():
    fig, ax = plt.subplots(figsize=(W, 2.6))
    d_au = np.logspace(np.log10(0.02), np.log10(1.5), 200)
    for D, colour in ((50.0, TXTDIM), (60.0, ACCENT), (140.0, AMBER)):
        theta = D / (d_au * AU)
        for B, ls, lw in ((100.0, "--", 0.9), (1500.0, "-", 1.3)):
            ax.plot(d_au, theta * B / LAM, lw=lw, color=colour, ls=ls)
    ax.axhline(4.0, color=GREEN, lw=1.0)

    # The concept study's own design point: a 100 m baseline at a 50 m
    # object at 0.1 AU.  N = 0.45 there; at 0.2 AU it is 0.22.  Both come
    # from compute_numbers.py, and the pair quoted here is the one the
    # generator prints.
    n_design = 50.0 * 100.0 / (0.1 * AU * LAM)
    ax.plot([0.1], [n_design], "o", ms=4.0, color=RED)

    # The four-sample condition, labelled in the band beyond the point where
    # every curve has dropped below it.
    ax.text(1.45, 5.6, "N = 4: the shape condition\ncalibrated on 3 Juno",
            color=GREEN, fontsize=6.2, ha="right", va="bottom")

    # The design point, labelled in the empty lower-left corner.
    ax.annotate("the concept design point:\n50 m at 0.1 AU, N = 0.45",
                xy=(0.1, n_design), xytext=(0.021, 0.055),
                color=RED, fontsize=6.2, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color=RED, lw=0.7,
                                shrinkA=2, shrinkB=3))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.02, 1.5)
    ax.set_ylim(0.02, 400)
    style(ax, "Samples across the diameter", "geocentric distance (AU)",
          "N = diameter x baseline / wavelength")
    ax.plot([], [], color=TXTDIM, ls="--", label="100 m baseline")
    ax.plot([], [], color=TXTDIM, ls="-", label="1.5 km baseline")
    ax.legend(frameon=False, fontsize=6.4, loc="upper right")

    tight(fig, pad=0.5)
    finish(fig, "fig_samples.pdf")


# =====================================================================
#  5.  The mid-infrared channel, closed twice
# =====================================================================
def fig_mir():
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.4),
                                  gridspec_kw={"wspace": 0.42})
    r_au = np.linspace(0.2, 1.5, 200)
    fg = CN.planck_radiance_um(10.0, 390.0)
    contrast = np.array([CN.planck_radiance_um(10.0, 278.0 / np.sqrt(r)) / 4.0 / fg
                         for r in r_au])
    ax.plot(r_au, contrast, lw=1.5, color=ACCENT)
    ax.axhline(1.0, color=RED, lw=1.0, ls="--")
    ax.text(0.23, 1.25, "sunlit ground as bright\nas the target",
            color=RED, fontsize=6.4)
    ax.set_ylim(0, 1.6)
    style(ax, "Target against sunlit regolith", "heliocentric distance (AU)",
          "contrast")
    # The four marked contrasts are computed, never typed in.  Each label
    # sits above and to the right of its point, which is clear of the
    # descending curve.
    for r in (0.3, 0.5, 1.0, 1.3):
        c = CN.planck_radiance_um(10.0, 278.0 / np.sqrt(r)) / 4.0 / fg
        ax.plot([r], [c], "o", ms=3.4, color=ACCENT)
        ax.annotate(f"{c:.3f}", (r, c), textcoords="offset points",
                    xytext=(5, 6), color=TXT, fontsize=6.2, va="bottom")

    sb03 = CN.planck_radiance_um(10.0, 278.0 / np.sqrt(0.3)) / 4.0
    tb = np.linspace(25, 400, 200)
    bb = np.array([CN.planck_radiance_um(10.0, t) for t in tb])
    ax2.plot(tb, bb / sb03, lw=1.5, color=AMBER)
    ax2.axhline(1.0, color=RED, lw=1.0, ls="--")
    ax2.set_yscale("log")
    ax2.set_xlim(25, 400)
    ax2.set_ylim(1e-17, 100)
    style(ax2, "Baffle against the target disk",
          "baffle temperature (K)", "relative to the target")
    for t, off, ha in ((390.0, (-6, 8), "right"), (40.0, (6, -6), "left")):
        c = CN.planck_radiance_um(10.0, t) / sb03
        ax2.plot([t], [c], "o", ms=3.4, color=AMBER)
        ax2.annotate(f"{t:.0f} K", (t, c), textcoords="offset points",
                     xytext=off, ha=ha, va="center", color=TXT, fontsize=6.2)

    tight(fig, pad=0.6)
    finish(fig, "fig_mir.pdf")


# =====================================================================
#  6.  The accountability ladder
# =====================================================================
def fig_energy_ladder():
    rows = [
        ("Sentry tabulated state\nD 30 %, rho 30 %", 0.30, 0.30, AMBER),
        ("thermal-model spread removed\nD 19 %, rho 30 %", 0.19, 0.30, ACCENT),
        ("plus a resolved shape\nD 10 %, rho 30 %", 0.10, 0.30, ACCENT),
        ("plus a close-approach density\nD 10 %, rho 10 %", 0.10, 0.10, GREEN),
        ("both at 5 %", 0.05, 0.05, GREEN),
    ]
    labels = [r[0] for r in rows]
    vals = [CN.energy_uncertainty_factor(r[1], r[2]) for r in rows]
    colours = [r[3] for r in rows]
    fig, ax = plt.subplots(figsize=(W, 2.5))
    y = np.arange(len(rows))[::-1]
    ax.barh(y, vals, height=0.56, color=colours)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6.3)
    ax.set_xlim(1.0, 3.4)
    for yy, v in zip(y, vals):
        ax.text(v + 0.03, yy, f"{v:.2f}x", va="center", color=TXT, fontsize=6.8)
    ax.axvline(3.0, color=RED, lw=0.9, ls="--")
    ax.text(3.02, y[-1] - 0.42, "the present factor of three",
            color=RED, fontsize=6.2)
    style(ax, "Uncertainty remaining in the impact energy",
          "factor of uncertainty in E", "", grid_axis="x")

    tight(fig, pad=0.5)
    finish(fig, "fig_energy_ladder.pdf")


# =====================================================================
#  7.  Two-station ranging on the Earth-Moon baseline
# =====================================================================
def fig_two_station():
    fig, ax = plt.subplots(figsize=(W, 2.8))
    b_au = CN.EARTH_MOON / AU
    d_au = np.logspace(np.log10(0.00015), np.log10(1.5), 400)

    # The regime inside the baseline: the Moon's own ephemeris gives the
    # range directly, so the parallax construction is not needed at all.
    ax.axvspan(1.5e-4, b_au, color=PANEL, zorder=0)
    ax.axvline(b_au, color=RED, lw=1.0, ls="--")
    ax.text(b_au * 1.12, 1.3e5,
            "inside the baseline length:\nthe Moon's ephemeris gives the range",
            color=RED, fontsize=6.0, ha="left")

    for sig_mas, colour, ls in ((0.1, GREEN, "-"), (1.0, ACCENT, "-"),
                                (10.0, AMBER, "-"), (100.0, TXTDIM, ":")):
        d = d_au[d_au > b_au]
        err = np.array([CN.two_station_range_error_m(
            x * AU, sig_mas / 1000.0 * CN.ARCSEC, CN.EARTH_MOON) for x in d])
        ax.plot(d, err / 1000.0, lw=1.4, color=colour, ls=ls,
                label=f"{sig_mas:g} mas")

    # The three documented close approaches.  Their labels sit in the empty
    # region inside the baseline length, and are staggered so that neither
    # touches the other, a marker or a curve.
    inside = [("Apophis 2029\n38,011 km", 38011e3, (8, -22)),
              ("2019 OK\n71,355 km", 71355e3, (0, 20))]
    for label, rng, off in inside:
        ax.plot([rng / AU], [1e-2], "o", ms=4.0, color=GREEN)
        ax.annotate(label, (rng / AU, 1e-2), textcoords="offset points",
                    xytext=off, color=TXT, fontsize=6.0, ha="center",
                    va="center")
    rng = 828775e3
    err = CN.two_station_range_error_m(rng, 1.0 / 1000.0 * CN.ARCSEC,
                                       CN.EARTH_MOON) / 1000.0
    ax.plot([rng / AU], [err], "o", ms=4.4, color=ACCENT)
    ax.annotate("2024 YR4, 828,775 km\n8.66 m at 1 mas", (rng / AU, err),
                textcoords="offset points", xytext=(46, -20), ha="center",
                va="center", color=TXT, fontsize=6.0)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.5e-4, 1.5)
    ax.set_ylim(1e-4, 1e6)
    style(ax, "Two-station range error on the Earth-Moon baseline",
          "geocentric distance (AU)", "range error (km)")
    ax.legend(frameon=False, fontsize=6.4, loc="upper left",
              bbox_to_anchor=(0.02, 0.99))

    tight(fig, pad=0.5)
    finish(fig, "fig_two_station.pdf")


# =====================================================================
#  8.  The 2024 YR4 energy spread and the threshold it moves
# =====================================================================
def fig_yr4():
    models = CN.yr4_model_set()
    short = ["NEATM\nrejected", "FRM", "TPM", "TPM\nrho 1300",
             "FRM\nrho 1300", "TPM\nrho 3500"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.5),
                                  gridspec_kw={"wspace": 0.55,
                                               "width_ratios": [1.35, 1.0]})
    energies = [CN.energy_mt(d, r, 14.1) for _, d, r in models]
    xs = np.arange(len(models))
    bars = ax.bar(xs, energies, width=0.6,
                   color=[RED, ACCENT, GREEN, TXTDIM, TXTDIM, TXTDIM])
    ax.set_xticks(xs)
    ax.set_xticklabels(short, fontsize=5.7)
    style(ax, "Impact energy, 2024 YR4", "", "energy (Mt)")
    ax.set_xlabel("rho is the bulk density in kg/m3", fontsize=6.2,
                  color=TXTDIM, labelpad=2)
    for bar, e in zip(bars, energies):
        ax.text(bar.get_x() + bar.get_width() / 2, e + 0.25,
                f"{e:.2f}", ha="center", color=TXT, fontsize=6.2)
    ax.set_ylim(0, 14)

    # The spread across the published model set, from the lowest bar to the
    # highest.  Both ends are bars that are actually drawn.
    e_lo, e_hi = min(energies), max(energies)
    ax.annotate("", xy=(5.42, e_lo), xytext=(5.42, e_hi),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=0.9))
    ax.text(5.38, 11.4, f"factor {e_hi / e_lo:.1f}\nfrom model choice alone",
            color=RED, fontsize=6.2, va="bottom", ha="right")

    p1 = [(lab, 10.0 ** (-7.0 / 3.0) / CN.energy_mt(d, r, 14.1))
          for lab, d, r in models]
    p1.sort(key=lambda z: z[1])
    short_y = ["NEATM", "FRM", "TPM", "TPM 1300", "FRM 1300", "TPM 3500"]
    key = {m[0]: s for m, s in zip(models, short_y)}
    labs = [key[p[0]] for p in p1]
    vals = [p[1] for p in p1]
    ax2.barh(np.arange(len(vals)), vals, height=0.55,
             color=[ACCENT if v > 1.5e-3 else TXTDIM for v in vals])
    ax2.set_yticks(np.arange(len(vals)))
    ax2.set_yticklabels(labs, fontsize=5.7)
    ax2.set_xscale("log")
    style(ax2, "Probability for Torino Level 1", "", "p",
          grid_axis="x")
    ax2.set_xlim(min(vals) * 0.5, max(vals) * 3.0)
    for i, v in enumerate(vals):
        ax2.text(v * 1.25, i, f"{v:.2e}", va="center", color=TXT, fontsize=6.0)

    tight(fig, pad=0.6)
    finish(fig, "fig_yr4.pdf")


# =====================================================================
#  9.  The 2036 keyhole magnifies physical error
# =====================================================================
def fig_keyhole():
    rows = CN.bottke_2036_rows()
    labels = ["Nominal", "Diameter 270 +/- 60 m", "Uniform cos gamma",
              "Symmetric cos gamma", "Density variance 0.6", "mu_d0 = 200",
              "mu_d0 = 400"]
    nominal = rows[0][1]
    fig, ax = plt.subplots(figsize=(W, 2.6))
    y = np.arange(len(rows))[::-1]
    vals = [v for _, v in rows]
    facs = [v / nominal for v in vals]
    colours = [ACCENT if f > 10 else TXTDIM for f in facs]

    # Each row is drawn as a departure from the nominal case, so that the
    # perturbations that lower the probability are as visible as the ones
    # that raise it.  A bar drawn from zero would vanish on a log axis.
    for yy, f, colour in zip(y, facs, colours):
        ax.plot([1.0, f], [yy, yy], lw=5.0, color=colour,
                solid_capstyle="butt")
        ax.plot([f], [yy], "o", ms=4.0, color=colour)

    ax.axvline(1.0, color=EDGE, lw=1.0, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6.4)
    ax.set_xscale("log")
    ax.set_xlim(0.03, 3000)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    style(ax, "2036 impact probability against the nominal case",
          "factor by which the probability moves", "", grid_axis="x")
    for yy, f in zip(y, facs):
        if f >= 1.0:
            lx, ha = f * 1.35, "left"
        else:
            lx, ha = f / 1.8, "right"
        ax.text(lx, yy, f"{f:,.2f}x" if f < 10 else f"{f:,.0f}x",
                va="center", ha=ha, color=TXT, fontsize=6.6)
    ax.text(1.15, -0.45, "the nominal case", color=TXTDIM, fontsize=6.0,
            va="center", ha="left")
    ax.text(700, 5.55, "diameter alone", color=ACCENT, fontsize=6.2,
            va="center", ha="center")

    tight(fig, pad=0.5)
    finish(fig, "fig_keyhole.pdf")


# =====================================================================
#  10.  Along-track error against the astrometric floor
# =====================================================================
def fig_along_track():
    horizons = np.linspace(1, 60, 200)
    rates = [50.0, 300.0, 1000.0]
    fig, ax = plt.subplots(figsize=(W, 2.5))
    for rate, colour in zip(rates, (TXTDIM, AMBER, ACCENT)):
        err = np.array([CN.along_track_offset_m(rate * 0.30, 1.1, h) / 1000.0
                        for h in horizons])
        ax.plot(horizons, err, lw=1.4, color=colour,
                label=f"{rate:.0f} m/yr, 30 % error")
    ax.axhline(25000.0, color=RED, lw=1.0, ls="--")
    ax.text(1.4, 30000, "published lunar B-plane uncertainty, 25,000 km",
            color=RED, fontsize=6.2)
    ax.set_yscale("log")
    ax.set_xlim(1, 60)
    ax.set_ylim(1, 1e6)
    style(ax, "Along-track error against the astrometric floor",
          "years from the 2025 arc", "along-track error (km)")
    ax.legend(frameon=False, fontsize=6.4, loc="upper right")

    tight(fig, pad=0.5)
    finish(fig, "fig_along_track.pdf")


# =====================================================================
#  11.  The sky turns more slowly on the Moon
# =====================================================================
def fig_rotation():
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.2),
                                  gridspec_kw={"width_ratios": [1, 1.2]})
    rate_moon = 360.0 / CN.LUNAR_SIDEREAL_DAYS
    bars = ax.bar([0, 1], [15.0 * 60.0, rate_moon], width=0.5,
                  color=[TXTDIM, ACCENT])
    ax.set_yscale("log")
    ax.set_ylim(1, 1e4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Earth\nsky", "Moon\nsky"], fontsize=6.6)
    style(ax, "Rate the sky turns", "", "degrees per day")
    for b, v in zip(bars, [15.0 * 60.0, rate_moon]):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.5,
                f"{v:,.1f}" + (" deg/hr" if v > 100 else " deg/day"),
                ha="center", color=TXT, fontsize=6.4)

    days = np.linspace(0, 30, 300)
    ax2.plot(days, (360.0 / CN.LUNAR_SIDEREAL_DAYS) * days, lw=1.6, color=ACCENT)
    ax2.axhline(90, color=GREEN, lw=1.0, ls="--")
    ax2.plot([90.0 / rate_moon], [90], "o", ms=4.4, color=GREEN)
    ax2.annotate(f"90 deg in {90.0 / rate_moon:.2f} days",
                 (90.0 / rate_moon, 90), textcoords="offset points",
                 xytext=(6, -14), color=GREEN, fontsize=6.4)
    ax2.axhline(180, color=AMBER, lw=0.9, ls=":")
    ax2.set_xlim(0, 30)
    ax2.set_ylim(0, 200)
    style(ax2, "Baseline orientation sweep", "days", "degrees")

    tight(fig, pad=0.6)
    finish(fig, "fig_rotation.pdf")


# =====================================================================
#  12.  The Sun-ward lead time
# =====================================================================
def fig_sunward():
    v_rel = 20.0
    rows = [("30 m", 0.05, 4.0, 5.0), ("140 m", 0.10, 9.0, 9.0),
            ("1 km", 0.50, 42.0, 42.0)]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(W, 2.3))
    labels = [r[0] for r in rows]
    moon = [r[1] for r in rows]
    ground = [r[1] + v_rel * 0.5 * (r[2] + r[3]) * 86400.0 * 1000.0 / AU
              for r in rows]
    x = np.arange(len(rows))
    ax.bar(x - 0.19, ground, width=0.36, color=TXTDIM, label="ground limit")
    ax.bar(x + 0.19, moon, width=0.36, color=ACCENT, label="lunar limit")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=6.8)
    ax.set_yscale("log")
    ax.set_ylim(0.02, 2.0)
    style(ax, "First detectable distance", "object class", "distance (AU)")
    ax.legend(frameon=False, fontsize=6.4)
    for i, (g, m) in enumerate(zip(ground, moon)):
        ax.annotate(f"{g:.2f}", (i - 0.19, g), textcoords="offset points",
                    xytext=(0, 4), ha="center", color=TXT, fontsize=6.0)
        ax.annotate(f"{m:.2f}", (i + 0.19, m), textcoords="offset points",
                    xytext=(0, 4), ha="center", color=TXT, fontsize=6.0)

    days = [0.5 * (r[2] + r[3]) for r in rows]
    bars = ax2.bar(x, days, width=0.5, color=AMBER)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=6.8)
    ax2.set_yscale("log")
    ax2.set_ylim(1, 200)
    style(ax2, "Extra warning time", "object class", "days")
    for b, dd in zip(bars, days):
        ax2.text(b.get_x() + b.get_width() / 2, dd * 1.25, f"{dd:.1f} d",
                 ha="center", color=TXT, fontsize=6.4)

    tight(fig, pad=0.6)
    finish(fig, "fig_sunward.pdf")


# =====================================================================
#  13.  The scale comparison: what was achieved, what is required
# =====================================================================
def fig_scale():
    fig, ax = plt.subplots(figsize=(W, 2.6))
    items = [
        ("Palma, the only asteroid interferometry ever done\n"
         "Earth, radio, 3.6 mm, 1,200 to 2,300 km", 1200, 2300, AMBER),
        ("the concept design point\nlunar, optical, 100 m", 100, 100, RED),
        ("lunar array required for a 140 m object at 0.1 AU", 321, 321, GREEN),
        ("lunar array required for a 60 m object at 0.2 AU", 1496, 1496, GREEN),
        ("lunar array required for a 60 m object at 0.5 AU", 3740, 3740, GREEN),
    ]
    y = np.arange(len(items))[::-1]
    for yy, (lab, lo, hi, colour) in zip(y, items):
        ax.plot([lo, hi], [yy, yy], lw=5.5, color=colour, solid_capstyle="round")
        ax.text(hi * 1.18, yy, f"{lo:,.0f} m" if lo == hi else
                f"{lo:,.0f} to {hi:,.0f} m", va="center", color=TXT, fontsize=6.4)
    ax.set_yticks(y)
    ax.set_yticklabels([i[0] for i in items], fontsize=5.9)
    ax.set_xscale("log")
    ax.set_xlim(40, 60000)
    ax.set_xlabel("baseline (m)")
    ax.grid(True, axis="x", lw=0.4, alpha=0.55)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    # The title spans the whole figure: the long row labels push the axes
    # to the right, so an axes-level title would sit over the right half.
    fig.suptitle("Baseline scales side by side", fontsize=8.8,
                 fontweight="bold", color=TXT, y=0.99)

    tight(fig, pad=0.5, rect=(0, 0, 1, 0.96))
    finish(fig, "fig_scale.pdf")


# =====================================================================
#  14.  The surface brightness of a resolved target
# =====================================================================
def fig_brightness():
    fig, ax = plt.subplots(figsize=(W, 2.5))
    d_au = np.logspace(np.log10(0.2), np.log10(1.0), 120)

    def sb_of(D, d):
        h = CN.absolute_magnitude(D, 0.10)
        v = CN.apparent_magnitude(h, d, d)
        return CN.resolved_surface_brightness(D, d * AU, v)

    # A resolved disk's surface brightness depends on its distance and its
    # albedo, not on its diameter, so the 60 m and 140 m curves coincide.
    # Both are drawn; the 140 m curve is dashed so that it reads through.
    for D, colour, ls, lw in ((60.0, ACCENT, "-", 2.2), (140.0, AMBER, "--", 1.2)):
        ax.plot(d_au, [sb_of(D, d) for d in d_au], lw=lw, color=colour, ls=ls,
                label=f"{D:.0f} m, albedo 0.10")

    ax.axhline(22.0, color=RED, lw=1.0, ls="--")
    ax.text(0.205, 21.6, "zodiacal light, about 22 mag per square arcsecond",
            color=RED, fontsize=6.2, va="bottom")
    ax.text(0.225, 12.0, "the two curves coincide: a resolved disk's surface\n"
                          "brightness depends on its distance and albedo, not on\n"
                          "its diameter",
            color=TXTDIM, fontsize=6.0, ha="left", va="center")

    for d in (0.2, 1.0):
        s = sb_of(60.0, d)
        ax.plot([d], [s], "o", ms=3.6, color=TXT)
        ax.annotate(f"{s:.2f}", (d, s), textcoords="offset points",
                    xytext=(-6, -9) if d > 0.5 else (6, -9), ha="right" if d > 0.5 else "left",
                    color=TXT, fontsize=6.4)

    ax.set_xscale("log")
    ax.set_xlim(0.19, 1.03)
    ax.set_xticks([0.2, 0.3, 0.5, 0.7, 1.0])
    ax.set_xticklabels(["0.2", "0.3", "0.5", "0.7", "1.0"])
    ax.set_ylim(24.0, -1.0)
    style(ax, "Surface brightness of a resolved disk",
          "geocentric distance (AU)", "mag per square arcsecond")
    ax.legend(frameon=False, fontsize=6.4, loc="center right")

    tight(fig, pad=0.5)
    finish(fig, "fig_brightness.pdf")


BUILDERS = [
    fig_catalogue, fig_accountability, fig_shape_baseline, fig_samples,
    fig_mir, fig_energy_ladder, fig_two_station, fig_yr4, fig_keyhole,
    fig_along_track, fig_rotation, fig_sunward, fig_scale, fig_brightness,
]


def build_all(save=True):
    """Build every figure.  With save=False the PDFs are not written."""
    global SAVE
    SAVE = save
    BUILT.clear()
    for fn in BUILDERS:
        fn()
    return list(BUILT)


def main():
    build_all(save=True)
    print("figures complete")


if __name__ == "__main__":
    main()
