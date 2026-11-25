#!/usr/bin/env python3
"""
Print the display geometry of one figure.

    python3 build/probe_fig.py fig_two_station

For every axes it prints the rectangle of the plotting area, the position of
each visible spine, the bounding box of every piece of text, and the display
extent of every drawn line.  That is what is needed to place a label where
it cannot collide with anything.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_figures as MF  # noqa: E402


def main() -> int:
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    built = MF.build_all(save=False)
    for fig, name in built:
        if want and not name.startswith(want):
            continue
        print("=" * 78)
        print(name, " canvas", fig.canvas.get_width_height())
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        for ai, ax in enumerate(fig.axes):
            fr = ax.get_window_extent(r)
            print(f"-- axes {ai}: x[{fr.x0:.0f},{fr.x1:.0f}] "
                  f"y[{fr.y0:.0f},{fr.y1:.0f}]")
            for side, sp in ax.spines.items():
                if not sp.get_visible():
                    continue
                d = sp.get_transform().transform(sp.get_path().vertices)
                print(f"   spine {side:6s} x[{d[:,0].min():.0f},{d[:,0].max():.0f}] "
                      f"y[{d[:,1].min():.0f},{d[:,1].max():.0f}]")
            for t in list(ax.texts) + [ax.title]:
                if not t.get_text().strip():
                    continue
                bb = t.get_window_extent(r)
                print(f"   text {t.get_text()[:38]!r:42s} "
                      f"x[{bb.x0:.0f},{bb.x1:.0f}] y[{bb.y0:.0f},{bb.y1:.0f}] "
                      f"pos={t.get_position()}")
            for i, ln in enumerate(ax.lines):
                v = ln.get_path().vertices
                if len(v) == 0:
                    continue
                d = ax.transData.transform(np.asarray(v, dtype=float))
                print(f"   line {i:2d} {ln.get_label()[:22]!r:26s} "
                      f"x[{d[:,0].min():.0f},{d[:,0].max():.0f}] "
                      f"y[{d[:,1].min():.0f},{d[:,1].max():.0f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
