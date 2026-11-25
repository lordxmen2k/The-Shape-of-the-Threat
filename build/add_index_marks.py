#!/usr/bin/env python3
"""
Insert index marks into the book chapters.

The book uses two kinds of mark, defined in the preamble:

    \\idxw{Term}   prints Term and registers it in the index.  Use it where
                   the mark stands in for the word itself.
    \\idx{Term}    prints nothing and registers Term.  Use it where the
                   prose already writes the term, so that the mark only has
                   to sit beside the word.

This script registers the FIRST plain occurrence of each term in each
chapter by placing \\idx immediately after the word, which leaves the
rendered prose byte for byte what it was before.  The canonical index entry
is used, so that a term written in lower case in one chapter and in title
case in another produces one index entry rather than two.

A candidate occurrence is skipped when it lies inside a formula, inside an
existing mark, or immediately before a full stop, a semicolon or a colon,
because a mark in those positions either breaks a formula or strands the
punctuation.

Run from the repository root:  python3 build/add_index_marks.py
"""
import pathlib
import re

CHAPTERS = pathlib.Path("source/chapters")

# (chapter number, canonical index entry)
MARKS = [
    (1, "Near-Earth object"), (1, "Catalogue"), (1, "Absolute magnitude"),
    (1, "Albedo"), (1, "Diameter"),
    (2, "Torino scale"), (2, "Impact energy"), (2, "Hazard class"),
    (2, "Impact probability"), (2, "Density"),
    (3, "Planetary defence coordination office"),
    (3, "International Astronomical Union"), (3, "Alerting"),
    (4, "Characterisation"), (4, "Backlog"), (4, "Population"),
    (5, "2024 YR4"), (5, "Beaming parameter"), (5, "Thermophysical model"),
    (5, "Mid-infrared"), (5, "JWST"),
    (6, "Thermal inertia"), (6, "Equilibrium temperature"),
    (6, "Convex hull"), (6, "Photometry"),
    (7, "Rubble pile"), (7, "Polarimetry"), (7, "Mass"),
    (7, "Spin state"),
    (8, "Volume"), (8, "Fresnel number"), (8, "VLBA"),
    (8, "Radio occultation"), (8, "Convexity"),
    (9, "Lightcurve"), (9, "Rotation period"), (9, "Pole"),
    (9, "YORP"), (9, "Obliquity"),
    (10, "Impact speed"), (10, "Background impact frequency"),
    (10, "Kinetic energy"),
    (11, "Keyhole"), (11, "Target plane"), (11, "Along-track coordinate"),
    (11, "Impact parameter"),
    (12, "Yarkovsky"), (12, "Thermal parameter"), (12, "Secular"),
    (13, "Torque"), (13, "Normal direction"),
    (14, "B-plane"), (14, "Tail"), (14, "Along-track"),
    (15, "Renormalisation"), (15, "Regression"), (15, "Monitoring"),
    (16, "Projection"), (16, "Convex body"), (16, "Body of revolution"),
    (16, "Uniqueness"),
    (17, "Lightcurve inversion"), (17, "Asteroid models database"),
    (17, "Roundness"),
    (18, "Radar"), (18, "Delay-Doppler"), (18, "Radar cross-section"),
    (18, "Fourth-power law"), (18, "Bistatic radar"),
    (19, "Adaptive optics"), (19, "Phase angle"), (19, "Terminator"),
    (19, "Limb profile"),
    (20, "Interferometry"), (20, "Fringe spacing"), (20, "Visibility"),
    (20, "Over-resolution"), (20, "Matched baseline"),
    (21, "Vantage"), (21, "Zodiacal light"), (21, "Polar site"),
    (21, "Sidereal rotation"), (21, "Solar elongation"),
    (22, "Baseline"), (22, "Metrology"), (22, "Anchor point"),
    (22, "Survey"),
    (23, "Baffle"), (23, "Permanently shadowed region"), (23, "Regolith"),
    (23, "Regenerative fuel cell"), (23, "Emissivity"),
    (24, "Dust"), (24, "Electrodynamic Dust Shield"), (24, "Night"),
    (24, "Survival temperature"),
    (25, "Service"), (25, "Campaign"), (25, "Array"),
    (25, "Alert path"),
    (26, "NEO Surveyor"), (26, "NEOMIR"), (26, "Segmented mirror"),
    (26, "Elongation"), (26, "Halo orbit"),
    (27, "Parkes"), (27, "Green Bank Telescope"),
    (28, "Portfolio"), (28, "Marginal value"), (28, "Jobs to be done"),
    (29, "Counterfactual"), (29, "Two-station ranging"), (29, "Parallax"),
    (29, "Close approach"),
    (30, "Selection rule"), (30, "Buildability"),
    (31, "Worked case"),
    (32, "Prior art"), (32, "Novelty"), (32, "Falsification"),
    (33, "Accountability"),
]


def add_mark(text: str, term: str) -> tuple[str, bool]:
    """Place \\idx{term} immediately after the first plain occurrence."""
    pattern = re.compile(r"(?<![\w\\])(" + re.escape(term) + r")(?![\w])",
                         re.IGNORECASE)
    for m in pattern.finditer(text):
        start, end = m.span()
        before = text[:start]
        after = text[end:]
        # inside an unbalanced group: a formula, a mark, or a command argument
        if before.count("{") != before.count("}"):
            continue
        # an odd number of dollar signs before the term means we are inside
        # a formula
        if before.count("$") % 2 == 1:
            continue
        if "\\idxw{" in before[-12:] or "\\idx{" in before[-12:]:
            continue
        # already marked
        if after.startswith("\\idx{") or after.startswith("\\idxw{"):
            continue
        # a mark immediately before punctuation would strand it
        if after[:1] in (".", ";", ":"):
            continue
        return text[:end] + "\\idx{" + term + "}" + after, True
    return text, False


def main() -> None:
    total_added = 0
    missing = []
    by_chapter: dict[int, list[str]] = {}
    for num, term in MARKS:
        by_chapter.setdefault(num, []).append(term)

    for num, terms in sorted(by_chapter.items()):
        path = CHAPTERS / f"ch{num:02d}.tex"
        if not path.exists():
            for term in terms:
                missing.append((num, term))
            continue
        text = path.read_text(encoding="utf-8")
        for term in terms:
            text, ok = add_mark(text, term)
            if ok:
                total_added += 1
            else:
                missing.append((num, term))
        path.write_text(text, encoding="utf-8")

    print(f"index marks added: {total_added}")
    if missing:
        print("terms not found (and therefore not marked):")
        for num, term in missing:
            print(f"  ch{num:02d}: {term}")


if __name__ == "__main__":
    main()
