#!/usr/bin/env python3
"""
The source artwork for the cover of "The Shape of the Threat".

This is the one raster artefact in the book that is not a figure: the
original artwork that the cover plates are cropped and scrimmed from.  It is
generated here rather than licensed, so that the cover is original work and
carries no attribution requirement.

The composition is flat by design.  There is no book, no spine, no binding,
no page edges and no perspective: the artwork is a single flat field, edge
to edge.

The subject is the book's own subject.  The large body is drawn as a
delay-Doppler radar image --- concentric range contours inside an irregular
silhouette --- because that is what the measurement the book argues for
actually looks like, and because the silhouette is the thing that carries
the title.  Below it the lunar surface runs across the foot of the page as a
dark horizon with a thin rim of sunlight, and three reflector nodes sit on
it joined by the measured baseline that the book requires.  The two halves of
the cover are the two halves of the argument: the shape, and the platform
that resolves it.

Output: figures/cover_art.jpg at 2400 x 3600 px (400 DPI at the 6 x 9 trim).
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

W, H = 2400, 3600
SS = 2                      # supersampling factor, for antialiasing

INK = np.array([0x08, 0x0B, 0x14], dtype="float32")
DEEP = np.array([0x05, 0x06, 0x0D], dtype="float32")
PANEL = np.array([0x12, 0x18, 0x28], dtype="float32")
GOLD = np.array([0xE8, 0xB8, 0x5C], dtype="float32")
AMBER = np.array([0x6F, 0xA3, 0xD6], dtype="float32")
TXT = np.array([0xE6, 0xE9, 0xF0], dtype="float32")
WARM = np.array([0xC9, 0x70, 0x5A], dtype="float32")

# The cover style is drawn from a fixed pool with a seed derived from the
# title, so that the draw is reproducible and recorded rather than a taste.
STYLE_POOL = [
    "watercolour", "swiss", "blueprint", "holographic", "vaporwave",
    "minimalist geometric", "retro sci-fi pulp", "woodcut", "isometric 3D",
    "paper-cut layers", "vintage NASA poster", "cyberpunk neon",
    "art deco", "ink and line art",
]


def draw_record() -> dict:
    import hashlib
    seed_material = "The-Shape-of-the-Threat"
    seed = int(hashlib.sha256(seed_material.encode()).hexdigest()[:8], 16)
    index = seed % len(STYLE_POOL)
    return {
        "title": "The Shape of the Threat",
        "seed_material": seed_material,
        "seed": seed,
        "pool_size": len(STYLE_POOL),
        "drawn_index": index,
        "drawn_style": STYLE_POOL[index],
        "style_interpretation":
            "Vintage NASA poster: flat fields, one accent, a horizon line "
            "and a single astronomical subject, with technical type set "
            "over the plate.",
        "draw_order": [
            "space gradient", "milky way band", "star field", "sun glow",
            "asteroid range-Doppler image", "lunar horizon", "surface rim "
            "light", "array nodes and baseline", "dust scatter",
        ],
    }


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def space_field(rng):
    """The deep field: a vertical gradient with a faint galactic band."""
    t = np.linspace(0.0, 1.0, H, dtype="float32")[:, None]
    base = DEEP[None, None, :] * (1.0 - t[:, :, None]) + INK[None, None, :] * t[:, :, None]
    base = np.repeat(base, W, axis=1)

    yy, xx = np.mgrid[0:H, 0:W].astype("float32")

    # A soft galactic band running from the upper right to the lower left.
    d = np.abs((xx / W) * 0.72 + (yy / H) * 0.55 - 0.62) / 0.30
    band = np.exp(-d ** 2)
    noise = rng.random((H // 40, W // 40)).astype("float32")
    noise = np.array(Image.fromarray((noise * 255).astype("uint8"))
                     .resize((W, H), Image.BICUBIC), dtype="float32") / 255.0
    noise = np.array(Image.fromarray((noise * 255).astype("uint8"))
                     .filter(ImageFilter.GaussianBlur(9)), dtype="float32") / 255.0
    band = band * (0.55 + 0.45 * noise)
    base += band[:, :, None] * (PANEL[None, None, :] * 0.85 + TXT[None, None, :] * 0.022)

    # The Sun is off the left edge: a broad, low glow.
    glow = np.exp(-(((xx / W) + 0.05) ** 2) / 0.30) * np.exp(-((yy / H - 0.30) ** 2) / 0.34)
    base += glow[:, :, None] * (GOLD[None, None, :] * 0.055 + WARM[None, None, :] * 0.020)

    return np.clip(base, 0, 255)


def star_field(img: Image.Image, rng, n=2600):
    """Stars, with a few bright ones carrying diffraction spikes."""
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H * 0.72)
        # Slightly fewer stars low down, where the dust band thickens.
        if rng.random() > 0.35 + 0.65 * (1.0 - y / (H * 0.72)):
            continue
        r = rng.uniform(0.7, 2.4)
        b = int(rng.uniform(40, 210) * (1.0 - 0.4 * (y / H)))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 14), 255))

    for _ in range(22):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H * 0.55)
        r = rng.uniform(3.0, 6.0)
        a = int(rng.uniform(120, 210))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(240, 240, 250, a))
        L = r * rng.uniform(4.0, 7.5)
        w = max(1, int(r * 0.28))
        draw.line([x - L, y, x + L, y], fill=(230, 232, 245, int(a * 0.55)), width=w)
        draw.line([x, y - L, x, y + L], fill=(230, 232, 245, int(a * 0.55)), width=w)
    return img


def asteroid_polygon(cx, cy, r, n=1400):
    """An irregular closed outline: a few harmonics and two craters."""
    th = np.linspace(0.0, 2.0 * np.pi, n)
    rad = (1.0
           + 0.085 * np.sin(3.0 * th + 0.45)
           + 0.052 * np.sin(5.0 * th + 1.95)
           + 0.030 * np.sin(7.0 * th + 3.05)
           + 0.018 * np.sin(11.0 * th + 0.80))
    # Two shallow craters bitten out of the limb.
    for ct, cw, cd in ((2.05, 0.30, 0.085), (4.35, 0.22, 0.060)):
        rad -= cd * np.exp(-((np.cos(th - ct)) ** 2) / (2.0 * cw ** 2))
    pts = [(cx + r * rad[i] * np.cos(th[i]), cy + r * rad[i] * 0.92 * np.sin(th[i]))
           for i in range(n)]
    return pts


def draw_asteroid(img: Image.Image, rng):
    """The body, as a delay-Doppler image: range contours in a silhouette."""
    cx, cy = W * 0.605, H * 0.470
    R = W * 0.268
    outer = asteroid_polygon(cx, cy, R)

    # --- the body itself: a lit solid, lit from the left, falling into
    #     shadow toward the right-hand limb.
    mask = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(mask).polygon([(x * SS, y * SS) for x, y in outer], fill=255)
    mask = mask.resize((W, H), Image.LANCZOS)

    yy, xx = np.mgrid[0:H, 0:W].astype("float32")
    lit = np.clip(1.28 - 1.05 * (xx / W), 0.0, 1.0) ** 1.25
    lit = lit * (0.55 + 0.45 * np.clip(1.0 - (yy - (cy - R)) / (2.0 * R), 0, 1))
    body = (INK[None, None, :] * 1.0
            + np.array([0x2A, 0x2E, 0x3C], dtype="float32")[None, None, :] * lit[:, :, None]
            + GOLD[None, None, :] * (lit ** 3.2)[:, :, None] * 0.30)
    body = np.clip(body, 0, 255).astype("uint8")
    layer = Image.fromarray(body, "RGB").convert("RGBA")
    layer.putalpha(mask)
    img.alpha_composite(layer)

    # --- the range contours, drawn on a supersampled overlay so that the
    #     lines are antialiased like the silhouette they sit inside.
    line = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(line, "RGBA")

    n_contours = 14
    for i in range(n_contours, 0, -1):
        f = i / n_contours
        pts = [(cx + (x - cx) * f, cy + (y - cy) * f) for x, y in outer]
        alpha = int(46 + 185 * (1.0 - f) ** 1.55)
        d.polygon([(x * SS, y * SS) for x, y in pts],
                  outline=(236, 190, 96, alpha), width=max(1, int(2.0 * SS)))

    # A handful of craters drawn as small offset contours.
    for _ in range(7):
        a = rng.uniform(0, 2 * np.pi)
        rr = rng.uniform(0.16, 0.66) * R
        cr = rng.uniform(0.018, 0.042) * R
        ccx, ccy = cx + rr * np.cos(a), cy + rr * np.sin(a) * 0.92
        for k in (1.0, 0.62):
            box = [(ccx - cr * k) * SS, (ccy - cr * k * 0.9) * SS,
                   (ccx + cr * k) * SS, (ccy + cr * k * 0.9) * SS]
            d.ellipse(box, outline=(236, 190, 96, 78), width=max(1, int(1.5 * SS)))

    # The sunward rim, bright where the light grazes the limb.
    pts = [(x * SS, y * SS) for x, y in outer]
    d.line(pts + [pts[0]], fill=(248, 210, 130, 235), width=int(3.0 * SS))

    line = line.resize((W, H), Image.LANCZOS)
    img.alpha_composite(line)

    # A soft glow around the body: scattered light, not an outline.
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse(
        [cx - R * 1.30, cy - R * 1.30, cx + R * 1.30, cy + R * 1.30], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    halo = Image.new("RGBA", (W, H), (232, 184, 92, 0))
    halo.putalpha(glow.point(lambda v: int(v * 0.42)))
    img.alpha_composite(halo)
    return img


def draw_horizon(img: Image.Image, rng):
    """The lunar surface: a dark curve across the foot of the page."""
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")

    hz = H * 0.730

    def surf(x):
        return (hz
                + 30.0 * np.sin(x / 620.0 + 0.7)
                + 15.0 * np.sin(x / 245.0 + 2.1)
                + 7.0 * np.sin(x / 96.0 + 4.4))

    pts = [(x * SS, surf(x) * SS) for x in np.arange(0, W + 24, 24)]
    poly = pts + [(W * SS, H * SS), (0, H * SS)]
    d.polygon(poly, fill=(13, 15, 23, 255))

    # Foreground craters: dark bowls with a lit upper rim.
    for _ in range(34):
        x = rng.uniform(-80, W + 80)
        y = surf(x) + rng.uniform(30, 2600)
        r = rng.uniform(26, 240)
        sq = rng.uniform(0.20, 0.42)
        d.ellipse([(x - r) * SS, (y - r * sq) * SS,
                   (x + r) * SS, (y + r * sq) * SS],
                  fill=(7, 9, 15, 255))
        d.arc([(x - r) * SS, (y - r * sq) * SS,
               (x + r) * SS, (y + r * sq) * SS],
              start=185, end=355, fill=(198, 156, 82, 135), width=int(2.0 * SS))

    # Scattered rocks along the plain.
    for _ in range(260):
        x = rng.uniform(0, W)
        y = surf(x) + rng.uniform(6, 1400)
        r = rng.uniform(2.5, 9.0)
        d.ellipse([(x - r) * SS, (y - r * 0.6) * SS,
                   (x + r) * SS, (y + r * 0.6) * SS],
                  fill=(4, 5, 9, 255))

    # The rim of sunlight on the far horizon.
    d.line(pts, fill=(236, 190, 100, 215), width=int(3.0 * SS))

    layer = layer.resize((W, H), Image.LANCZOS)
    img.alpha_composite(layer)
    return img, hz


def draw_array(img: Image.Image, hz):
    """Three reflector nodes on the surface, joined by the measured baseline."""
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")

    xs = [W * 0.180, W * 0.505, W * 0.830]
    ys = [hz + 210, hz + 168, hz + 224]

    # The baseline: a thin measured line with end ticks.
    d.line([(xs[0] * SS, ys[0] * SS), (xs[1] * SS, ys[1] * SS),
            (xs[2] * SS, ys[2] * SS)],
           fill=(122, 176, 228, 175), width=int(2.6 * SS))
    for x, y in zip(xs, ys):
        d.line([(x * SS, (y - 26) * SS), (x * SS, (y + 26) * SS)],
               fill=(122, 176, 228, 215), width=int(2.6 * SS))

    # Each node: a reflector dish on a short mast.
    for x, y in zip(xs, ys):
        r = 52.0
        # the dish, seen edge-on and tilted
        d.ellipse([(x - r) * SS, (y - r * 0.58) * SS,
                   (x + r) * SS, (y + r * 0.58) * SS],
                  fill=(16, 19, 28, 255),
                  outline=(238, 198, 112, 245), width=int(2.8 * SS))
        d.line([(x - r * 0.62) * SS, (y - r * 0.30) * SS,
                (x + r * 0.62) * SS, (y + r * 0.30) * SS],
               fill=(238, 198, 112, 120), width=int(1.8 * SS))
        # the mast
        d.line([(x * SS, (y + r * 0.30) * SS), (x * SS, (y + 78) * SS)],
               fill=(150, 162, 188, 215), width=int(2.6 * SS))
        d.ellipse([(x - 8) * SS, (y + 72) * SS, (x + 8) * SS, (y + 88) * SS],
                  fill=(238, 198, 112, 240))

    layer = layer.resize((W, H), Image.LANCZOS)
    img.alpha_composite(layer)
    return img


def dust_scatter(img: Image.Image, rng):
    """A thin scatter of ejecta above the horizon."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    for _ in range(900):
        x = rng.uniform(0, W)
        y = rng.uniform(H * 0.48, H * 0.66)
        r = rng.uniform(0.6, 2.6)
        a = int(rng.uniform(20, 110))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(198, 206, 224, a))
    layer = layer.filter(ImageFilter.GaussianBlur(0.5))
    img.alpha_composite(layer)
    return img


def main():
    rng = np.random.default_rng(20261124)

    base = space_field(rng)
    img = Image.fromarray(base.astype("uint8"), "RGB").convert("RGBA")

    img = star_field(img, rng)
    img = draw_asteroid(img, rng)
    img, hz = draw_horizon(img, rng)
    img = draw_array(img, hz)
    img = dust_scatter(img, rng)

    out = img.convert("RGB")
    out.save(FIG / "cover_art.jpg", quality=93, subsampling=0, dpi=(400, 400))

    record = draw_record()
    (ROOT / "research").mkdir(parents=True, exist_ok=True)
    (ROOT / "research" / "cover_draw.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("cover style drawn:", record["drawn_style"], "(seed", record["seed"], ")")
    print("wrote", (FIG / "cover_art.jpg").relative_to(ROOT), out.size)


if __name__ == "__main__":
    main()
