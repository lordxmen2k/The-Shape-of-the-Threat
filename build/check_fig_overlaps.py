#!/usr/bin/env python3
"""
Geometric overlap gate for the book's figures.

The owner asked for one thing: "check the figures just to see there is no
overlapping happening".  Eyeballing fourteen figures at print size finds some
collisions and misses others, so this script measures them instead.

It rebuilds every figure from build/make_figures.py (without writing PDFs),
draws each canvas, and then tests, in display coordinates:

  * every text artist against every other text artist, across axes, so that
    the titles of two adjacent panels cannot collide unnoticed;
  * every text artist against every drawn line, marker, spine and annotation
    arrow of the same axes;
  * every text artist against the boundary of the figure canvas and of its
    own axes, so that a label cannot sit off the page or over the frame.

A line is sampled densely along its path and clipped to the axes rectangle
before testing, because a curve that runs outside the axes is not drawn
there.  A collision is a sample point inside the text's bounding box grown
by a small margin, or two boxes separated by less than the margin.

Exit status is non-zero when anything collides, so this can gate a build.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_figures as MF  # noqa: E402

# Text that is deliberately set on top of, or immediately beside, a feature
# it names.  Each entry is (figure name, substring of the text, what it
# touches).  Keep this list short and justify every entry.
ALLOWED: list[tuple[str, str, str]] = []

GAP = 2.5        # pixels: two boxes closer than this read as touching
PAD = 1.0        # pixels of slack around a text box


def _densify(pts):
    """Insert intermediate points so a straight segment cannot skip a box."""
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        n = int(min(max(2, np.hypot(*(b - a)) // 2), 400))
        for t in np.linspace(0.0, 1.0, n):
            out.append(a + t * (b - a))
    return out


def _clip_segment(a, b, rect):
    """Liang-Barsky clip of the segment a-b to an axis-aligned rectangle."""
    x0, y0 = float(a[0]), float(a[1])
    x1, y1 = float(b[0]), float(b[1])
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - rect.x0), (dx, rect.x1 - x0),
                 (-dy, y0 - rect.y0), (dy, rect.y1 - y0)):
        if p == 0.0:
            if q < 0.0:
                return None
        else:
            r = q / p
            if p < 0.0:
                if r > t1:
                    return None
                t0 = max(t0, r)
            else:
                if r < t0:
                    return None
                t1 = min(t1, r)
    return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)


def _path_points(artist, trans, rect=None):
    """Display-coordinate sample points along an artist's drawn path.

    The path is clipped to the rectangle first, so that a line running far
    outside the axes is sampled where it is actually drawn and a wide span
    cannot hide a collision behind sparse sampling.
    """
    try:
        verts = artist.get_path().vertices
    except Exception:
        return []
    if len(verts) == 0:
        return []
    pts = np.asarray(verts, dtype=float)
    try:
        pts = trans.transform(pts)
    except Exception:
        return []
    if not np.all(np.isfinite(pts)):
        return []
    if len(pts) == 1:
        return [pts[0]]
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        seg = (a, b)
        if rect is not None:
            seg = _clip_segment(a, b, rect)
            if seg is None:
                continue
        out.extend(_densify([seg[0], seg[1]]))
    return out


def _marker_points(artist, trans):
    """Display-coordinate points for a scatter-style marker artist."""
    try:
        off = artist.get_offsets()
    except Exception:
        return []
    if off is None or len(off) == 0:
        return []
    arr = np.atleast_2d(np.asarray(off, dtype=float))
    try:
        arr = trans.transform(arr)
    except Exception:
        return []
    return [p for p in arr]


def _arrow_points(patch, trans):
    """Display-coordinate points along an annotation arrow."""
    try:
        path = patch.get_path()
        verts = path.vertices
    except Exception:
        return []
    if len(verts) == 0:
        return []
    pts = np.asarray(verts, dtype=float)
    try:
        pts = patch.get_transform().transform(pts)
    except Exception:
        return []
    if len(pts) == 1:
        return [pts[0]]
    return _densify(pts)


def _all_texts(ax):
    """Every piece of text an axes carries.

    Returns (text, kind) pairs.  kind is "note" for an annotation drawn on
    the data, and "frame" for a title, which sits outside the axes by
    design and so is exempt from the outside-the-axes test.
    """
    out = [(t, "note") for t in ax.texts]
    for holder in (ax, ax._left_title, ax._right_title):
        t = getattr(holder, "get_title", lambda: "")()
        if t:
            out.append((holder.title, "frame"))
    return [(t, k) for t, k in out if t.get_text().strip()]


def _bbox_intersect(b1, b2):
    """True when two boxes touch at all, containment included."""
    return not (b1.x1 < b2.x0 or b2.x1 < b1.x0 or
                b1.y1 < b2.y0 or b2.y1 < b1.y0)


def _gap(a, b):
    """Separation between two boxes; negative means they overlap."""
    dx = max(a.x0 - b.x1, b.x0 - a.x1)
    dy = max(a.y0 - b.y1, b.y0 - a.y1)
    if dx >= 0 and dy >= 0:
        return max(dx, dy)      # separated diagonally
    if dx >= 0:
        return dx              # separated horizontally only
    if dy >= 0:
        return dy              # separated vertically only
    return max(dx, dy)         # they overlap


def _hit_points(a, b, tol=1.0):
    """True when any point of a lies within tol of any point of b."""
    if not a or not b:
        return False
    for (x1, y1) in a:
        for (x2, y2) in b:
            if abs(x1 - x2) <= tol and abs(y1 - y2) <= tol:
                return True
    return False


def _rect_points(box):
    """The four corners of a display-coordinate rectangle."""
    return [(box.x0, box.y0), (box.x1, box.y0),
            (box.x1, box.y1), (box.x0, box.y1)]


def _hit(box, pts, clip=None):
    for (x, y) in pts:
        if clip is not None:
            if not (clip.x0 <= x <= clip.x1 and clip.y0 <= y <= clip.y1):
                continue        # the curve is not drawn here
        if (box.x0 - PAD <= x <= box.x1 + PAD and
                box.y0 - PAD <= y <= box.y1 + PAD):
            return (x, y)
    return None


def check_figure(fig, name):
    problems = []
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas_w, canvas_h = fig.canvas.get_width_height()

    all_boxes = []      # (text, bbox, axes, kind)
    from matplotlib.text import Text
    for ax in fig.axes:
        for t, kind in _all_texts(ax):
            try:
                # The base Text method gives the text alone; an Annotation
                # would otherwise report a box that includes its arrow.
                bb = Text.get_window_extent(t, renderer)
            except Exception:
                continue
            all_boxes.append((t, bb, ax, kind))

    # ---- text against text, across the whole figure ----------------------
    for i in range(len(all_boxes)):
        for j in range(i + 1, len(all_boxes)):
            t1, b1 = all_boxes[i][0], all_boxes[i][1]
            t2, b2 = all_boxes[j][0], all_boxes[j][1]
            if _gap(b1, b2) < GAP:
                problems.append((name, "text/text",
                                 f"{t1.get_text()[:30]!r} <-> "
                                 f"{t2.get_text()[:30]!r}"))

    # ---- text against geometry, per axes ---------------------------------
    for ax in fig.axes:
        trans = ax.transData
        clip = ax.get_window_extent(renderer)

        geometry = []      # (label, points)
        arrows = []        # (patch, points)
        for artist in ax.lines:
            geometry.append((artist.get_label(),
                             _path_points(artist, trans, clip)))
        for artist in ax.spines.values():
            if artist.get_visible():
                geometry.append((f"spine:{artist.get_label()}",
                                 _path_points(artist, artist.get_transform(), clip)))
        for artist in ax.collections:
            geometry.append((artist.get_label(),
                             _marker_points(artist, trans)))
        for patch in ax.patches:
            from matplotlib.patches import FancyArrowPatch
            if isinstance(patch, FancyArrowPatch):
                geometry.append(("annotation arrow",
                                 _arrow_points(patch, trans)))
                arrows.append((patch, _arrow_points(patch, trans)))

        # A legend that sits on top of a curve is an overlap too.
        legend = ax.get_legend()
        legend_box = None
        if legend is not None:
            try:
                legend_box = legend.get_window_extent(renderer)
            except Exception:
                legend_box = None

        for t, bb, _ax, _kind in all_boxes:
            for label, pts in geometry:
                if not pts:
                    continue
                if _hit(bb, pts, clip) is None:
                    continue
                allowed = any(
                    a[0] == name and a[1] in t.get_text() and a[2] in label
                    for a in ALLOWED
                )
                if allowed:
                    continue
                problems.append((name, "text/curve",
                                 f"{t.get_text()[:34]!r} over {label[:34]!r} "
                                 f"[{bb.x0:.0f},{bb.x1:.0f}]x"
                                 f"[{bb.y0:.0f},{bb.y1:.0f}]"))

        if legend_box is not None:
            for label, pts in geometry:
                if not pts:
                    continue
                if _hit(legend_box, pts, clip) is None:
                    continue
                problems.append((name, "legend/curve",
                                 f"the legend sits on {label[:30]!r} "
                                 f"[{legend_box.x0:.0f},{legend_box.x1:.0f}]x"
                                 f"[{legend_box.y0:.0f},{legend_box.y1:.0f}]"))

        # A leader line that runs across a curve is a crossing, not a
        # collision, but it is worth seeing.
        for patch, apts in arrows:
            for label, pts in geometry:
                if label == "annotation arrow" or not pts:
                    continue
                if _hit_points(apts, pts):
                    problems.append((name, "arrow/curve",
                                     f"a leader crosses {label[:30]!r}"))

    # ---- text against a legend ------------------------------------------
    for ax in fig.axes:
        legend = ax.get_legend()
        if legend is None:
            continue
        try:
            lb = legend.get_window_extent(renderer)
        except Exception:
            continue
        for t, bb, _ax, kind in all_boxes:
            if kind != "note":
                continue
            if _bbox_intersect(bb, lb):
                problems.append((name, "text/legend",
                                 f"{t.get_text()[:34]!r} over the legend"))

    # ---- text that falls outside the axes it belongs to ------------------
    for t, bb, ax, kind in all_boxes:
        if kind != "note":
            continue
        frame = ax.get_window_extent(renderer)
        if bb.x1 < frame.x0 or bb.x0 > frame.x1 or \
                bb.y1 < frame.y0 or bb.y0 > frame.y1:
            problems.append((name, "off-axes",
                             f"{t.get_text()[:34]!r} lies outside its axes"))
    return problems


def main() -> int:
    built = MF.build_all(save=False)
    all_problems = []
    for fig, name in built:
        all_problems.extend(check_figure(fig, name))

    if not all_problems:
        print(f"[OK] {len(built)} figures: no text overlaps any curve, "
              f"marker, arrow, spine or other text.")
        return 0

    for name, kind, desc in all_problems:
        print(f"[FAIL] {name:24s} {kind:11s} {desc}")
    print()
    print(f"{len(all_problems)} overlap(s) found in {len(built)} figures.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
