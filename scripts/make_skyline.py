"""Draw the pixel-art Istanbul skyline used by the app and the docs.

Galata Tower and houses on the left, the Bosphorus Bridge, a vapur, Kız Kulesi
and a mosque on the right, seagulls and clouds. Every pixel is a 1x1 SVG rect,
merged into horizontal runs so the file stays small.

Moving parts live in their own <g> layers and are animated with CSS inside the SVG,
so they also play when the file is used as a plain <img>: the vapur crosses the
Bosphorus, the water ripples and sparkles, gulls flap and drift, clouds drift. In
dark mode (the embedding page's color-scheme) the windows light up and a few twinkle.
Everything moves in whole pixels (steps()) and nothing moves under
prefers-reduced-motion: reduce; the first frame is the static picture.

    uv run scripts/make_skyline.py
"""

import math
import random
from pathlib import Path

W, H = 320, 110
WATER = 92  # first row of water
ROOT = Path(__file__).resolve().parent.parent

C = {
    "sky": None, "cloud": "#ffffff", "cloud2": "#cfe9fb",
    "water": "#2b7bd6", "water2": "#4b9be8", "water3": "#1f62b8", "foam": "#ffffff",
    "stone": "#e3d5b8", "stone2": "#c9b793", "stone3": "#a8956f", "roofgrey": "#3d5080", "roofgrey2": "#2c3c66",
    "win": "#3a3a4a", "red": "#c94a35", "red2": "#a83a2a",
    "wall1": "#f2c14e", "wall2": "#f6f1e6", "wall3": "#e9895b", "wall4": "#7fb3e6", "wall5": "#f4d9a8",
    "tree": "#3f9b4a", "tree2": "#2f7d3b", "tree3": "#5bb85f",
    "bridge": "#46598c", "bridge2": "#33456f", "cable": "#5c6fa3",
    "hull": "#ffffff", "hull2": "#d6dde8", "deck": "#2b2f3a", "funnel": "#f2c14e", "flag": "#e30a17",
    "dome": "#9aa5b8", "dome2": "#7d889c", "minaret": "#e8e1d2", "cap": "#5d6b85",
    "gull": "#5d6b85", "gull2": "#f2c14e",
}

# Each layer is its own pixel grid; to_svg() stacks them back to front:
# clouds, base (shores, bridge, water), ripples, sparkles, islet, gulls, ferry.
layers: dict[str, dict[tuple[int, int], str]] = {}
lights: dict[str, dict[tuple[int, int], str]] = {}  # night-time window lights, per layer
grid = layers.setdefault("base", {})
LIT = "#ffd66b"


def use(name):
    """Draw into another layer from here on."""
    global grid
    grid = layers.setdefault(name, {})


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H and c:
        grid[(x, y)] = C[c]
        if c == "win":
            name = next(k for k, v in layers.items() if v is grid)
            lights.setdefault(name, {})[(x, y)] = LIT


def rect(x, y, w, h, c):
    for i in range(x, x + w):
        for j in range(y, y + h):
            px(i, j, c)


def roof(x, y, w, c, c2=None):
    """Stepped triangular roof sitting on row y, w wide."""
    for k in range((w + 1) // 2):
        rect(x + k, y - k, w - 2 * k, 1, c if k % 2 == 0 or not c2 else c2)


def house(x, base, w, h, wall, windows=True):
    rect(x, base - h, w, h, wall)
    roof(x - 1, base - h - 1, w + 2, "red", "red2")
    if windows:
        for wy in range(base - h + 2, base - 2, 4):
            for wx in range(x + 1, x + w - 1, 3):
                px(wx, wy, "win")
                px(wx, wy + 1, "win")


def tree(x, base, r):
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + 1:
                px(x + dx, base - r + dy, "tree" if (dx + dy) % 3 else "tree2")
    px(x - 1, base - r - 1, "tree3")


def cloud(x, y, w):
    rect(x + 2, y, w - 4, 1, "cloud")
    rect(x, y + 1, w, 2, "cloud")
    rect(x + 3, y - 1, w // 3, 1, "cloud")
    rect(x, y + 3, w, 1, "cloud2")


GULL_UP = ["XX.....XX",
           ".XXX.XXX.",
           "...XoX..."]
GULL_DOWN = [".........",
             ".XXXoXXX.",
             "X.......X"]


def gull(x, y, shape=GULL_UP):
    for dy, row in enumerate(shape):
        for dx, ch in enumerate(row):
            if ch != ".":
                px(x + dx, y + dy, "gull" if ch == "X" else "gull2")


# --- sky -------------------------------------------------------------------------------------------
CLOUDS = [(40, 10, 22), (150, 6, 16), (196, 22, 12), (240, 10, 24)]
for i, c in enumerate(CLOUDS):
    use(f"cloud{i}")
    cloud(*c)
GULLS = [(70, 26), (180, 36), (110, 50)]
for i, (gx, gy) in enumerate(GULLS):
    use(f"gull{i}a")
    gull(gx, gy)
    use(f"gull{i}b")
    gull(gx, gy, GULL_DOWN)
use("base")

# --- left shore: houses, trees, Galata Tower --------------------------------------------------------
rect(0, 84, 118, WATER - 84, "stone2")
rect(0, 90, 120, 2, "stone3")
walls = ["wall1", "wall2", "wall3", "wall4", "wall5", "wall2", "wall1", "wall3", "wall4", "wall5"]
x = 0
random.seed(19122026)
while x < 112:
    w = random.choice([7, 8, 9, 10])
    h = random.choice([10, 12, 14, 16])
    base = 84 if x > 30 else 86
    if not 14 <= x <= 30:  # gap for the tower
        house(x, base, w, h, walls[(x // 7) % len(walls)])
    x += w + 1
for tx in (36, 64, 92, 108):
    tree(tx, 84, 3)
# Galata Tower: stone cylinder, arched window ring, conical cap
rect(17, 40, 12, 46, "stone")
rect(17, 40, 2, 46, "stone2")
rect(27, 40, 2, 46, "stone2")
for wy in (50, 60, 70):
    for wx in (20, 23, 26):
        rect(wx, wy, 1, 3, "win")
rect(15, 38, 16, 2, "stone3")
for wx in range(16, 30, 2):
    rect(wx, 34, 1, 4, "win")
rect(16, 33, 14, 1, "stone3")
for k in range(13):
    rect(16 + k // 2, 32 - k, 14 - k, 1, "roofgrey" if k % 3 else "roofgrey2")
px(23, 18, "roofgrey2")
px(23, 17, "cap")

# --- Bosphorus Bridge -------------------------------------------------------------------------------
L, R, TOP, DECK = 128, 236, 46, 76
for tx in (L, R):
    rect(tx, TOP, 4, WATER - TOP, "bridge")
    rect(tx + 3, TOP, 1, WATER - TOP, "bridge2")
    for cy in (TOP + 4, TOP + 16, DECK - 6):
        rect(tx - 1, cy, 6, 2, "bridge2")
rect(110, DECK, 150, 3, "bridge")
rect(110, DECK + 3, 150, 1, "bridge2")
for xx in range(L + 2, R + 3):  # main cable, a parabola between the towers
    t = (xx - (L + 2)) / (R - L)
    yy = int(TOP + 2 + (DECK - TOP - 6) * (1 - (2 * t - 1) ** 2))
    px(xx, yy, "cable")
    if xx % 4 == 0:
        rect(xx, yy + 1, 1, DECK - yy - 1, "cable")
for side, sx, ex in ((-1, 110, L), (1, R + 4, 260)):  # side spans
    for xx in range(sx, ex):
        t = (xx - sx) / max(1, ex - sx)
        yy = int(DECK - 2 - (DECK - TOP - 4) * (t if side < 0 else 1 - t))
        px(xx, yy, "cable")

# --- right shore: hill, mosque with minarets, houses -------------------------------------------------
random.seed(1453)
for xx in range(246, W):
    top = int(80 - 22 * math.sin(min(1.0, (xx - 246) / 60) * math.pi / 2))
    for yy in range(top, WATER):
        px(xx, yy, random.choice(["tree", "tree", "tree2", "tree3"]) if yy < top + 3 else
           random.choice(["tree2", "tree2", "tree", "tree2"]))
for tx in (252, 262, 314):
    tree(tx, 78 if tx < 260 else 70, 4)
house(266, 86, 9, 10, "wall2")
house(290, 86, 8, 12, "wall1")
house(301, 88, 9, 10, "wall3")
# mosque body and dome
rect(268, 54, 34, 12, "minaret")
for wx in range(271, 300, 4):
    rect(wx, 57, 1, 3, "win")
for k in range(10):
    w = int(2 * math.sqrt(max(0, 100 - k * k)))
    rect(285 - w // 2, 53 - k, w, 1, "dome" if k % 4 else "dome2")
for k in range(5):  # half domes
    w = int(2 * math.sqrt(max(0, 25 - k * k)))
    rect(274 - w // 2, 53 - k, w, 1, "dome2")
    rect(296 - w // 2, 53 - k, w, 1, "dome2")
rect(285, 40, 1, 4, "cap")
px(285, 39, "funnel")
for mx in (264, 305):
    rect(mx, 26, 3, 38, "minaret")
    rect(mx - 1, 38, 5, 1, "cap")
    for k in range(5):
        rect(mx + (1 if k > 1 else 0), 25 - k, 3 - (2 if k > 1 else 0), 1, "cap")

# --- water ------------------------------------------------------------------------------------------
rect(0, WATER, W, H - WATER, "water")
use("ripples")
random.seed(7)
for _ in range(90):
    xx, yy = random.randrange(W), random.randrange(WATER + 1, H)
    rect(xx, yy, random.choice([3, 4, 6]), 1, random.choice(["water2", "water2", "water3"]))
# sparkles: hidden in the still picture; they blink in three groups (fewer repaints than one by one)
SPARKLES = []
while len(SPARKLES) < 15:
    xx, yy = random.randrange(4, W - 4), random.randrange(WATER + 2, H - 1)
    if not 208 <= xx <= 240:  # keep clear of the islet
        SPARKLES.append((xx, yy, random.choice([2, 3])))

# Kız Kulesi on its islet
use("islet")
rect(212, 98, 26, 4, "stone3")
rect(214, 96, 22, 2, "stone2")
rect(219, 80, 10, 16, "stone")
rect(221, 84, 2, 3, "win")
rect(225, 84, 2, 3, "win")
rect(218, 79, 12, 1, "stone3")
rect(221, 72, 6, 7, "stone")
for k in range(6):
    rect(221 + k // 2, 71 - k, 6 - k, 1, "roofgrey")
rect(230, 90, 5, 6, "wall2")
roof(229, 89, 7, "red")
px(224, 64, "flag")
px(225, 64, "flag")
px(224, 65, "flag")

# Vapur (city ferry)
use("ferry")
FX, FY = 54, 100
rect(FX, FY, 46, 4, "hull")
rect(FX + 2, FY + 4, 42, 2, "hull2")
rect(FX, FY + 1, 46, 1, "deck")
rect(FX + 6, FY - 5, 32, 5, "hull")
for wx in range(FX + 8, FX + 36, 3):
    rect(wx, FY - 3, 2, 2, "win")
rect(FX + 12, FY - 8, 22, 3, "hull2")
rect(FX + 20, FY - 13, 4, 5, "funnel")
rect(FX + 20, FY - 13, 4, 1, "deck")
rect(FX + 12, FY - 8, 22, 1, "deck")
rect(FX + 1, FY - 6, 1, 6, "deck")
rect(FX + 2, FY - 6, 3, 2, "flag")
rect(FX - 4, FY + 5, 6, 1, "foam")
rect(FX + 44, FY + 5, 5, 1, "foam")


# Ferry: enters at the left edge, leaves at the right, wraps around. The negative delay makes the
# first frame the drawn position, so a still image (or reduced motion) shows the original picture.
FERRY_FROM, FERRY_TO, FERRY_S = -(FX + 52), W - FX + 6, 100
FERRY_DELAY = FERRY_S * (0 - FERRY_FROM) / (FERRY_TO - FERRY_FROM)

STYLE = f"""
.gb,.sp,.lit{{opacity:0}}
@media (prefers-color-scheme:dark){{.lit{{opacity:1}}.cl{{opacity:.6}}}}
@media (prefers-reduced-motion:no-preference){{
.fe{{animation:fe {FERRY_S}s steps({FERRY_TO - FERRY_FROM}) -{FERRY_DELAY + .05:.2f}s infinite}}
@keyframes fe{{from{{transform:translateX({FERRY_FROM}px)}}to{{transform:translateX({FERRY_TO}px)}}}}
.bob{{animation:bob 2.4s steps(1) infinite}}
@keyframes bob{{50%{{transform:translateY(1px)}}}}
.rp{{animation:rp 7s steps(1) infinite}}
@keyframes rp{{25%{{transform:translateX(1px)}}50%{{transform:translateX(2px)}}75%{{transform:translateX(1px)}}}}
.sp{{animation:sp 6s steps(1) infinite}}
@keyframes sp{{0%{{opacity:0}}82%{{opacity:1}}90%{{opacity:0}}}}
.cl{{animation:cl 40s steps(10) infinite alternate}}
@keyframes cl{{to{{transform:translateX(10px)}}}}
.gl{{animation:gl 16s steps(8) infinite alternate}}
@keyframes gl{{50%{{transform:translate(8px,-2px)}}to{{transform:translate(16px,1px)}}}}
.ga{{animation:ga 5s steps(1) infinite}}
@keyframes ga{{45%{{opacity:0}}55%{{opacity:1}}}}
.gb{{animation:gb 5s steps(1) infinite}}
@keyframes gb{{45%{{opacity:1}}55%{{opacity:0}}}}
@media (prefers-color-scheme:dark){{
.tw{{animation:tw 5s steps(1) infinite}}
@keyframes tw{{60%{{opacity:.15}}75%{{opacity:1}}}}}}
}}
"""


def runs(cells: dict[tuple[int, int], str]) -> str:
    out = []
    for y in range(H):
        x = 0
        while x < W:
            c = cells.get((x, y))
            if c is None:
                x += 1
                continue
            start = x
            while x < W and cells.get((x, y)) == c:
                x += 1
            out.append(f'<rect x="{start}" y="{y}" width="{x - start}" height="1" fill="{c}"/>')
    return "".join(out)


def lit(name: str) -> str:
    """Window lights for one layer; every 4th window twinkles, in three groups out of phase."""
    cells = {p: c for p, c in lights.get(name, {}).items() if layers[name].get(p) == C["win"]}  # not painted over
    if not cells:
        return ""
    keys = sorted(cells, key=lambda p: (p[0], p[1]))
    windows: list[list[tuple[int, int]]] = []  # group pixels into windows (touching columns)
    for p in keys:
        if windows and any(abs(p[0] - q[0]) <= 1 and abs(p[1] - q[1]) <= 1 for q in windows[-1]):
            windows[-1].append(p)
        else:
            windows.append([p])
    steady = {p: LIT for i, w in enumerate(windows) if i % 4 for p in w}
    out = runs(steady)
    for k in range(3):
        cells = {p: LIT for i, w in enumerate(windows) if i % 4 == 0 and (i // 4) % 3 == k for p in w}
        if cells:
            out += f'<g class="tw" style="animation-delay:-{1.7 * k:.1f}s">{runs(cells)}</g>'
    return f'<g class="lit">{out}</g>'


def to_svg() -> str:
    body = []
    for i in range(len(CLOUDS)):
        body.append(f'<g class="cl" style="animation-duration:{34 + 9 * i}s;animation-delay:-{7 * i}s">'
                    f'{runs(layers[f"cloud{i}"])}</g>')
    body.append(runs(layers["base"]) + lit("base"))
    body.append(f'<g class="rp">{runs(layers["ripples"])}</g>')
    for k in range(3):
        rects = "".join(f'<rect x="{sx}" y="{sy}" width="{sw}" height="1" fill="#ffffff"/>' for sx, sy, sw in SPARKLES[k::3])
        body.append(f'<g class="sp" style="animation-delay:-{2 * k}s">{rects}</g>')
    body.append(runs(layers["islet"]) + lit("islet"))
    for i in range(len(GULLS)):
        body.append(f'<g class="gl" style="animation-duration:{24 + 6 * i}s;animation-delay:-{5 * i}s">'
                    f'<g class="ga" style="animation-delay:-{1.7 * i:.1f}s">{runs(layers[f"gull{i}a"])}</g>'
                    f'<g class="gb" style="animation-delay:-{1.7 * i:.1f}s">{runs(layers[f"gull{i}b"])}</g></g>')
    body.append(f'<g class="fe"><g class="bob">{runs(layers["ferry"])}</g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="crispEdges" '
            f'role="img" aria-label="Pixel-art Istanbul skyline: Galata Tower, Bosphorus Bridge, a ferry, '
            f'Maiden\'s Tower and a mosque"><style>{" ".join(STYLE.split())}</style>' + "".join(body) + "</svg>\n")


if __name__ == "__main__":
    svg = to_svg()
    for out in (ROOT / "app/static/img/skyline.svg", ROOT / "docs/overrides/assets/images/skyline.svg"):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg)
        print(f"{out.relative_to(ROOT)}  {len(svg) / 1024:.0f} KB")
