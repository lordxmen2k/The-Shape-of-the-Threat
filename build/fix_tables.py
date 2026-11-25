#!/usr/bin/env python3
"""Rebalance every tabularx column specification against the measure.

The book is set at a 4.6 inch text width.  Several tables were written with
fixed column widths that add up to more than the measure leaves after the
column separations, so the X column that carries the prose was squeezed to
a few points and the table either overflowed the margin or produced a
column that could not be set.

This script rewrites the column specifications so that the prose column
always has room:

  * the fixed columns are rescaled proportionally, inside a budget;
  * the X column is given the share that remains;
  * every prose column is set ragged right, through the P and Y column
    types declared in the preamble, so that a narrow column does not break
    a word across a line.

No cell content is changed.

    python3 build/fix_tables.py
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")

TEXTWIDTH_PT = 4.6 * 72.0            # 6 in trim, 0.80 inner, 0.60 outer
TABCOLSEP_PT = 6.0                   # the default: 12 pt per column gap

OPEN = "\\begin{tabularx}{\\textwidth}{"


def parse(spec: str) -> list[tuple[str, str]]:
    """Split a column specification into (kind, argument) pairs."""
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(spec):
        c = spec[i]
        if c == "@":
            j = spec.index("}", i)
            out.append(("@", spec[i:j + 1]))
            i = j + 1
            continue
        if c == ">":
            j = spec.index("}", i)
            out.append((">", spec[i:j + 1]))
            i = j + 1
            continue
        m = re.match(r"[pP]\{([^}]*)\}", spec[i:])
        if m:
            out.append(("p", m.group(1)))
            i += m.end()
            continue
        m = re.match(r"[XY]", spec[i:])
        if m:
            out.append(("X", ""))
            i += m.end()
            continue
        m = re.match(r"[rcl]", spec[i:])
        if m:
            out.append((m.group(0), ""))
            i += m.end()
            continue
        i += 1
    return out


def build(cols: list[tuple[str, str]]) -> str:
    """Render a column list back into a specification."""
    parts = []
    for kind, arg in cols:
        if kind == "p":
            parts.append(f"P{{{arg}}}")
        elif kind == "X":
            parts.append("Y")
        elif kind in ("r", "c", "l"):
            parts.append(kind)
        else:
            parts.append(arg)
    return "".join(parts)


def rebalance(spec: str) -> str:
    cols = parse(spec)
    n = len([k for k, _ in cols if k not in ("@", ">")])
    if n == 0:
        return spec

    n_fixed = sum(1 for k, _ in cols if k == "p")
    n_x = sum(1 for k, _ in cols if k == "X")
    n_nat = sum(1 for k, _ in cols if k in ("r", "c", "l"))

    # The space left after the column separations.
    gaps = max(0, n - 1) * 2 * TABCOLSEP_PT
    available = TEXTWIDTH_PT - gaps

    # The natural-width columns take what they take; 0.52 in is a working
    # estimate for a numeric column in this measure.
    natural = n_nat * 0.52 * 72.0

    # The share the prose column is given.
    if n_x == 0:
        x_share = 0.0
    elif n_x == 1:
        x_share = 0.42 if n_fixed == 1 else (0.40 if n_fixed == 2 else 0.34)
    else:
        x_share = 0.58

    x_total = available * x_share
    fixed_budget = available - x_total - natural

    widths = []
    for kind, arg in cols:
        if kind != "p":
            continue
        m = re.match(r"([\d.]+)\s*in", arg)
        widths.append(float(m.group(1)) * 72.0 if m else 72.0)

    total = sum(widths)
    if n_fixed and fixed_budget > 0:
        scale = fixed_budget / total if total else 1.0
        new = [max(0.60 * 72.0, w * scale) for w in widths]
        # If the floor pushed the total over budget, take it back off the
        # widest column until it fits.
        while sum(new) > fixed_budget and max(new) > 0.60 * 72.0:
            i = new.index(max(new))
            new[i] = max(0.60 * 72.0, new[i] - 0.5)
    else:
        new = widths

    out = []
    wi = 0
    for kind, arg in cols:
        if kind == "p":
            out.append(("p", f"{new[wi] / 72.0:.2f}in"))
            wi += 1
        else:
            out.append((kind, arg))
    return build(out)


def rewrite(text: str) -> tuple[str, int]:
    """Rewrite every tabularx column specification in ``text``."""
    out = []
    pos = 0
    count = 0
    while True:
        i = text.find(OPEN, pos)
        if i < 0:
            out.append(text[pos:])
            break
        out.append(text[pos:i])
        j = i + len(OPEN)
        depth = 1
        while j < len(text) and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        spec = text[i + len(OPEN):j]
        out.append(OPEN + rebalance(spec) + "}")
        pos = j + 1
        count += 1
    return "".join(out), count


def main() -> int:
    files = []
    for base in (SRC, os.path.join(SRC, "chapters")):
        for name in sorted(os.listdir(base)):
            if name.endswith(".tex"):
                files.append(os.path.join(base, name))

    total = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        new, n = rewrite(text)
        if n:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            print(f"{os.path.relpath(path, ROOT)}: {n} table(s) rebalanced")
            total += n
    print(f"{total} tables rebalanced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
