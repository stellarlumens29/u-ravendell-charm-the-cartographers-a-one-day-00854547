#!/usr/bin/env python3
"""make.fun entry: Charm the Cartographers: A One Day Treasure Map Sprint.

Draws one original treasure map of a fictional island — the Isle of
Giggles — with seven labelled places, a compass rose, a dashed route to
a big red X, a sea serpent and a scale bar. Drawn entirely from code:
Python standard library only (zlib PNG encoder written by hand, 5x7
bitmap font defined inline), no network, no randomness beyond a fixed
seed, no timestamps. Running twice produces byte-identical output.

Bounty: https://make.fun/bounty/u-ravendell-charm-the-cartographers-a-one-day-00854547
Gate: /output/entry.png, whole PNG, at most 1 MiB, at most 1024x1024.
"""

import hashlib
import math
import os
import random
import struct
import sys
import zlib

W = H = 1024
SEED = 20261124

# --- palette ---
PARCH_TOP = (238, 220, 172)
PARCH_BOT = (226, 205, 150)
SAND = (226, 200, 140)
GREEN = (170, 186, 124)
GREEN_DK = (120, 140, 88)
INK = (74, 52, 30)          # label ink
COAST = (120, 90, 50)       # coastline
SEA = (125, 180, 195)       # lagoon / cove water
SEA_DK = (110, 130, 125)    # wave squiggles
RED = (178, 52, 38)         # treasure X + route
BROWN = (110, 80, 45)       # palm trunk
ROCK = (150, 120, 85)       # mountain
SNOW = (245, 240, 225)
BORDER = (96, 66, 36)

# --- 5x7 bitmap font (rows of 5 bits) ---
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    ' ': ["00000"] * 7,
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
}

PLACES = [
    "WHISPERING COVE",
    "PIRATES PERCH",
    "MOUNT GIGGLE",
    "PARROT TAVERN",
    "MERMAID LAGOON",
    "DEAD MAN'S DUNES",
    "THE GIGGLING CHEST",
]


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def row_fill(self, y, x0, x1, c):
        x0 = max(0, x0)
        x1 = min(self.w - 1, x1)
        if x1 < x0 or not (0 <= y < self.h):
            return
        n = x1 - x0 + 1
        i = self._idx(x0, y)
        self.buf[i:i + n * 3] = bytes(c) * n

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            self.row_fill(yy, x, x + w - 1, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.row_fill(yy, cx - dx, cx + dx, c)

    def ring(self, cx, cy, r0, r1, c):
        for yy in range(cy - r1, cy + r1 + 1):
            dy = yy - cy
            o = math.sqrt(max(0, r1 * r1 - dy * dy))
            i2 = r0 * r0 - dy * dy
            inner = int(math.sqrt(i2)) if i2 > 0 else -1
            self.row_fill(yy, cx - int(o), cx - inner - 1, c)
            self.row_fill(yy, cx + inner + 1, cx + int(o), c)

    def line(self, x0, y0, x1, y1, c, w=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        r = max(0, w // 2)
        while True:
            if w <= 1:
                self.px(x, y, c)
            else:
                self.disc(x, y, r, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def polyline(self, pts, c, w=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], c, w)

    def poly(self, pts, c):
        # scanline fill
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                self.row_fill(y, int(math.ceil(a)), int(math.floor(b)), c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for ry, row in enumerate(g):
                for rx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx - x - scale

    def text_center(self, s, cx, y, scale, c):
        w = len(s) * 6 * scale - scale
        return self.text(s, cx - w // 2, y, scale, c)


def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    return out + struct.pack(">I", crc32(typ + data))


def encode_png(w, h, buf):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def island_outline(cx, cy, n=96):
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = 300 + 38 * math.sin(3 * th + 0.7) + 22 * math.sin(7 * th + 2.1) \
            + 14 * math.sin(11 * th + 0.4)
        pts.append((int(cx + r * math.cos(th)), int(cy + r * 0.92 * math.sin(th))))
    return pts


def draw(cv):
    rnd = random.Random(SEED)
    # parchment gradient
    for y in range(H):
        cv.row_fill(y, 0, W - 1, mix(PARCH_TOP, PARCH_BOT, y / (H - 1)))
    # aged vignette: nested frames darkening toward the edge
    for k in range(8):
        inset = k * 6
        col = mix(PARCH_TOP, (196, 168, 112), (7 - k) / 7 * 0.55)
        cv.rect(inset, inset, W - 2 * inset, 6, col)
        cv.rect(inset, H - inset - 6, W - 2 * inset, 6, col)
        cv.rect(inset, inset, 6, H - 2 * inset, col)
        cv.rect(W - inset - 6, inset, 6, H - 2 * inset, col)
    # speckles (age spots) — drawn before everything else
    for _ in range(4500):
        x, y = rnd.randrange(W), rnd.randrange(H)
        cv.px(x, y, rnd.choice([(200, 175, 120), (240, 225, 180),
                                (180, 150, 95)]))
    for _ in range(350):
        x, y = rnd.randrange(W), rnd.randrange(H)
        cv.disc(x, y, 2, (205, 180, 125))

    # ---- island ----
    pts = island_outline(500, 545)
    cv.poly(pts, SAND)
    cv.polyline(pts + [pts[0]], COAST, 3)
    # green interior patches
    for (gx, gy, gr) in [(420, 480, 70), (600, 600, 80), (350, 650, 55),
                         (560, 420, 45)]:
        cv.disc(gx, gy, gr, GREEN)
    for _ in range(90):  # forest dots
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0, 200)
        cv.disc(int(500 + rr * math.cos(a)), int(545 + rr * 0.9 * math.sin(a)),
                rnd.choice([3, 4, 5]), GREEN_DK)

    # ---- Whispering Cove: water inlet on the north coast ----
    cv.disc(330, 268, 30, SEA)
    cv.ring(330, 268, 28, 32, COAST)
    # ---- Mermaid Lagoon ----
    cv.disc(250, 600, 58, SEA)
    cv.disc(250, 600, 40, (150, 200, 210))
    cv.ring(250, 600, 56, 60, COAST)
    # ---- Mount Giggle ----
    cv.poly([(468, 522), (520, 412), (578, 522)], ROCK)
    cv.poly([(508, 440), (520, 412), (533, 440), (526, 448),
             (520, 442), (514, 448)], SNOW)
    # ---- Pirates Perch: cliff rocks ----
    cv.poly([(225, 385), (258, 338), (292, 385)], (140, 115, 80))
    cv.poly([(250, 385), (272, 352), (295, 385)], (120, 98, 68))
    # ---- Parrot Tavern ----
    cv.rect(755, 455, 30, 24, (150, 100, 60))
    cv.poly([(750, 455), (770, 435), (790, 455)], (120, 70, 40))
    cv.rect(766, 465, 8, 14, (74, 52, 30))
    # ---- Dead Man's Dunes ----
    for (dx, dy, dr) in [(680, 720, 22), (730, 742, 26), (700, 762, 18)]:
        cv.disc(dx, dy, dr, (205, 175, 110))
        cv.ring(dx, dy, dr - 2, dr, (170, 140, 85))
    # ---- palms ----
    for (px, py) in [(650, 560), (590, 300)]:
        cv.line(px, py, px + 4, py - 34, BROWN, 4)
        for ang in (-150, -110, -70, -30, 10):
            a = math.radians(ang)
            ex = int(px + 4 + 26 * math.cos(a))
            ey = int(py - 34 + 14 * math.sin(a) + 8)
            cv.line(px + 4, py - 34, ex, ey, GREEN_DK, 3)

    # ---- dashed route: cove -> treasure ----
    p0, p1, p2, p3 = (330, 285), (240, 450), (400, 620), (478, 692)
    prev = None
    for i in range(201):
        t = i / 200
        mt = 1 - t
        x = int(mt**3 * p0[0] + 3 * mt * mt * t * p1[0]
                + 3 * mt * t * t * p2[0] + t**3 * p3[0])
        y = int(mt**3 * p0[1] + 3 * mt * mt * t * p1[1]
                + 3 * mt * t * t * p2[1] + t**3 * p3[1])
        if prev is not None and (i // 6) % 2 == 0:
            cv.line(prev[0], prev[1], x, y, RED, 3)
        prev = (x, y)

    # ---- treasure X ----
    cv.line(458, 678, 502, 722, RED, 5)
    cv.line(502, 678, 458, 722, RED, 5)
    cv.ring(480, 700, 34, 38, RED)

    # ---- waves in the open sea ----
    for _ in range(30):
        x, y = rnd.randrange(50, 974), rnd.randrange(50, 974)
        if math.hypot(x - 500, (y - 545) / 0.92) < 345:
            continue
        if 820 < x < 945 and 85 < y < 215:
            continue
        if y < 130 and 300 < x < 720:
            continue
        wpts = [(x + k * 6, y + int(4 * math.sin(k * 1.4))) for k in range(5)]
        cv.polyline(wpts, SEA_DK, 2)

    # ---- sea serpent + "HERE BE GIGGLES" ----
    serp = [(110, 895), (140, 880), (170, 895), (200, 880), (230, 895),
            (255, 882)]
    cv.polyline(serp, SEA_DK, 3)
    cv.disc(262, 876, 8, SEA_DK)
    cv.px(265, 873, (20, 20, 20))
    cv.text("HERE BE GIGGLES", 90, 845, 2, INK)

    # ---- birds ----
    for (bx, by) in [(150, 170), (230, 140), (190, 205)]:
        cv.polyline([(bx - 10, by + 4), (bx, by - 4), (bx + 10, by + 4)],
                    INK, 2)

    # ---- labels (all 7 places, scale 2) ----
    cv.text_center("WHISPERING COVE", 330, 212, 2, INK)
    cv.text_center("PIRATES PERCH", 258, 312, 2, INK)
    cv.text_center("MOUNT GIGGLE", 520, 382, 2, INK)
    cv.text_center("PARROT TAVERN", 770, 410, 2, INK)
    cv.text_center("MERMAID LAGOON", 250, 672, 2, INK)
    cv.text_center("DEAD MAN'S DUNES", 705, 700, 2, INK)
    cv.text_center("THE GIGGLING CHEST", 480, 748, 2, INK)

    # ---- compass rose ----
    cv.disc(880, 150, 56, INK)
    cv.disc(880, 150, 50, PARCH_TOP)
    cv.poly([(880, 102), (890, 140), (920, 150), (890, 160),
             (880, 198), (870, 160), (840, 150), (870, 140)], INK)
    cv.disc(880, 150, 7, RED)
    cv.text("N", 874, 76, 2, INK)
    cv.text("E", 944, 143, 2, INK)
    cv.text("S", 874, 210, 2, INK)
    cv.text("W", 812, 143, 2, INK)

    # ---- title + flourish ----
    cv.text_center("ISLE OF GIGGLES", 512, 58, 4, INK)
    cv.line(380, 100, 644, 100, INK, 2)
    cv.disc(512, 100, 5, RED)

    # ---- scale bar ----
    cv.text_center("ONE LEAGUE", 880, 895, 2, INK)
    cv.line(830, 925, 930, 925, INK, 3)
    cv.line(830, 918, 830, 932, INK, 3)
    cv.line(930, 918, 930, 932, INK, 3)

    # ---- double border ----
    cv.rect(14, 14, W - 28, 3, BORDER)
    cv.rect(14, H - 17, W - 28, 3, BORDER)
    cv.rect(14, 14, 3, H - 28, BORDER)
    cv.rect(W - 17, 14, 3, H - 28, BORDER)
    cv.rect(26, 26, W - 52, 2, BORDER)
    cv.rect(26, H - 28, W - 52, 2, BORDER)
    cv.rect(26, 26, 2, H - 52, BORDER)
    cv.rect(W - 28, 26, 2, H - 52, BORDER)
    for (cx, cy) in [(20, 20), (W - 20, 20), (20, H - 20), (W - 20, H - 20)]:
        cv.disc(cx, cy, 6, BORDER)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    cv = Canvas(W, H)
    draw(cv)
    png = encode_png(W, H, cv.buf)
    with open(out_path, "wb") as f:
        f.write(png)
    print(out_path)
    print("size:", len(png), "bytes (limit 1048576)")
    print("dims: 1024x1024")
    print("labels:", len(PLACES), PLACES)
    print("sha256:", hashlib.sha256(png).hexdigest())
    if len(png) > 1048576:
        print("FAIL: over 1 MiB gate", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
