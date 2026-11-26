#!/usr/bin/env python3
"""news-image-20261125 v2.8 - illustrated broadsheet, built from scratch.
One image summing up Wednesday 25 November 2026's world news.
Pure stdlib. Glyphs rendered from Liberation Serif outlines (GLYPH_BLOB,
regenerated from the system TTFs in the v1 session) and its own PNG encoder.
Layout, composition and all 13 code-drawn scenes are new for v2; only the
glyph/PNG/text-metric machinery is shared with v1. v2.8 promotes 4 also-list
stories (macaw #22, Dragonfly #24, Iwo Jima #32, Para hockey #34) to drawn
tiles in the IN BRIEF zone (3-col one-liners + 4-tile strip), taking drawn
scenes from 13 to 17; heroes, small cards, UTC, map, legend and DATE CHECK
keep their v2.7 geometry. Writes exactly one file: entry.png in
MAKEFUN_OUTPUT_DIR (fallback /output). Deterministic: same bytes every run.
"""
import base64
import math
import os
import struct
import zlib

GLYPH_BLOB = [
    "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",
]

UPM = 2048
SS = 3  # supersample factor for glyph masks (3x render, averaged down)


def _decode_blob():
    raw = zlib.decompress(base64.b64decode("".join(GLYPH_BLOB))).decode("utf-8")
    glyphs = {}
    for line in raw.splitlines():
        if not line:
            continue
        fid, cp, adv, _bbox, contours = line.split("\t")
        cont = []
        if contours.strip():
            for c in contours.split("|"):
                pts = []
                for p in c.split(";"):
                    x, y, on = p.split(",")
                    pts.append((int(x), int(y), int(on)))
                cont.append(pts)
        glyphs[(fid, int(cp))] = (int(adv), cont)
    return glyphs


GLYPHS = _decode_blob()


def _quad(out, p0, p1, p2, depth=0):
    """Flatten one quadratic Bezier; append end point."""
    dx, dy = p2[0] - p0[0], p2[1] - p0[1]
    length = math.hypot(dx, dy) or 1.0
    dev = abs((p1[0] - p0[0]) * dy - (p1[1] - p0[1]) * dx) / length
    if dev < 0.6 or depth >= 10:
        out.append(p2)
        return
    m01 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    m12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    m = ((m01[0] + m12[0]) / 2, (m01[1] + m12[1]) / 2)
    _quad(out, p0, m01, m, depth + 1)
    _quad(out, m, m12, p2, depth + 1)


def _flatten(pts, scale):
    """TrueType contour -> polyline in px (y down)."""
    P = [(x * scale, -y * scale, on) for (x, y, on) in pts]
    n = len(P)
    if n == 0:
        return []
    if P[0][2]:
        rot = P
        start = (P[0][0], P[0][1])
        j = 1
    elif P[-1][2]:
        rot = P[-1:] + P[:-1]
        start = (P[-1][0], P[-1][1])
        j = 1
    else:
        rot = P
        start = ((P[-1][0] + P[0][0]) / 2, (P[-1][1] + P[0][1]) / 2)
        j = 0
    out = [start]
    cur = start
    m = len(rot)
    while j < m:
        x, y, on = rot[j]
        if on:
            out.append((x, y))
            cur = (x, y)
            j += 1
        else:
            k = (j + 1) % m
            nx, ny, non = rot[k]
            if non:
                _quad(out, cur, (x, y), (nx, ny))
                cur = (nx, ny)
                j += 2
            else:
                mx, my = (x + nx) / 2, (y + ny) / 2
                _quad(out, cur, (x, y), (mx, my))
                cur = (mx, my)
                j += 1
    return out


def _render_glyph_mask(fid, cp, size):
    """Return (advance_px, w, h, xoff, yoff, alpha) for one glyph.

    All contours of the glyph are filled in ONE even-odd scanline pass,
    so O/o/0/a/e/D/8 render hollow. xoff/yoff are the bitmap origin
    relative to the pen position on the baseline (y down).
    """
    if (fid, cp) not in GLYPHS:
        cp = 63
        if (fid, cp) not in GLYPHS:
            return (0.0, 0, 0, 0, 0, bytearray())
    adv, contours = GLYPHS[(fid, cp)]
    scale = size * SS / UPM
    polys = [_flatten(c, scale) for c in contours]
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    if not xs:
        return (adv * size / UPM, 0, 0, 0, 0, bytearray())
    # Snap bbox to SS multiples so the downsampled origin is integral.
    x0 = int(math.floor(min(xs) / SS)) * SS
    x1 = int(math.ceil(max(xs) / SS)) * SS
    y0 = int(math.floor(min(ys) / SS)) * SS
    y1 = int(math.ceil(max(ys) / SS)) * SS
    w, h = x1 - x0, y1 - y0
    edges = []
    for poly in polys:
        for i in range(len(poly)):
            ax, ay = poly[i]
            bx, by = poly[(i + 1) % len(poly)]
            if ay == by:
                continue
            edges.append((ax, ay, bx, by))
    mask2 = bytearray(w * h)
    for row in range(h):
        yc = y0 + row + 0.5
        xi = []
        for (ax, ay, bx, by) in edges:
            if (ay <= yc < by) or (by <= yc < ay):
                t = (yc - ay) / (by - ay)
                xi.append(ax + t * (bx - ax))
        xi.sort()
        for k in range(0, len(xi) - 1, 2):
            px0 = max(0, int(math.ceil(xi[k] - x0 - 0.5)))
            px1 = min(w, int(math.ceil(xi[k + 1] - x0 - 0.5)))
            for px in range(px0, px1):
                mask2[row * w + px] = 1
    ow, oh = w // SS, h // SS
    alpha = bytearray(ow * oh)
    for j in range(oh):
        for i in range(ow):
            s = 0
            for dy in range(SS):
                base = (j * SS + dy) * w + i * SS
                for dx in range(SS):
                    s += mask2[base + dx]
            alpha[j * ow + i] = min(255, s * 255 // (SS * SS))
    return (adv * size / UPM, ow, oh, x0 // SS, y0 // SS, alpha)


_GLYPH_CACHE = {}


def _glyph(fid, cp, size):
    key = (fid, cp, size)
    m = _GLYPH_CACHE.get(key)
    if m is None:
        m = _render_glyph_mask(fid, cp, size)
        _GLYPH_CACHE[key] = m
    return m


def text_width(s, size, bold=False):
    fid = "B" if bold else "R"
    w = 0.0
    for ch in s:
        w += _glyph(fid, ord(ch), size)[0]
    return w


def wrap_text(s, size, bold, max_w):
    lines = []
    cur = ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, size, bold) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(self.w, int(x + w))
        y1 = min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def blit_alpha(self, bx, by, gw, gh, alpha, color):
        r, g, b = color
        for j in range(gh):
            yy = by + j
            if yy < 0 or yy >= self.h:
                continue
            for i in range(gw):
                a = alpha[j * gw + i]
                if a == 0:
                    continue
                xx = bx + i
                if xx < 0 or xx >= self.w:
                    continue
                k = (yy * self.w + xx) * 3
                if a == 255:
                    self.buf[k] = r
                    self.buf[k + 1] = g
                    self.buf[k + 2] = b
                else:
                    self.buf[k] = (r * a + self.buf[k] * (255 - a)) // 255
                    self.buf[k + 1] = (g * a + self.buf[k + 1] * (255 - a)) // 255
                    self.buf[k + 2] = (b * a + self.buf[k + 2] * (255 - a)) // 255

    def text(self, x, y, s, size, bold, color, align="left"):
        """Draw text; x, y is the baseline point (left/center/right)."""
        fid = "B" if bold else "R"
        w = text_width(s, size, bold)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        pen = x
        for ch in s:
            adv, gw, gh, xoff, yoff, alpha = _glyph(fid, ord(ch), size)
            if gw and gh:
                bx = int(round(pen + xoff))
                by = int(round(y + yoff))
                self.blit_alpha(bx, by, gw, gh, alpha, color)
            pen += adv
        return w

    def line(self, x0, y0, x1, y1, color, width=1):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length == 0:
            return
        nx, ny = -dy / length * width / 2, dx / length * width / 2
        self.fill_poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                        (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], color)

    def fill_poly(self, pts, color):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(self.h, int(math.ceil(max(ys))))
        edges = []
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            if ay == by:
                continue
            edges.append((ax, ay, bx, by))
        r, g, b = color
        for yy in range(y0, y1):
            yc = yy + 0.5
            xs = []
            for (ax, ay, bx, by) in edges:
                if (ay <= yc < by) or (by <= yc < ay):
                    t = (yc - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = max(0, int(math.ceil(xs[k] - 0.5)))
                xb = min(self.w, int(math.ceil(xs[k + 1] - 0.5)))
                for xx in range(xa, xb):
                    i = (yy * self.w + xx) * 3
                    self.buf[i] = r
                    self.buf[i + 1] = g
                    self.buf[i + 2] = b

    def circle(self, cx, cy, r, color):
        for yy in range(int(cy - r), int(cy + r) + 1):
            dy = yy - cy
            dx = math.sqrt(max(0, r * r - dy * dy))
            self.fill_rect(cx - dx, yy, 2 * dx, 1, color)

    def ring(self, cx, cy, r_out, r_in, color):
        for yy in range(int(cy - r_out), int(cy + r_out) + 1):
            dy = yy - cy
            dxo = math.sqrt(max(0, r_out * r_out - dy * dy))
            dxi = math.sqrt(max(0, r_in * r_in - dy * dy)) if abs(dy) < r_in else 0
            if dxi > 0:
                self.fill_rect(cx - dxo, yy, dxo - dxi, 1, color)
                self.fill_rect(cx + dxi, yy, dxo - dxi, 1, color)
            else:
                self.fill_rect(cx - dxo, yy, 2 * dxo, 1, color)


def _png_chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    w, h = cv.w, cv.h
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += cv.buf[y * w * 3:(y + 1) * w * 3]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (26, 26, 26)
INK_SOFT = (78, 76, 68)
DECK_GREY = (58, 56, 50)
TEAL = (15, 76, 76)
NAVY = (20, 33, 61)
NAVY_DK = (13, 22, 44)
NAVY_LT = (52, 70, 104)
RED = (178, 34, 34)
RED_BR = (204, 48, 32)
AMBER = (168, 116, 0)
BLUE = (36, 80, 140)
GREY = (96, 94, 86)
RULE = (198, 190, 170)
LAND = (222, 214, 186)
LAND_LINE = (120, 130, 110)
SEA_MAP = (198, 214, 218)
WHITE = (255, 255, 255)
CREAM = (240, 234, 214)
SKY_NIGHT = (10, 16, 40)
SKY_NIGHT2 = (24, 34, 66)
DUSK1 = (214, 110, 50)
DUSK2 = (232, 150, 80)
DUSK3 = (245, 200, 130)
SEA = (28, 68, 110)
SEA_DK = (18, 48, 84)
FIRE = (240, 110, 20)
FLAME = (255, 180, 40)
SMOKE = (96, 96, 100)
SAND = (222, 196, 150)
GREEN = (96, 138, 80)
EARTH = (122, 90, 60)
EARTH_DK = (88, 62, 40)
WOOD = (146, 104, 58)

PILL_COLOR = {"CONFIRMED": TEAL, "CLAIM": RED, "REPORTED": AMBER,
              "ONGOING": BLUE, "SCHEDULED": GREY, "OFFICIAL": TEAL}

# ---------------------------------------------------------------- content
# (title-case headline, deck, pill, kicker)
LEADS = [
    ("Asia's chip stocks crash on AI doubts",
     "TAIEX \u22126%+, SoftBank \u221216.1%, TSMC \u22128.1% as AI doubts spread. "
     "Dow still topped 50,000.",
     "CONFIRMED", "SELL-OFF \u00b7 SEOUL \u00b7 TAIPEI \u00b7 TOKYO \u00b7 MARKETS"),
    ("Shenzhou-24 flies a Pakistani to Tiangong",
     "Long March 2F lifts off 00:18 UTC, docks ~3.5h later. "
     "Zeeshan Ali, 40, first foreigner on Tiangong.",
     "CONFIRMED", "LIFTOFF \u00b7 JIUQUAN, CHINA \u00b7 SPACE"),
    ("Two oil tankers hit mines and burn, Iran says",
     "IRGC claims 2 more tankers hit mines early Wed; Tehran says it "
     "downed 2 drones. No US confirmation.",
     "CLAIM", "WAR AT SEA \u00b7 STRAIT OF HORMUZ \u00b7 IRAN WAR"),
]

# (headline, deck, pill, kicker, scene)
SMALL = [
    ("Australia CPI jumps to +4.9%",
     "Oct CPI up from 4.3%; fuel +6.3%. RBA 4.85%; ASX +1.35%.",
     "CONFIRMED", "CANBERRA, AUSTRALIA", "cpi"),
    ("Bangladesh garment pay +36%",
     "17,000 taka ($139) at 2am Wed; 4m workers, 80% exports.",
     "CONFIRMED", "DHAKA, BANGLADESH", "garment"),
    ("Solomons signs Australia pact",
     "Australia primary partner; no foreign base. A$740m aid.",
     "CONFIRMED", "CANBERRA, AUSTRALIA", "treaty"),
    ("Cartagena standoff drags on",
     "10 of ~30 freed; ~20 still held Wed; president at scene.",
     "ONGOING", "CARTAGENA, COLOMBIA", "store"),
    ("Trump readies tariffs on 16",
     "USTR findings due Tue\u2013Wed; rates unclear.",
     "REPORTED", "WASHINGTON, US", "tariffs"),
    ("N. Korea expels Swiss envoy",
     "48 hours to leave; Pyongyang office shut after 37 days.",
     "CONFIRMED", "PYONGYANG, N. KOREA", "pyongyang"),
    ("Sydney double-murder guilty",
     "Ex-cop convicted over 2024 killings; sentencing Mar 2027.",
     "CONFIRMED", "SYDNEY, AUSTRALIA", "court"),
    ("26 trapped in Bogor gold mine",
     "Shaft flooded Mon; 11 of ~30 escaped; rescue blocked.",
     "CONFIRMED", "BOGOR, INDONESIA", "mine"),
    ("Iowa to blast 9,500 lb azide",
     "68 barrels at 9am CT; plume 100+ miles; 5-mile cone.",
     "SCHEDULED", "IOWA, US", "blast"),
    ("Korea births jump +12.2%",
     "Sept births 25,113; fertility 0.90; 27th straight rise.",
     "CONFIRMED", "SEOUL, S. KOREA", "births"),
]

ALSO = [
    "TSMC \u22128.1% in Taiwan chip rout",
    "Samsung \u22129.1%; SK Hynix \u22128.6%",
    "Kioxia \u221215.4% in Tokyo sell-off",
    "Iran says it downed 2 drones",
    "Hang Seng +1% as Asia sinks",
    "Brent \u221221% in Nov, at $87.49",
    "Sensex +1.8% as Asia sinks",
    "HK marks Tai Po fire, 168 dead",
    "Spix's macaw chick Hope hatches",
    "Brazil dengue \u221268% via mosquitoes",
    "Dragonfly Titan parts arrive",
    "Astronaut's wife gives birth",
    "Deepest eruptions in Mariana Trench",
    "New amphibian named Maria",
    "Blight-proof chestnut returns",
    "Microplastics in 95/120 Oman fish",
    "Oh Seung-ho in Naoki shortlist",
    "First Children's Booker shortlist",
    "Iwo Jima eruption adds new land",
    "18% of midlife women quit smoking",
    "Canada women win Para hockey 10-0",
    "MIT: tiny black holes may eat stars",
]

# (big number, caption, sub-caption)
STATS = [
    ("\u22123.6%", "NIKKEI", "Asia's chip stocks plunge"),
    ("\u221216.1%", "SOFTBANK", "Biggest single-day fall"),
    ("+4.9%", "AU CPI", "Oct inflation; RBA 4.85%"),
    ("+36%", "GARMENT PAY", "17,000 taka minimum"),
    ("+12.2%", "KOREA BIRTHS", "Sept; 27th monthly rise"),
    ("26", "TRAPPED MINERS", "Bogor gold-mine flood"),
]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off"),
    ("00:30", "Australia CPI: +4.9%"),
    ("03:10", "Korea births out"),
    ("05:17", "10 freed, Cartagena"),
    ("05:23", "Iran: 2 more tankers hit"),
    ("15:00", "Iowa azide blast 9am CT"),
]

# (name, lat, lon, story number, label?)
PINS = [
    ("Tokyo", 35.7, 139.7, 1, True),
    ("Seoul", 37.6, 127.0, 1, True),
    ("Taipei", 25.0, 121.6, 1, False),
    ("Jiuquan", 40.0, 100.0, 2, False),
    ("Hormuz", 26.5, 56.5, 3, True),
    ("Canberra", -35.3, 149.1, 4, True),
    ("Dhaka", 23.8, 90.4, 5, False),
    ("Cartagena", 10.4, -75.5, 7, True),
    ("Washington", 38.9, -77.0, 8, True),
    ("Pyongyang", 39.0, 125.8, 9, False),
    ("Sydney", -33.9, 151.2, 10, False),
    ("Bogor", -6.6, 106.8, 11, False),
    ("Iowa", 40.8, -91.3, 12, True),
]

DATECHECK = [
    "Houthi hits Riyadh PIF Tower, 11 hurt \u2014 Tue 24 Nov",
    "Nvidia \u22127%; Huang in therapy \u2014 Tue 24 Nov",
    "Huawei guilty on 10 of 12 counts \u2014 Tue 24 Nov",
    "Hamas security chief killed in Gaza \u2014 Tue 24 Nov",
    "CIA/ODNI unclassified breach \u2014 Tue 24 Nov",
    "Democrats reach 259 House seats \u2014 Tue 24 Nov",
    "Cuba life expectancy 78.8 to 74.4 \u2014 Tue 24 Nov",
    "Ronaldo's 987th goal \u2014 Tue 24 Nov",
    "Sooryavanshi 204 off 53 balls \u2014 Tue 24 Nov",
    "RAK bus crash kills 13 \u2014 Tue 24 Nov",
    "Turkish heli crash kills 5 \u2014 Tue 24 Nov",
    "BepiColombo enters Mercury orbit \u2014 Sat 21 Nov",
]

# (label, count, color) — widths proportional to count, mins applied in code
REGIONS = [
    ("ASIA-PACIFIC", 14, (178, 34, 34)),
    ("MIDDLE EAST", 4, (168, 116, 0)),
    ("AMERICAS", 10, (36, 80, 140)),
    ("OCEANIA", 4, (15, 76, 76)),
    ("EUROPE", 2, (96, 94, 86)),
    ("WORLD", 1, (26, 26, 26)),
]

# Simplified continent outlines (lon, lat), equirectangular schematic.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-145, 60), (-165, 60)],
    [(-80, 10), (-70, 12), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -55),
     (-73, -40), (-75, -20), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -30), (12, -18), (13, -5), (9, 4), (-8, 5)],
    [(-10, 36), (-9, 43), (0, 44), (10, 44), (20, 40), (26, 38),
     (30, 36), (36, 36), (40, 38), (45, 40), (50, 45), (55, 50),
     (60, 55), (65, 60), (70, 70), (80, 73), (90, 75), (100, 77),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 66),
     (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 60),
     (142, 55), (140, 45), (135, 43), (130, 38), (127, 35), (122, 32),
     (120, 28), (115, 23), (110, 20), (108, 15), (105, 10), (100, 8),
     (98, 12), (95, 16), (92, 21), (90, 22), (85, 20), (80, 15),
     (77, 8), (75, 12), (72, 20), (68, 23), (65, 25), (60, 25),
     (57, 26), (54, 27), (50, 29), (48, 30), (44, 29), (40, 31),
     (36, 36), (33, 36), (30, 36), (26, 38), (22, 37), (18, 40),
     (15, 38), (12, 42), (8, 44), (3, 43), (-2, 37), (-6, 36), (-9, 38)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20), (114, -22)],
]

# ---------------------------------------------------------------- helpers
W, H = 1024, 1024
M = 14
CW = W - 2 * M


def rect_outline(cv, x, y, w, h, color, width=1):
    cv.fill_rect(x, y, w, width, color)
    cv.fill_rect(x, y + h - width, w, width, color)
    cv.fill_rect(x, y, width, h, color)
    cv.fill_rect(x + w - width, y, width, h, color)


def vgrad(cv, x, y, w, h, top, bot):
    """Vertical gradient in h bands (deterministic, no dithering)."""
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        cv.fill_rect(x, y + i, w, 1, c)


def pill(cv, x, y, label, size=9):
    """Filled pill, left-anchored at x, top y; returns width."""
    w = int(text_width(label, size, True)) + 12
    h = size + 5
    cv.fill_rect(x, y, w, h, PILL_COLOR[label])
    cv.text(x + 6, y + size + 1, label, size, True, WHITE)
    return w


def pill_right(cv, x_right, y, label, size=9):
    w = int(text_width(label, size, True)) + 12
    pill(cv, x_right - w, y, label, size)
    return w


def num_badge(cv, cx, cy, n, r=9):
    """Red numbered circle with white bold number."""
    cv.circle(cx, cy, r, RED)
    s = str(n)
    cv.text(cx, cy + 3, s, 9 if len(s) == 1 else 8, True, WHITE,
            align="center")


def glow(cv, cx, cy, r, cols):
    """Stepped halo: cols from outer (faint) to inner (bright)."""
    n = len(cols)
    for i, c in enumerate(cols):
        rr = int(r * (n - i) / n)
        if rr > 0:
            cv.circle(cx, cy, rr, c)


def starfield(cv, x, y, w, h, seed):
    """Deterministic pseudo-random stars."""
    s = seed
    for _ in range(26):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        sx = x + s % w
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        sy = y + s % h
        r = 1 if s % 3 else 2
        cv.circle(sx, sy, r, WHITE if s % 5 else (255, 220, 160))


# ---------------------------------------------------------------- hero scenes
def scene_chart(cv, x, y, w, h):
    """H1: dark AI sell-off chart with chip and falling red line.
    Layers: dark bg + faint area fill under the line + grid + candles +
    falling line with glow endpoint + volume bars + chip with shadow."""
    cv.fill_rect(x, y, w, h, NAVY_DK)
    # grid (brighter, so the chart reads at thumbnail)
    for gy in range(1, 5):
        cv.fill_rect(x, y + h * gy // 5, w, 1, (64, 84, 134))
    for gx in range(1, 7):
        cv.fill_rect(x + w * gx // 7, y, 1, h, (64, 84, 134))
    # chart area is the left part; right column is a clean label panel
    cw = w - 132
    # falling red line (defined first so the area fill sits under it)
    pts = [(x + 10, y + 22), (x + cw * 0.25, y + 34), (x + cw * 0.42, y + 30),
           (x + cw * 0.6, y + 58), (x + cw * 0.78, y + 74), (x + cw - 12, y + 96)]
    # faint area fill under the falling line (loss zone, deeper red)
    cv.fill_poly([(x + 10, y + h - 8)] + pts +
                 [(x + cw - 12, y + h - 8)], (72, 24, 32))
    # candlesticks (falling) — 12 bars now, hotter colors + top lights
    tops = [18, 30, 26, 44, 40, 58, 52, 70, 66, 84, 78, 92]
    bw = cw // 18
    for i, t in enumerate(tops):
        bx = x + 12 + i * (cw - 24) // 12
        bh = 10 + (i % 3) * 4
        col = (230, 70, 45) if i % 2 else (50, 190, 110)
        hi = (255, 150, 100) if i % 2 else (140, 240, 180)
        cv.fill_rect(bx, y + t, bw, bh, col)
        cv.fill_rect(bx, y + t, bw, 2, hi)
        cv.fill_rect(bx + bw // 2, y + t - 6, 1, bh + 12, col)
    # glowing drop-trail: wide dark-red underlay, mid red, bright core
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], (110, 35, 22), 9)
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED_BR, 6)
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], (255, 120, 50), 3)
    for (px, py) in pts:
        cv.circle(px, py, 3, FLAME)
    # glow at the last point (the fall's end)
    glow(cv, pts[-1][0], pts[-1][1], 12,
         [(70, 30, 22), (150, 50, 30), (255, 170, 60)])
    # dashed resistance line near the top + bright ring on the end dot
    for gx in range(x + 12, x + cw - 20, 14):
        cv.fill_rect(gx, y + 13, 7, 1, (110, 130, 180))
    cv.ring(pts[-1][0], pts[-1][1], 8, 6, (255, 170, 60))
    # volume bars along the bottom of the chart area (red on down days)
    vols = [4, 7, 5, 9, 6, 11, 8, 12, 9, 13, 10, 12]
    for i, vh in enumerate(vols):
        bx = x + 12 + i * (cw - 24) // 12
        cv.fill_rect(bx, y + h - 6 - vh, bw, vh,
                     (180, 60, 40) if i >= 9 else (90, 120, 175))
    # chip, bottom-left (glow + brighter face + drop shadow)
    cx, cy = x + 34, y + h - 30
    glow(cv, cx, cy, 20, [(18, 26, 54), (36, 56, 104)])
    cv.fill_rect(cx - 15, cy - 11, 32, 24, (8, 12, 26))
    cv.fill_rect(cx - 16, cy - 12, 32, 24, (40, 56, 96))
    rect_outline(cv, cx - 16, cy - 12, 32, 24, (150, 180, 240), 1)
    cv.fill_rect(cx - 7, cy - 5, 14, 10, (70, 110, 190))
    for dx in (-20, -12, 12, 20):
        cv.fill_rect(cx + dx - 1, cy - 12, 2, 24, (120, 150, 220))
    cv.text(cx, cy + 4, "AI", 10, True, WHITE, align="center")
    # label panel (lighter, so text never sits on candles/line)
    cv.fill_rect(x + w - 128, y + 8, 120, 84, (30, 44, 80))
    cv.fill_rect(x + w - 128, y + 8, 1, 84, (90, 110, 165))
    # right-side index list: white names, hot-red values, down triangles
    rows = [("KOSPI", "\u22125.6%"), ("TAIEX", "\u22126%"),
            ("NIKKEI", "\u22123.6%"), ("SOFTBANK", "\u221216.1%")]
    for i, (nm, val) in enumerate(rows):
        ry = y + 16 + i * 20
        cv.text(x + w - 118, ry, nm, 10, True, WHITE)
        nw = text_width(nm, 10, True)
        vw = text_width(val, 10, True)
        vx = x + w - 14 - vw
        if vx - (x + w - 118 + nw) >= 12:
            tx = x + w - 118 + nw + 2
            cv.fill_poly([(tx, ry - 7), (tx + 8, ry - 7), (tx + 4, ry)],
                         (255, 90, 60))
        cv.text(x + w - 14, ry, val, 10, True, (255, 100, 70),
                align="right")


def scene_rocket(cv, x, y, w, h):
    """H2: night rocket launch from Jiuquan, Tiangong above.
    Layers: night gradient + double starfield + moon halo + horizon
    glow + distant hills + floodlight cones + control building + tower
    + smoke + flame glow + shaded rocket."""
    vgrad(cv, x, y, w, h, SKY_NIGHT, SKY_NIGHT2)
    starfield(cv, x, y, w, h - 40, 12345)
    starfield(cv, x, y, w, (h - 40) // 2, 999)
    # bright 4-point sparkles (clear of moon, station, tower, rocket)
    for (sx, sy) in ((x + 100, y + 14), (x + 238, y + 14), (x + 250, y + 44),
                     (x + 60, y + 48), (x + 135, y + 30), (x + 300, y + 60)):
        cv.line(sx - 4, sy, sx + 4, sy, WHITE, 1)
        cv.line(sx, sy - 4, sx, sy + 4, WHITE, 1)
        cv.circle(sx, sy, 1, (255, 240, 180))
    # shooting star, top-left (clear of sparkles, station, data panel)
    cv.line(x + 78, y + 8, x + 94, y + 15, (220, 225, 240), 1)
    cv.circle(x + 94, y + 15, 2, (255, 245, 200))
    # mission data panel, top-center (crew + stay; clear of station,
    # moon glow, and the rocket nose below it)
    cv.fill_rect(x + 116, y + 6, 98, 14, (12, 16, 34))
    rect_outline(cv, x + 116, y + 6, 98, 14, (150, 180, 240), 1)
    cv.text(x + 165, y + 17, "CREW 3 \u00b7 5\u201310 DAYS", 8, True, WHITE,
            align="center")
    # moon + halo
    glow(cv, x + w - 44, y + 26, 26,
         [(30, 34, 60), (70, 74, 100), (180, 180, 190)])
    cv.circle(x + w - 44, y + 26, 15, (240, 238, 220))
    cv.circle(x + w - 49, y + 22, 4, (210, 208, 190))
    cv.circle(x + w - 38, y + 30, 3, (210, 208, 190))
    # warm horizon glow behind the pad
    vgrad(cv, x, y + h - 44, w, 28, (52, 44, 38), (30, 34, 26))
    # distant hills silhouette
    cv.fill_poly([(x, y + h - 16), (x + 52, y + h - 34),
                  (x + 104, y + h - 22), (x + 160, y + h - 38),
                  (x + 220, y + h - 24), (x + w, y + h - 32),
                  (x + w, y + h - 16)], (22, 26, 22))
    # Tiangong station, top-left (solar arrays with cell grid)
    sx, sy = x + 30, y + 16
    cv.fill_rect(sx, sy, 26, 8, (200, 205, 215))
    cv.fill_rect(sx - 18, sy + 2, 16, 4, (90, 130, 200))
    cv.fill_rect(sx + 28, sy + 2, 16, 4, (90, 130, 200))
    for px in (sx - 18, sx + 28):
        for gx in (px + 4, px + 8, px + 12):
            cv.fill_rect(gx, sy + 2, 1, 4, (40, 70, 140))
        cv.fill_rect(px, sy + 2, 16, 1, (160, 200, 255))
    cv.text(sx + 13, sy + 22, "TIANGONG", 8, True, (200, 205, 215),
            align="center")
    # ground: Earth limb — blue gradient band + glowing curved rim
    vgrad(cv, x, y + h - 16, w, 16, (40, 90, 180), (12, 24, 56))
    glow(cv, x + w // 2, y + h - 18, 22, [(18, 36, 80), (50, 100, 190)])
    rim = [(x, y + h - 16), (x + w * 0.25, y + h - 19),
           (x + w * 0.5, y + h - 20), (x + w * 0.75, y + h - 19),
           (x + w, y + h - 16)]
    for a, b in zip(rim, rim[1:]):
        cv.line(a[0], a[1], b[0], b[1], (30, 70, 150), 5)
    for a, b in zip(rim, rim[1:]):
        cv.line(a[0], a[1], b[0], b[1], (150, 200, 255), 2)
    # floodlight poles + cones (clear of moon, station, tower)
    for fx in (x + 26, x + w - 26):
        cv.fill_rect(fx, y + h - 52, 3, 36, (90, 95, 105))
        cv.fill_poly([(fx - 4, y + h - 52), (fx + 7, y + h - 52),
                      (fx + 16, y + h - 16), (fx - 13, y + h - 16)],
                     (120, 122, 130))
    # control building, bottom-right (on the ground band)
    cv.fill_rect(x + w - 78, y + h - 40, 44, 24, (24, 28, 34))
    cv.fill_rect(x + w - 72, y + h - 34, 6, 6, (255, 220, 130))
    cv.fill_rect(x + w - 58, y + h - 34, 6, 6, (255, 220, 130))
    cv.fill_rect(x + w - 44, y + h - 34, 6, 6, (140, 170, 220))
    # launch tower, left of rocket (top tracks the shorter scene)
    tx = x + w // 2 - 46
    cv.fill_rect(tx, y + h - 80, 6, 64, (90, 95, 105))
    for ty in range(y + h - 74, y + h - 22, 12):
        cv.line(tx, ty, tx + 22, ty + 8, (90, 95, 105), 2)
    # red beacon on the tower top + smoke drifting left at the base
    cv.circle(tx + 3, y + h - 82, 2, (255, 90, 70))
    cv.circle(x + w // 2 - 46, y + h - 22, 7, (150, 150, 155))
    cv.circle(x + w // 2 - 58, y + h - 18, 5, (150, 150, 155))
    # smoke clouds at base
    for (ox, oy, r) in ((-28, -8, 12), (-14, -4, 15), (0, -10, 13),
                        (14, -4, 15), (28, -8, 12)):
        cv.circle(x + w // 2 + ox, y + h - 18 + oy, r, (150, 150, 155))
    # layered exhaust plume: outer, mid, inner core + ground flash
    fx, fy = x + w // 2, y + h - 52
    glow(cv, fx, fy + 18, 26,
         [(90, 40, 16), (190, 90, 30), (255, 170, 60)])
    glow(cv, fx, y + h - 16, 22,
         [(90, 50, 20), (200, 110, 40), (255, 200, 90)])
    cv.fill_poly([(fx - 14, fy + 4), (fx + 14, fy + 4), (fx, fy + 48)],
                 (190, 80, 25))
    cv.fill_poly([(fx - 9, fy), (fx + 9, fy), (fx, fy + 36)], FLAME)
    cv.fill_poly([(fx - 5, fy), (fx + 5, fy), (fx, fy + 26)], FIRE)
    cv.fill_poly([(fx - 3, fy), (fx + 3, fy), (fx, fy + 16)],
                 (255, 240, 190))
    # plume-edge smoke puffs
    cv.circle(fx - 20, fy + 30, 6, SMOKE)
    cv.circle(fx + 20, fy + 30, 6, SMOKE)
    # rocket body (shaded: light stripe left, shadow right); ry tracks
    # the scene height so the body sits on the pad at h=115 as at h=132
    rx, ry = x + w // 2, y + h - 88
    cv.fill_poly([(rx - 10, ry + 62), (rx + 10, ry + 62),
                  (rx + 10, ry + 12), (rx, ry - 2), (rx - 10, ry + 12)],
                 WHITE)
    cv.fill_poly([(rx - 10, ry + 12), (rx + 10, ry + 12),
                  (rx, ry - 2)], RED_BR)
    cv.fill_rect(rx - 10, ry + 30, 20, 8, (36, 80, 180))
    cv.fill_rect(rx - 10, ry + 12, 5, 50, WHITE)
    cv.fill_rect(rx + 5, ry + 12, 5, 50, (175, 175, 180))
    # stage band + separation line
    cv.fill_rect(rx - 10, ry + 42, 20, 3, (200, 60, 50))
    cv.fill_rect(rx - 10, ry + 38, 20, 1, (60, 60, 70))
    cv.fill_poly([(rx - 10, ry + 44), (rx - 20, ry + 62),
                  (rx - 10, ry + 62)], RED_BR)
    cv.fill_poly([(rx + 10, ry + 44), (rx + 20, ry + 62),
                  (rx + 10, ry + 62)], RED_BR)
    cv.text(rx, ry + 26, "CZ-2F", 7, True, INK, align="center")
    # labels on the ground band (liftoff left, docking right)
    cv.text(x + 10, y + h - 5, "LIFTOFF 00:18 UTC", 9, True, WHITE)
    cv.text(x + w - 10, y + h - 5, "DOCK ~03:50 UTC", 9, True, WHITE,
            align="right")


def scene_tanker(cv, x, y, w, h):
    """H3: burning tanker at dusk in the Strait of Hormuz.
    Layers: dusk gradient + sun glow + birds + coast ridges + sea
    with sun-glint column + distant tanker + main tanker + fire glow
    + smoke + mine dots."""
    vgrad(cv, x, y, w, int(h * 0.62), DUSK1, DUSK3)
    # strike data panel, top-left (clear of the number badge, sun,
    # smoke, and coast ridges)
    cv.fill_rect(x + 24, y + 6, 88, 35, (20, 26, 44))
    rect_outline(cv, x + 24, y + 6, 88, 35, (255, 200, 120), 1)
    for k, ln in enumerate(("2 TANKERS HIT", "MINES IN STRAIT",
                            "2 DRONES DOWNED")):
        cv.text(x + 30, y + 16 + k * 10, ln, 8, True, WHITE)
    # sun + glow
    glow(cv, x + w - 52, y + 34, 30,
         [(200, 110, 40), (240, 160, 70), (255, 216, 130)])
    cv.circle(x + w - 52, y + 34, 16, (255, 226, 140))
    # birds (right of the data panel, clear of the sun glow + smoke)
    for (bx, by) in ((x + 132, y + 14), (x + 178, y + 12), (x + 200, y + 22),
                     (x + 222, y + 14)):
        cv.line(bx - 5, by, bx, by - 3, (60, 44, 36), 1)
        cv.line(bx, by - 3, bx + 5, by, (60, 44, 36), 1)
    # sun rays (short, inside the glow zone)
    sx, sy = x + w - 52, y + 34
    for (ax, ay, bx, by) in ((sx - 24, sy - 14, sx - 18, sy - 10),
                             (sx + 24, sy - 14, sx + 18, sy - 10),
                             (sx, sy - 26, sx, sy - 20)):
        cv.line(ax, ay, bx, by, (255, 200, 120), 1)
    # coast strips (two ridges: far pale, near dark)
    cv.fill_poly([(x, y + int(h * 0.62)), (x + 62, y + int(h * 0.46)),
                  (x + 118, y + int(h * 0.62))], (140, 104, 78))
    cv.fill_poly([(x, y + int(h * 0.62)), (x + 62, y + int(h * 0.44)),
                  (x + 118, y + int(h * 0.62))], (120, 88, 66))
    cv.fill_poly([(x, y + int(h * 0.62)), (x + 62, y + int(h * 0.42)),
                  (x + 118, y + int(h * 0.62))], (96, 70, 52))
    cv.fill_poly([(x + w, y + int(h * 0.62)), (x + w - 56, y + int(h * 0.48)),
                  (x + w - 112, y + int(h * 0.62))], (140, 104, 78))
    cv.fill_poly([(x + w, y + int(h * 0.62)), (x + w - 56, y + int(h * 0.46)),
                  (x + w - 112, y + int(h * 0.62))], (120, 88, 66))
    cv.fill_poly([(x + w, y + int(h * 0.62)), (x + w - 56, y + int(h * 0.44)),
                  (x + w - 112, y + int(h * 0.62))], (96, 70, 52))
    # tiny coastal structures: houses on the left ridge, lighthouse left
    for hx in (x + 18, x + 34):
        cv.fill_rect(hx, y + int(h * 0.56), 8, 6, (60, 44, 34))
        cv.fill_rect(hx + 2, y + int(h * 0.56) + 2, 2, 2, (255, 220, 130))
    cv.fill_rect(x + 96, y + int(h * 0.5), 4, 14, WHITE)
    cv.fill_rect(x + 96, y + int(h * 0.5), 4, 3, RED_BR)
    cv.circle(x + 98, y + int(h * 0.5) - 2, 2, (255, 240, 180))
    cv.text(x + 12, y + int(h * 0.52), "IRAN", 9, True, WHITE)
    cv.text(x + w - 12, y + int(h * 0.52), "OMAN", 9, True, WHITE,
            align="right")
    # sea: dark top band, mid sea, lighter swell band at the bottom
    sy = y + int(h * 0.62)
    cv.fill_rect(x, sy, w, 10, SEA_DK)
    cv.fill_rect(x, sy + 10, w, h - int(h * 0.62) - 22, SEA)
    cv.fill_rect(x, y + h - 12, w, 12, (40, 90, 140))
    # sun-glint column on the water under the sun
    gx = x + w - 52
    cv.fill_rect(gx - 14, sy, 28, h - int(h * 0.62), (120, 90, 50))
    cv.fill_rect(gx - 7, sy, 14, h - int(h * 0.62), (190, 140, 70))
    cv.fill_rect(gx - 3, sy, 6, h - int(h * 0.62), (240, 190, 110))
    # layered wave crests (short bright dashes, staggered rows; 3 rows
    # so the lowest stays inside the shorter scene)
    for wy, xs in ((sy + 12, (16, 60, 104, 148, 192, 236, 280)),
                   (sy + 20, (34, 82, 130, 178, 226, 268)),
                   (sy + 28, (16, 58, 100, 142, 184, 228, 272))):
        for ox in xs:
            cv.fill_rect(x + ox, wy, 14, 2, (130, 170, 210))
    # distant tanker (small, left) + its smoke wisp + hull highlight
    dx, dy = x + 26, sy + 6
    cv.circle(dx + 26, dy - 16, 6, SMOKE)
    cv.circle(dx + 32, dy - 24, 5, SMOKE)
    cv.fill_rect(dx, dy, 52, 10, (20, 26, 40))
    cv.fill_rect(dx, dy, 52, 2, (120, 130, 145))
    cv.fill_rect(dx + 34, dy - 8, 12, 8, (220, 220, 225))
    cv.fill_rect(dx + 8, dy - 4, 6, 4, (220, 220, 225))
    # main tanker
    tx, ty = x + w // 2 - 78, sy + 8
    cv.fill_poly([(tx, ty), (tx + 156, ty), (tx + 146, ty + 22),
                  (tx + 10, ty + 22)], (30, 34, 44))
    # deck-edge highlight + portholes + bright waterline stripe
    cv.fill_rect(tx + 2, ty, 152, 2, (180, 190, 200))
    for px in (tx + 20, tx + 40, tx + 60, tx + 80, tx + 100):
        cv.circle(px, ty + 12, 2, (200, 205, 215))
    cv.fill_rect(tx + 118, ty - 16, 22, 16, (235, 235, 240))
    cv.fill_rect(tx + 122, ty - 12, 5, 4, NAVY_DK)
    cv.fill_rect(tx + 131, ty - 12, 5, 4, NAVY_DK)
    cv.fill_rect(tx + 122, ty - 5, 5, 4, NAVY_DK)
    cv.fill_rect(tx + 131, ty - 5, 5, 4, NAVY_DK)
    cv.fill_rect(tx + 140, ty - 14, 14, 4, (235, 235, 240))
    cv.fill_rect(tx + 10, ty - 6, 60, 6, (200, 70, 45))
    # pale wake trailing behind the hull (on the water below)
    cv.fill_rect(tx + 10, ty + 26, 140, 2, (150, 180, 210))
    # fire glow + fire + smoke on deck
    glow(cv, tx + 52, ty - 16, 24,
         [(120, 50, 20), (200, 90, 30), (255, 170, 60)])
    for (ox, oy, r) in ((30, -14, 10), (48, -22, 13), (66, -14, 10)):
        cv.circle(tx + ox, ty + oy, r, FIRE)
    for (ox, oy, r) in ((36, -12, 6), (52, -18, 7), (62, -12, 5)):
        cv.circle(tx + ox, ty + oy, r, FLAME)
    # smoke plume (kept inside the scene: top >= y+6) + dark core
    for (ox, oy, r) in ((40, -40, 9), (52, -52, 11), (64, -62, 10),
                        (76, -70, 8), (58, -56, 7), (44, -48, 7),
                        (68, -58, 6)):
        cv.circle(tx + ox, ty + oy, r, SMOKE)
    cv.circle(tx + 52, ty - 40, 6, (60, 60, 64))
    # second plume from the distant tanker (kept low, clear of the
    # data panel above it)
    for (ox, oy, r) in ((24, -20, 6), (30, -26, 7), (36, -22, 5)):
        cv.circle(dx + ox, dy + oy, r, SMOKE)
    # fire-glow reflections on the water below the hull
    glow(cv, tx + 52, y + h - 12, 16,
         [(120, 50, 20), (220, 100, 35), (255, 170, 60)])
    for (ry2, rw, col) in ((y + h - 10, 64, (255, 150, 50)),
                           (y + h - 5, 48, (230, 120, 40)),
                           (y + h - 1, 32, (200, 90, 30))):
        cv.fill_rect(tx + 52 - rw // 2, ry2, rw, 2, col)
    # mine label on the water, right of the left mine dot (the old
    # ty+38 spot falls outside the shorter scene)
    cv.text(x + 34, y + h - 7, "NAVAL MINE", 8, True, WHITE)
    # mine dots in water
    for (mx, my) in ((x + 24, sy + 34), (x + w - 30, sy + 30),
                     (x + w - 64, sy + 40)):
        cv.circle(mx, my, 4, (10, 12, 18))
        cv.line(mx - 6, my, mx + 6, my, (10, 12, 18), 1)
        cv.line(mx, my - 6, mx, my + 6, (10, 12, 18), 1)

# ---------------------------------------------------------------- supporting scenes (186 x 62)
def scene_cpi(cv, x, y, w, h):
    """S1: rising CPI bars with +4.9% tag on a cream chip.
    Layers: cream bg + gridlines + shaded bars + value dots + trend
    arrow + outlined chip."""
    vgrad(cv, x, y, w, h, (246, 241, 226), (226, 216, 190))
    # horizontal gridlines
    for gy in (y + 14, y + 26, y + 38):
        cv.fill_rect(x + 8, gy, w - 16, 1, (210, 202, 180))
    bars = [12, 18, 24, 30, 36]
    bw = 22
    for i, bh in enumerate(bars):
        bx = x + 12 + i * 27
        cv.fill_rect(bx, y + h - 8 - bh, bw, bh,
                     (230, 60, 40) if i == 4 else (178, 90, 70))
        # highlight edge + value dot on each bar (hot dot on the last)
        cv.fill_rect(bx, y + h - 8 - bh, 3, bh, (205, 120, 100))
        cv.circle(bx + bw // 2, y + h - 10 - bh,
                  4 if i == 4 else 3,
                  (255, 120, 80) if i == 4 else (120, 40, 30))
    # baseline axis + vertical axis
    cv.fill_rect(x + 8, y + h - 8, w - 16, 2, (120, 110, 90))
    cv.fill_rect(x + 8, y + 10, 1, h - 18, (210, 202, 180))
    # sparkle above the 3rd bar (clear of the chip, top-right)
    sx = x + 80
    cv.line(sx - 3, y + 14, sx + 3, y + 14, (255, 120, 80), 1)
    cv.line(sx, y + 11, sx, y + 17, (255, 120, 80), 1)
    cv.line(x + 12, y + h - 8 - 44, x + w - 12, y + h - 8 - 8, RED, 3)
    # arrowhead at the trend-line end
    ex, ey = x + w - 12, y + h - 8 - 8
    cv.fill_poly([(ex, ey), (ex - 9, ey - 5), (ex - 9, ey + 5)], RED)
    # opaque chip so the tag never sits on a bar (shadow + outline);
    # widened to a fuller data chip
    cv.fill_rect(x + w - 95, y + 7, 92, 20, (150, 140, 120))
    cv.fill_rect(x + w - 96, y + 6, 92, 20, (255, 250, 235))
    rect_outline(cv, x + w - 96, y + 6, 92, 20, RED_BR, 1)
    cv.text(x + w - 8, y + 21, "+4.9% \u00b7 OCT", 13, True, RED, align="right")


def scene_garment(cv, x, y, w, h):
    """S2: garment factory + clothesline.
    Layers: sky band + sun + factory with lit windows + chimney smoke
    + two clothesline rows + white chip behind the metric."""
    vgrad(cv, x, y, w, h, (198, 218, 234), (232, 226, 204))
    # sun with glow
    glow(cv, x + w - 16, y + 9, 12, [(220, 225, 200), (255, 230, 150)])
    cv.circle(x + w - 16, y + 9, 6, (255, 220, 120))
    # two birds, top-left (clear of the sun and chimneys)
    for (bx, by) in ((x + 96, y + 7), (x + 112, y + 11)):
        cv.line(bx - 4, by, bx, by - 2, (90, 90, 80), 1)
        cv.line(bx, by - 2, bx + 4, by, (90, 90, 80), 1)
    # potted plant by the factory door (sits on the shorter scene floor)
    cv.fill_rect(x + 78, y + 59, 6, 6, (150, 110, 70))
    cv.circle(x + 81, y + 57, 4, (90, 140, 70))
    cv.circle(x + 78, y + 60, 2, (110, 160, 90))
    # factory
    cv.fill_rect(x + 10, y + 22, 62, h - 22, (150, 140, 120))
    cv.fill_poly([(x + 10, y + 22), (x + 24, y + 12), (x + 38, y + 22),
                  (x + 52, y + 12), (x + 66, y + 22)], (120, 110, 92))
    cv.fill_rect(x + 62, y + 8, 8, 16, (110, 100, 84))
    cv.fill_rect(x + 30, y + 6, 5, 14, (110, 100, 84))
    # chimney smoke (kept inside the scene)
    cv.circle(x + 66, y + 8, 4, (220, 220, 215))
    cv.circle(x + 70, y + 4, 3, (220, 220, 215))
    cv.circle(x + 32, y + 4, 3, (220, 220, 215))
    for wx in (18, 34, 50):
        cv.fill_rect(x + wx, y + 32, 8, 8, (255, 240, 180))
        cv.fill_rect(x + wx, y + 46, 8, 6, (255, 240, 180))
    # door, bottom-right of the factory (on the shorter scene floor)
    cv.fill_rect(x + 60, y + 53, 10, 12, (90, 80, 66))
    cv.circle(x + 67, y + 59, 1, (255, 220, 130))
    # clothesline (two rows, garments with shadows)
    cv.line(x + 84, y + 16, x + w - 8, y + 16, INK, 1)
    for i, col in enumerate((TEAL, RED_BR, AMBER)):
        sx = x + 92 + i * 30
        cv.fill_rect(sx + 1, y + 33, 20, 2, (180, 175, 155))
        cv.fill_rect(sx, y + 16, 20, 16, col)
        cv.fill_rect(sx, y + 16, 20, 4, WHITE)
    cv.line(x + 96, y + 38, x + w - 8, y + 38, INK_SOFT, 1)
    for i, col in enumerate((AMBER, TEAL)):
        sx = x + 104 + i * 34
        cv.fill_rect(sx + 1, y + 51, 18, 2, (180, 175, 155))
        cv.fill_rect(sx, y + 38, 18, 12, col)
    # full-width data bar, bottom-right (replaces the corner chip:
    # pay + rise, both from the deck)
    cv.fill_rect(x + 97, y + h - 16, 84, 15, (150, 140, 120))
    cv.fill_rect(x + 96, y + h - 17, 84, 15, (255, 250, 235))
    rect_outline(cv, x + 96, y + h - 17, 84, 15, TEAL, 1)
    cv.text(x + 138, y + h - 6, "17,000 TK \u00b7 +36%", 8.5, True, TEAL,
            align="center")


def scene_treaty(cv, x, y, w, h):
    """S3: two flags over a signing table.
    Layers: sky gradient + window + flags with finials + table with
    shadow + document + pens + chairs."""
    vgrad(cv, x, y, w, h, (188, 208, 232), (244, 238, 222))
    # bunting across the top middle (clear of flags and window)
    cv.line(x + 62, y + 4, x + 124, y + 4, INK_SOFT, 1)
    for i, col in enumerate((RED_BR, AMBER, TEAL, RED_BR)):
        bx = x + 70 + i * 14
        cv.fill_poly([(bx, y + 4), (bx + 10, y + 4), (bx + 5, y + 12)], col)
    # window, top-right
    cv.fill_rect(x + w - 34, y + 6, 24, 18, (180, 205, 225))
    cv.fill_rect(x + w - 23, y + 6, 2, 18, WHITE)
    cv.fill_rect(x + w - 34, y + 14, 24, 2, WHITE)
    # aid data chip, top-center between the flags (new: scene had none)
    cv.fill_rect(x + 67, y + 15, 54, 16, (180, 160, 120))
    cv.fill_rect(x + 66, y + 14, 54, 16, (255, 250, 235))
    rect_outline(cv, x + 66, y + 14, 54, 16, RED_BR, 1)
    cv.text(x + 93, y + 26, "A$740M", 9, True, TEAL, align="center")
    # table shadow + table + document + pens
    cv.fill_rect(x + 56, y + h - 16, 78, 3, (200, 192, 170))
    cv.fill_rect(x + 52, y + h - 18, 82, 6, WOOD)
    cv.fill_rect(x + 52, y + h - 16, 82, 1, (120, 84, 44))
    # floor line under the table + inkwell right of the document
    cv.fill_rect(x + 8, y + h - 3, w - 16, 1, (200, 192, 170))
    cv.fill_rect(x + 120, y + h - 28, 5, 5, (30, 30, 36))
    cv.line(x + 122, y + h - 28, x + 126, y + h - 32, INK, 1)
    cv.fill_rect(x + 58, y + h - 12, 5, 12, WOOD)
    cv.fill_rect(x + 123, y + h - 12, 5, 12, WOOD)
    cv.fill_rect(x + 76, y + h - 26, 34, 9, WHITE)
    cv.line(x + 80, y + h - 23, x + 106, y + h - 23, INK_SOFT, 1)
    cv.line(x + 80, y + h - 20, x + 100, y + h - 20, INK_SOFT, 1)
    cv.circle(x + 104, y + h - 22, 3, RED_BR)
    cv.line(x + 112, y + h - 27, x + 116, y + h - 22, INK, 1)
    # chairs with backs
    cv.fill_rect(x + 44, y + h - 26, 6, 14, (120, 100, 70))
    cv.fill_rect(x + 44, y + h - 34, 6, 8, (120, 100, 70))
    cv.fill_rect(x + 140, y + h - 26, 6, 14, (120, 100, 70))
    cv.fill_rect(x + 140, y + h - 34, 6, 8, (120, 100, 70))
    # Australia flag (left)
    cv.fill_rect(x + 16, y + 8, 8, 34, INK)
    cv.circle(x + 20, y + 6, 2, (255, 220, 60))
    cv.fill_rect(x + 24, y + 8, 34, 20, (0, 40, 110))
    cv.circle(x + 32, y + 18, 3, WHITE)
    cv.circle(x + 46, y + 14, 2, WHITE)
    cv.circle(x + 50, y + 22, 2, WHITE)
    # Solomons flag (right)
    cv.fill_rect(x + 128, y + 8, 8, 34, INK)
    cv.circle(x + 132, y + 6, 2, (255, 220, 60))
    cv.fill_poly([(x + 136, y + 8), (x + 170, y + 8), (x + 170, y + 28)],
                 (0, 90, 160))
    cv.fill_poly([(x + 136, y + 28), (x + 170, y + 28), (x + 136, y + 8)],
                 (0, 140, 70))
    cv.circle(x + 144, y + 13, 2, (255, 220, 60))
    cv.circle(x + 152, y + 13, 2, (255, 220, 60))
    cv.circle(x + 160, y + 13, 2, (255, 220, 60))


def scene_store(cv, x, y, w, h):
    """S4: supermarket front with striped awning.
    Layers: sky band + sun + storefront with shaded awning + windows
    with reflections + door + figures + cart + tree + pavement."""
    vgrad(cv, x, y, w, h, (198, 218, 234), (236, 228, 208))
    # sky band + sun
    cv.fill_rect(x, y, w, 12, (198, 218, 234))
    cv.circle(x + w - 14, y + 8, 5, (255, 220, 120))
    cv.fill_rect(x + 12, y + 18, w - 24, h - 18, (240, 232, 210))
    rect_outline(cv, x + 12, y + 18, w - 24, h - 18, INK_SOFT, 1)
    # sign band above the awning
    cv.fill_rect(x + 12, y + 13, w - 24, 5, RED_BR)
    cv.fill_rect(x + 12, y + 13, w - 24, 1, (255, 150, 120))
    # striped awning (with shade under it)
    for i in range(8):
        col = RED_BR if i % 2 == 0 else WHITE
        cv.fill_poly([(x + 12 + i * 20, y + 18), (x + 32 + i * 20, y + 18),
                      (x + 28 + i * 20, y + 30), (x + 8 + i * 20, y + 30)],
                     col)
    cv.fill_rect(x + 12, y + 30, w - 24, 3, (210, 200, 175))
    # scalloped awning edge
    for i in range(8):
        col = RED_BR if i % 2 == 0 else WHITE
        cv.circle(x + 22 + i * 20, y + 31, 3, col)
    # windows with reflections + door
    cv.fill_rect(x + 22, y + 36, 26, 16, (90, 130, 170))
    cv.line(x + 24, y + 38, x + 46, y + 50, (200, 220, 235), 1)
    cv.fill_rect(x + 138, y + 36, 26, 16, (90, 130, 170))
    cv.line(x + 140, y + 38, x + 162, y + 50, (200, 220, 235), 1)
    cv.fill_rect(x + 80, y + 36, 26, h - 36, (90, 70, 50))
    cv.circle(x + 100, y + 48, 2, (255, 220, 120))
    # three figures with ground shadows (feet on the shorter scene floor)
    for fx, col in ((58, TEAL), (128, TEAL), (118, RED_BR)):
        cv.fill_rect(x + fx - 6, y + 63, 12, 2, (180, 170, 145))
        cv.circle(x + fx, y + 52, 4, (40, 40, 40))
        cv.fill_rect(x + fx - 4, y + 56, 8, 9, col)
    # shopping cart, bottom-left (with goods) + pavement
    cv.fill_rect(x + 4, y + h - 8, w - 8, 2, (180, 170, 145))
    cv.line(x + 6, y + h - 16, x + 20, y + h - 16, INK, 1)
    cv.fill_rect(x + 7, y + h - 20, 6, 4, TEAL)
    cv.fill_rect(x + 13, y + h - 22, 5, 6, RED_BR)
    cv.line(x + 6, y + h - 16, x + 8, y + h - 8, INK, 1)
    cv.line(x + 20, y + h - 16, x + 18, y + h - 8, INK, 1)
    cv.circle(x + 9, y + h - 6, 2, INK)
    cv.circle(x + 17, y + h - 6, 2, INK)
    # tree, right edge
    cv.fill_rect(x + w - 12, y + 34, 3, 22, (90, 70, 50))
    cv.circle(x + w - 10, y + 30, 7, (90, 140, 70))
    cv.circle(x + w - 6, y + 36, 4, (130, 185, 130))
    # second small tree, left edge (clear of the window and cart)
    cv.fill_rect(x + 3, y + 36, 3, 8, (90, 70, 50))
    cv.circle(x + 5, y + 32, 5, (90, 140, 70))
    cv.circle(x + 9, y + 37, 3, (130, 185, 130))
    # pavement edge line above the cart strip
    cv.fill_rect(x + 4, y + h - 10, w - 8, 1, (200, 190, 165))


def scene_tariffs(cv, x, y, w, h):
    """S5: US Capitol dome + red tariff tags.
    Layers: night gradient + stars + flag + statue + shaded dome +
    steps + glowing tags."""
    vgrad(cv, x, y, w, h, NAVY, NAVY_LT)
    # starfield regions pinned to the v2.5 heights (h was 70): the seeded
    # placement is sy = y + s % region, so deriving the region from the
    # new h=67 would reshuffle stars and can push a star 1px over the
    # scene's top edge. Regions sit at the scene top, all inside 67px.
    starfield(cv, x, y, w, 23, 4242)
    starfield(cv, x, y, w, 35, 777)
    # flag pole + flag, left (clear of the "16" tag) + white star dot
    cv.fill_rect(x + 10, y + 10, 3, 34, (200, 200, 205))
    cv.fill_poly([(x + 13, y + 10), (x + 30, y + 14), (x + 13, y + 18)],
                 (180, 40, 40))
    cv.circle(x + 19, y + 14, 1, WHITE)
    # dome (shaded: light left, shadow right) + statue with glow
    dx = x + w // 2
    glow(cv, dx, y + 4, 8,
         [(30, 32, 44), (90, 100, 140), (220, 220, 230)])
    cv.fill_poly([(dx - 26, y + 34), (dx + 26, y + 34), (dx, y + 12)], WHITE)
    cv.fill_poly([(dx, y + 34), (dx + 26, y + 34), (dx, y + 12)],
                 (200, 200, 205))
    cv.line(dx - 26, y + 34, dx, y + 12, WHITE, 2)
    cv.fill_rect(dx - 34, y + 34, 68, 8, WHITE)
    cv.fill_rect(dx - 2, y + 6, 4, 8, WHITE)
    cv.circle(dx, y + 4, 3, WHITE)
    cv.fill_rect(dx - 42, y + 42, 84, 6, WHITE)
    # warm lit dots on the architrave band + thin gold line above them
    for wx in (dx - 30, dx - 10, dx + 10, dx + 30):
        cv.circle(wx, y + 45, 2, (255, 220, 130))
    cv.fill_rect(dx - 38, y + 41, 76, 1, (255, 220, 130))
    # two sparkles in the night sky (clear of flag, tags, dome)
    for (sx, sy) in ((x + 70, y + 8), (x + w - 62, y + 34)):
        cv.line(sx - 3, sy, sx + 3, sy, WHITE, 1)
        cv.line(sx, sy - 3, sx, sy + 3, WHITE, 1)
    for cx in range(dx - 38, dx + 40, 12):
        cv.fill_rect(cx, y + 54, 5, 11, WHITE)
        cv.fill_rect(cx + 3, y + 54, 2, 11, (210, 210, 215))
    # steps
    cv.fill_rect(dx - 46, y + h - 8, 92, 4, (200, 200, 205))
    cv.fill_rect(dx - 40, y + h - 12, 80, 3, (170, 170, 178))
    # tariff tags (shadow + warm outline so they read at thumbnail)
    cv.fill_rect(x + 33, y + 9, 28, 16, (120, 30, 30))
    cv.fill_rect(x + 34, y + 10, 26, 14, RED_BR)
    rect_outline(cv, x + 34, y + 10, 26, 14, (255, 150, 120), 1)
    cv.text(x + 47, y + 21, "16", 10, True, WHITE, align="center")
    cv.fill_rect(x + w - 37, y + 11, 28, 16, (120, 30, 30))
    cv.fill_rect(x + w - 36, y + 12, 26, 14, RED_BR)
    rect_outline(cv, x + w - 36, y + 12, 26, 14, (255, 150, 120), 1)
    cv.text(x + w - 23, y + 23, "%", 11, True, WHITE, align="center")


def scene_pyongyang(cv, x, y, w, h):
    """S6: Ryugyong pyramid hotel + flag, night.
    Layers: night gradient + stars + moon halo + pyramid with lit
    windows + smaller building + ground lights + dark chip for 48H."""
    vgrad(cv, x, y, w, h, (16, 22, 48), (40, 52, 92))
    # starfield region pinned to the v2.5 height (h was 70): seeded
    # placement is sy = y + s % region, so h - 20 = 47 would reshuffle
    # stars vs v2.5. Region sits at the scene top, inside 67px.
    starfield(cv, x, y, w, 50, 777)
    # moon + halo, top-right (halo kept inside the scene)
    glow(cv, x + w - 22, y + 12, 18,
         [(30, 36, 66), (90, 100, 140), (220, 220, 230)])
    cv.circle(x + w - 22, y + 12, 8, (235, 233, 220))
    # pyramid hotel
    px = x + w // 2
    cv.fill_poly([(px - 46, y + h - 6), (px + 46, y + h - 6),
                  (px, y + 8)], (70, 78, 100))
    for wy in range(y + 18, y + h - 8, 8):
        t = (wy - (y + 8)) / max(1, (y + h - 6) - (y + 8))
        hw = 46 * (1 - t)
        cv.fill_rect(px - hw, wy, 2 * hw, 1, (200, 200, 210))
    # left-edge highlight on the pyramid + right-slope highlight
    cv.line(px - 46, y + h - 6, px, y + 8, (150, 160, 190), 2)
    cv.line(px + 46, y + h - 6, px, y + 8, (110, 118, 150), 1)
    # lit windows on the pyramid (warm dots, all inside the slopes)
    for (wx, wy) in ((px - 20, y + 30), (px + 8, y + 26), (px - 6, y + 38),
                     (px + 12, y + 40), (px - 5, y + 48), (px + 2, y + 20),
                     (px - 8, y + 44), (px + 2, y + 50), (px - 18, y + 34),
                     (px + 18, y + 32), (px + 6, y + 46)):
        cv.fill_rect(wx, wy, 3, 3, (255, 220, 130))
    cv.fill_rect(px - 3, y + 4, 6, 8, (220, 60, 60))
    # smaller building silhouette, left (clear of flag + 48H chip)
    cv.fill_rect(x + 50, y + h - 26, 20, 20, (28, 34, 60))
    cv.fill_rect(x + 54, y + h - 22, 4, 4, (255, 220, 130))
    cv.fill_rect(x + 62, y + h - 22, 4, 4, (255, 220, 130))
    # flag pole + flag + white dot
    cv.fill_rect(x + 12, y + 14, 3, h - 14, INK)
    cv.fill_poly([(x + 15, y + 14), (x + 44, y + 18), (x + 15, y + 24)],
                 (200, 40, 40))
    cv.circle(x + 22, y + 19, 2, WHITE)
    # ground lights (kept left of the widened chip, clear of the pyramid)
    for gx in (x + 74, x + 82, x + 90):
        cv.circle(gx, y + h - 8, 2, (255, 220, 130))
    cv.fill_rect(x, y + h - 4, w, 2, (90, 110, 170))
    # dark chip behind the metric, widened to the full fact (shadow + outline)
    tw = text_width("48H TO LEAVE", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + h - 19, tw + 12, 17, (0, 0, 0))
    cv.fill_rect(x + w - 8 - tw - 8, y + h - 20, tw + 12, 17, (12, 16, 34))
    rect_outline(cv, x + w - 8 - tw - 8, y + h - 20, tw + 12, 17,
                 (255, 220, 130), 1)
    cv.text(x + w - 8, y + h - 6, "48H TO LEAVE", 9, True, WHITE,
            align="right")


def scene_court(cv, x, y, w, h):
    """S7: courtroom — gavel, scales, columns.
    Layers: warm bg + wall panels + columns with capitals + bench
    with shadow + books + gavel + scales + flag banner + cream chip
    behind GUILTY."""
    vgrad(cv, x, y, w, h, (234, 220, 188), (214, 196, 158))
    # wall panels
    for px in (x + 30, x + w - 32):
        cv.fill_rect(px, y + 6, 2, h - 12, (200, 182, 140))
    # columns with capitals + bases
    for cx in (x + 12, x + w - 20):
        cv.fill_rect(cx - 2, y + 6, 12, 4, (214, 198, 158))
        cv.fill_rect(cx, y + 8, 8, h - 8, (200, 182, 140))
        cv.fill_rect(cx, y + 8, 3, h - 8, (214, 198, 158))
        cv.fill_rect(cx - 2, y + h - 6, 12, 4, (214, 198, 158))
    # bench shadow + bench
    cv.fill_rect(x + 36, y + h - 18, w - 72, 3, (180, 160, 120))
    cv.fill_rect(x + 34, y + h - 20, w - 68, 6, WOOD)
    cv.fill_rect(x + 40, y + h - 14, 5, 14, WOOD)
    cv.fill_rect(x + w - 45, y + h - 14, 5, 14, WOOD)
    # books on the bench, left + a second stack, right
    cv.fill_rect(x + 44, y + h - 28, 18, 4, (120, 40, 40))
    cv.fill_rect(x + 46, y + h - 32, 15, 4, (40, 70, 110))
    cv.fill_rect(x + w - 66, y + h - 28, 16, 4, (40, 110, 60))
    cv.fill_rect(x + w - 64, y + h - 32, 13, 4, (150, 120, 50))
    # rug on the floor between the bench legs
    cv.fill_rect(x + 70, y + h - 4, 46, 2, (140, 40, 40))
    # gavel
    cv.fill_poly([(x + 66, y + 22), (x + 96, y + 22), (x + 96, y + 32),
                  (x + 66, y + 32)], (120, 84, 44))
    cv.fill_rect(x + 66, y + 22, 30, 3, (150, 110, 60))
    cv.line(x + 96, y + 27, x + 128, y + 40, (120, 84, 44), 4)
    cv.fill_rect(x + 62, y + 40, 76, 4, (120, 84, 44))
    cv.fill_rect(x + 62, y + 40, 76, 1, (170, 130, 80))
    # scales (with chains from beam ends to pan apexes)
    sx = x + w // 2
    cv.line(sx, y + 14, sx, y + 34, INK, 2)
    cv.line(sx - 16, y + 18, sx + 16, y + 18, INK, 2)
    cv.line(sx - 16, y + 18, sx - 16, y + 24, INK, 1)
    cv.line(sx + 16, y + 18, sx + 16, y + 24, INK, 1)
    cv.fill_poly([(sx - 24, y + 34), (sx - 8, y + 34), (sx - 16, y + 24)],
                 (150, 130, 80))
    cv.fill_poly([(sx + 8, y + 34), (sx + 24, y + 34), (sx + 16, y + 24)],
                 (150, 130, 80))
    # flag banner, right edge (two-tone, clear of the GUILTY chip)
    cv.fill_rect(x + w - 8, y + 22, 3, 26, (120, 100, 70))
    cv.fill_poly([(x + w - 5, y + 22), (x + w - 22, y + 26),
                  (x + w - 5, y + 30)], (140, 40, 40))
    cv.fill_poly([(x + w - 5, y + 32), (x + w - 22, y + 36),
                  (x + w - 5, y + 40)], (180, 60, 60))
    # sentencing data chip, top-left (new: second fact on the card)
    cv.fill_rect(x + 25, y + 3, 52, 16, (180, 160, 120))
    cv.fill_rect(x + 24, y + 2, 52, 16, (255, 250, 235))
    rect_outline(cv, x + 24, y + 2, 52, 16, RED_BR, 1)
    cv.text(x + 28, y + 14, "MAR 2027", 9, True, RED)
    # cream chip behind the GUILTY metric (shadow + outline)
    tw = text_width("GUILTY", 10, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 16, (180, 160, 120))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 16, (255, 250, 235))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 16, RED_BR, 1)
    cv.text(x + w - 8, y + 14, "GUILTY", 10, True, RED, align="right")


def scene_mine(cv, x, y, w, h):
    """S8: flooded gold-mine shaft cross-section.
    Layers: earth with pebbles + timber supports + diagonal shaft +
    rope + lamp glow + cart + rocks + shimmering water + dark chip
    behind 100 M."""
    cv.fill_rect(x, y, w, h, EARTH)
    for i in range(8):
        cv.circle(x + 12 + (i * 23) % (w - 20), y + 8 + (i * 7) % 14, 3,
                  EARTH_DK)
    # earth strata bands (drawn before the shaft, so the tunnel cuts them)
    cv.fill_rect(x, y + 16, w, 2, (104, 76, 50))
    cv.fill_rect(x, y + 38, w, 2, (104, 76, 50))
    # timber supports across the shaft + two more on the earth
    cv.line(x + 36, y + 6, x + 52, y + 6, (90, 66, 40), 3)
    cv.line(x + 62, y + 34, x + 78, y + 34, (90, 66, 40), 3)
    cv.line(x + 20, y + 20, x + 36, y + 20, (90, 66, 40), 3)
    cv.line(x + 100, y + 48, x + 116, y + 48, (90, 66, 40), 3)
    # shaft (diagonal dark tunnel)
    cv.fill_poly([(x + 30, y), (x + 52, y), (x + 96, y + h),
                  (x + 74, y + h)], (28, 20, 14))
    # ladder rungs along the shaft centerline
    for (rx, ry) in ((52, 16), (59, 25), (65, 34), (72, 43)):
        cv.line(x + rx - 5, y + ry + 4, x + rx + 5, y + ry - 4,
                (200, 170, 120), 1)
    # water at bottom + shimmer + lamp reflection streak
    cv.fill_rect(x, y + h - 12, w, 12, (40, 90, 130))
    cv.line(x + 10, y + h - 8, x + 60, y + h - 8, (140, 180, 220), 1)
    cv.line(x + 110, y + h - 5, x + 170, y + h - 5, (140, 180, 220), 1)
    cv.fill_rect(x + 80, y + h - 10, 8, 10, (200, 160, 80))
    # rope + helmet lamp + glow
    cv.line(x + 60, y, x + 96, y + h - 12, (220, 200, 150), 2)
    glow(cv, x + 84, y + 30, 20,
         [(90, 70, 30), (180, 140, 60), (255, 220, 120)])
    cv.circle(x + 84, y + 30, 5, FLAME)
    cv.circle(x + 84, y + 30, 9, (255, 220, 120))
    cv.fill_rect(x + 76, y + 38, 16, 6, (240, 200, 60))
    # ore cart, bottom-left (with gold lumps)
    cv.fill_rect(x + 12, y + h - 24, 22, 10, (70, 52, 36))
    cv.circle(x + 28, y + h - 25, 2, (240, 200, 60))
    cv.circle(x + 32, y + h - 26, 2, (240, 200, 60))
    cv.circle(x + 18, y + h - 12, 3, (30, 24, 18))
    cv.circle(x + 28, y + h - 12, 3, (30, 24, 18))
    # rocks
    cv.fill_poly([(x + 8, y + h - 14), (x + 26, y + h - 14),
                  (x + 17, y + h - 26)], (100, 84, 66))
    cv.fill_poly([(x + 150, y + h - 12), (x + 164, y + h - 12),
                  (x + 157, y + h - 22)], (100, 84, 66))
    # stalactite from the top edge (moved left: the widened chip covers
    # the old spot) + gold glints
    cv.fill_poly([(x + 100, y), (x + 108, y), (x + 104, y + 10)],
                 (100, 84, 66))
    for (gx, gy) in ((x + 160, y + h - 18), (x + 152, y + 24)):
        cv.line(gx - 2, gy, gx + 2, gy, (255, 220, 120), 1)
        cv.line(gx, gy - 2, gx, gy + 2, (255, 220, 120), 1)
    # dark chip behind the metric, widened to depth + unit (shadow + outline)
    tw = text_width("100 M DEEP", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 15, (0, 0, 0))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 15, (20, 16, 12))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 15,
                 (255, 220, 120), 1)
    cv.text(x + w - 8, y + 14, "100 M DEEP", 9, True, WHITE, align="right")


def scene_blast(cv, x, y, w, h):
    """S9: lead-azide blast fireball.
    Layers: dusk gradient + ground + cracks + shock rings + fireball
    glow + smoke + debris + barrels + dark chip behind 9 AM CT."""
    # dusk gradient in three bands (hotter horizon at mid-height)
    vgrad(cv, x, y, w, h // 2, (30, 26, 22), (80, 55, 35))
    vgrad(cv, x, y + h // 2, w, h - h // 2, (80, 55, 35), (24, 20, 18))
    cx, cy = x + w // 2, y + h - 16
    # ground + cracks
    cv.fill_rect(x, y + h - 10, w, 10, (24, 20, 18))
    cv.line(x + 20, y + h - 6, x + 44, y + h - 2, (60, 50, 40), 1)
    cv.line(x + 140, y + h - 8, x + 168, y + h - 3, (60, 50, 40), 1)
    # shock rings (kept inside the scene: cy-r >= y)
    cv.ring(cx, cy, 44, 42, (200, 180, 140))
    cv.ring(cx, cy, 32, 30, (220, 200, 160))
    # fireball glow + outer ring + fireball + hot core
    glow(cv, cx, cy - 6, 34,
         [(90, 40, 16), (190, 90, 30), (255, 170, 60)])
    cv.ring(cx, cy - 6, 30, 28, (200, 120, 50))
    cv.circle(cx, cy - 6, 26, FIRE)
    cv.circle(cx, cy - 10, 18, FLAME)
    cv.circle(cx - 6, cy - 14, 12, (255, 240, 180))
    # smoke (kept inside the scene: tops >= y) + dark cores
    for (ox, oy, r) in ((-34, -30, 9), (-22, -36, 10), (24, -34, 9),
                        (26, -34, 8), (0, -38, 8), (-46, -24, 7),
                        (34, -32, 7)):
        cv.circle(cx + ox, cy + oy, r, SMOKE)
    for (ox, oy, r) in ((-22, -36, 4), (26, -34, 4)):
        cv.circle(cx + ox, cy + oy, r, (40, 35, 30))
    # two more smoke puffs, upper left (clear of the 9 AM CT chip)
    cv.circle(cx - 72, cy - 36, 6, SMOKE)
    cv.circle(cx - 84, cy - 30, 5, SMOKE)
    # one more debris streak, upper left
    cv.line(cx - 58, cy - 40, cx - 44, cy - 32, (120, 100, 80), 1)
    # flying debris (kept clear of the 9 AM CT chip, top-right)
    for (dx, dy) in ((cx - 44, cy - 22), (cx + 46, cy - 18),
                     (cx - 52, cy - 34), (cx - 60, cy - 18)):
        cv.fill_rect(dx, dy, 3, 3, (30, 26, 22))
    # debris motion streaks trailing toward the center
    for (ax, ay, bx, by) in ((cx - 44, cy - 22, cx - 30, cy - 16),
                             (cx + 46, cy - 18, cx + 32, cy - 14),
                             (cx - 52, cy - 34, cx - 38, cy - 26),
                             (cx - 60, cy - 18, cx - 46, cy - 14)):
        cv.line(ax, ay, bx, by, (120, 100, 80), 1)
    # barrels (hazard band + highlight edge)
    for bx in (x + 12, x + 26):
        cv.fill_rect(bx, y + h - 14, 10, 12, (120, 110, 100))
        cv.fill_rect(bx, y + h - 14, 10, 3, (90, 82, 74))
        cv.fill_rect(bx, y + h - 9, 10, 2, (255, 200, 60))
        cv.fill_rect(bx, y + h - 14, 2, 12, (180, 170, 160))
    # dark chip behind the metric, widened to time + barrels (shadow + outline)
    tw = text_width("9 AM CT \u00b7 68 BARRELS", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 15, (0, 0, 0))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 15, (16, 14, 12))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 15,
                 (255, 220, 120), 1)
    cv.text(x + w - 8, y + 12, "9 AM CT \u00b7 68 BARRELS", 9, True, WHITE,
            align="right")


def scene_births(cv, x, y, w, h):
    """S10: crib + rising births curve.
    Layers: sky gradient + window + sun + rising curve with dots +
    crib with blanket + mobile moon/star + white chip for +12.2%."""
    vgrad(cv, x, y, w, h, (214, 230, 240), (240, 238, 226))
    # window, top-left + sun with rays
    cv.fill_rect(x + 8, y + 6, 20, 16, (170, 205, 230))
    cv.fill_rect(x + 17, y + 6, 2, 16, WHITE)
    cv.fill_rect(x + 8, y + 13, 20, 2, WHITE)
    cv.circle(x + 18, y + 14, 4, (255, 220, 120))
    for (ax, ay, bx, by) in ((x + 12, y + 8, x + 15, y + 11),
                             (x + 24, y + 8, x + 21, y + 11),
                             (x + 12, y + 20, x + 15, y + 17),
                             (x + 24, y + 20, x + 21, y + 17)):
        cv.line(ax, ay, bx, by, (255, 200, 100), 1)
    # rising curve (ends clear of the +12.2% chip, top-right)
    pts = [(x + 10, y + 44), (x + 50, y + 40), (x + 90, y + 34),
           (x + 122, y + 28)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], TEAL, 3)
    for (px, py) in pts:
        cv.circle(px, py, 3, TEAL)
    # amber sparkles above the curve
    for (sx, sy) in ((x + 34, y + 30), (x + 70, y + 24)):
        cv.line(sx - 3, sy, sx + 3, sy, AMBER, 1)
        cv.line(sx, sy - 3, sx, sy + 3, AMBER, 1)
    # crib shadow + crib (sits on the taller scene floor)
    cx = x + w // 2
    cv.fill_rect(cx - 32, y + 62, 68, 3, (200, 196, 180))
    cv.fill_rect(cx - 34, y + 38, 68, 6, WOOD)
    for rx in range(cx - 34, cx + 36, 8):
        cv.fill_rect(rx, y + 44, 3, 18, WOOD)
    cv.fill_rect(cx - 34, y + 60, 68, 4, WOOD)
    cv.fill_rect(cx - 30, y + 44, 60, 8, (250, 245, 235))
    # blanket fold + top-edge line + pillow under the left head
    cv.fill_rect(cx - 30, y + 48, 60, 2, (200, 170, 190))
    cv.fill_rect(cx - 30, y + 44, 60, 1, (180, 150, 170))
    cv.fill_rect(cx - 30, y + 46, 12, 5, WHITE)
    cv.circle(cx - 12, y + 40, 6, (255, 220, 200))
    cv.circle(cx + 12, y + 40, 6, (255, 220, 200))
    # mobile: moon + stars hanging
    cv.line(cx, y + 6, cx, y + 18, INK_SOFT, 1)
    cv.circle(cx - 10, y + 20, 2, AMBER)
    cv.circle(cx + 10, y + 20, 2, RED_BR)
    cv.circle(cx - 22, y + 16, 3, (255, 230, 150))
    cv.circle(cx + 22, y + 16, 2, AMBER)
    # two more mobile stars + one more sparkle above the curve
    cv.circle(cx - 34, y + 22, 2, RED_BR)
    cv.circle(cx + 34, y + 24, 2, AMBER)
    cv.line(x + 96, y + 18, x + 102, y + 18, AMBER, 1)
    cv.line(x + 99, y + 15, x + 99, y + 21, AMBER, 1)
    # white chip behind the +12.2% metric (shadow + TEAL outline)
    tw = text_width("+12.2%", 11, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 17, (200, 196, 180))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 17,
                 (255, 252, 240))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 17, TEAL, 1)
    cv.text(x + w - 8, y + 12, "+12.2%", 11, True, TEAL, align="right")


def scene_macaw(cv, x, y, w, h):
    """A9 (#22): Spix's macaw chick Hope hatches.
    Layers: sky gradient + sun + branch + leaves + blue macaw
    (yellow chest, white face, long tail) + pale chick + HOPE chip."""
    vgrad(cv, x, y, w, h, (198, 224, 238), (246, 240, 224))
    # sun with short rays, above the chick (clear of the HOPE chip)
    cv.circle(x + 88, y + 10, 6, (255, 220, 120))
    for (ax, ay, bx, by) in ((x + 78, y + 10, x + 81, y + 10),
                             (x + 95, y + 10, x + 98, y + 10),
                             (x + 88, y + 2, x + 88, y + 5)):
        cv.line(ax, ay, bx, by, (255, 200, 100), 1)
    # branch (slight diagonal) + leaves
    cv.fill_poly([(x + 6, y + h - 12), (x + w - 6, y + h - 16),
                  (x + w - 6, y + h - 12), (x + 6, y + h - 8)], WOOD)
    for (lx, ly, dx, dy) in ((x + 18, y + h - 16, -8, -6),
                             (x + 130, y + h - 18, 8, -7),
                             (x + 142, y + h - 16, 6, -4)):
        cv.fill_poly([(lx, ly), (lx + dx, ly + dy), (lx + dx + 4, ly + 2)],
                     GREEN)
    # macaw: tail (long, down-right), body, wing, head, beak, face patch
    bx, by = x + 52, y + 20
    cv.fill_poly([(bx + 4, by + 6), (bx + 26, by + 16), (bx + 22, by + 20),
                  (bx + 2, by + 10)], (28, 64, 128))
    cv.circle(bx, by, 10, (36, 80, 180))
    cv.fill_poly([(bx - 8, by - 6), (bx + 2, by - 10), (bx + 4, by + 2),
                  (bx - 6, by + 6)], (28, 64, 128))
    cv.circle(bx - 2, by - 2, 5, (255, 210, 60))
    cv.circle(bx - 4, by - 12, 6, (36, 80, 180))
    cv.circle(bx - 8, by - 13, 3, WHITE)
    cv.fill_poly([(bx + 1, by - 13), (bx + 9, by - 10), (bx + 1, by - 8)],
                 (240, 170, 40))
    cv.circle(bx - 5, by - 14, 1, INK)
    # chick: pale fluff ball on the branch, right of the adult
    cx, cy = x + 104, y + h - 20
    cv.circle(cx, cy, 6, (238, 232, 218))
    cv.circle(cx - 3, cy - 6, 4, (245, 240, 228))
    cv.fill_poly([(cx + 1, cy - 7), (cx + 6, cy - 5), (cx + 1, cy - 4)],
                 (240, 170, 40))
    cv.circle(cx - 4, cy - 7, 1, INK)
    # white chip behind HOPE (shadow + TEAL outline)
    tw = text_width("HOPE", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 15, (200, 196, 180))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 15, (255, 252, 240))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 15, TEAL, 1)
    cv.text(x + w - 8, y + 12, "HOPE", 9, True, TEAL, align="right")


def scene_dragonfly(cv, x, y, w, h):
    """A11 (#24): Dragonfly Titan parts arrive.
    Layers: night gradient + starfield + Titan haze disc + rotorcraft
    (body, 4 rotor arms, rotor discs, legs) + TITAN chip."""
    vgrad(cv, x, y, w, h, SKY_NIGHT, (30, 40, 80))
    starfield(cv, x, y, w, h, 7)
    # Titan: orange haze dome rising from the tile's bottom edge.
    # Drawn as half-discs (flat side on y+h) so nothing spills below
    # the tile into the label / legend rows.
    tx = x + 42
    for rr, c in ((28, (120, 70, 30)), (20, (200, 130, 60)),
                  (12, (240, 180, 100))):
        pts = [(tx + rr * math.cos(math.radians(a)),
                y + h + rr * math.sin(math.radians(a)))
               for a in range(180, 361, 10)]
        cv.fill_poly(pts, c)
    for rr, c in ((24, DUSK2), (18, DUSK3)):
        pts = [(tx + rr * math.cos(math.radians(a)),
                y + h + rr * math.sin(math.radians(a)))
               for a in range(180, 361, 10)]
        cv.fill_poly(pts, c)
    # Dragonfly rotorcraft, centre-right
    dx, dy = x + 112, y + 24
    cv.fill_rect(dx - 7, dy - 2, 14, 5, (220, 224, 230))
    cv.fill_rect(dx - 7, dy - 2, 14, 2, WHITE)
    for (ox, oy) in ((-12, -6), (12, -6), (-12, 6), (12, 6)):
        cv.line(dx, dy, dx + ox, dy + oy, (180, 186, 196), 1)
        cv.line(dx + ox - 7, dy + oy, dx + ox + 7, dy + oy,
                (220, 224, 230), 1)
    cv.line(dx - 4, dy + 3, dx - 6, dy + 9, (180, 186, 196), 1)
    cv.line(dx + 4, dy + 3, dx + 6, dy + 9, (180, 186, 196), 1)
    cv.circle(dx + 5, dy, 2, (255, 220, 120))
    # dark chip behind TITAN (shadow + amber outline)
    tw = text_width("TITAN", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 15, (0, 0, 0))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 15, (16, 14, 12))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 15,
                 (255, 220, 120), 1)
    cv.text(x + w - 8, y + 12, "TITAN", 9, True, WHITE, align="right")


def scene_iwo(cv, x, y, w, h):
    """A19 (#32): Iwo Jima eruption adds new land.
    Layers: dusk gradient + sea band + volcano cone + eruption plume
    (smoke + fire core) + lava streaks + new-land islet + NEW LAND chip."""
    vgrad(cv, x, y, w, h // 2 + 8, DUSK3, DUSK1)
    vgrad(cv, x, y + h // 2 + 8, w, h - h // 2 - 8, DUSK1, (90, 60, 40))
    # sea band + wave lines
    cv.fill_rect(x, y + h - 12, w, 12, SEA_DK)
    cv.line(x + 8, y + h - 8, x + 30, y + h - 8, (120, 160, 200), 1)
    cv.line(x + 120, y + h - 5, x + 152, y + h - 5, (120, 160, 200), 1)
    # volcano cone (peak clear of the badge, base on the sea)
    px, py = x + 70, y + 12
    cv.fill_poly([(x + 28, y + h - 10), (px - 8, py), (px + 8, py),
                  (x + 112, y + h - 10)], EARTH_DK)
    cv.fill_poly([(x + 28, y + h - 10), (px - 8, py), (px - 2, py + 10),
                  (x + 46, y + h - 10)], (70, 48, 32))
    # eruption plume: smoke puffs + fire core at the crater
    # (all tops >= y+1: nothing crosses the tile's top border)
    for (ox, oy, r) in ((-6, -6, 5), (4, -6, 5), (0, -7, 4), (-12, -2, 4),
                        (12, -3, 4)):
        cv.circle(px + ox, py + oy, r, SMOKE)
    cv.circle(px, py - 2, 4, FIRE)
    cv.circle(px, py - 3, 2, FLAME)
    # lava streaks down the cone
    cv.line(px - 2, py + 4, px - 8, py + 18, (255, 140, 40), 1)
    cv.line(px + 3, py + 4, px + 10, py + 16, (255, 170, 60), 1)
    # new-land islet in the sea + wisp of smoke
    cv.fill_poly([(x + 124, y + h - 4), (x + 132, y + h - 12),
                  (x + 140, y + h - 12), (x + 150, y + h - 4)], EARTH_DK)
    cv.circle(x + 136, y + h - 14, 3, SMOKE)
    # white chip behind NEW LAND (shadow + RED outline)
    tw = text_width("NEW LAND", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 15, (200, 196, 180))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 15, (255, 252, 240))
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 15, RED_BR, 1)
    cv.text(x + w - 8, y + 12, "NEW LAND", 9, True, RED_BR, align="right")


def scene_hockey(cv, x, y, w, h):
    """A21 (#34): Canada women win Para hockey 10-0.
    Layers: ice gradient + boards + rink lines + faceoff rings +
    two sledge players + puck + goal posts + 10-0 chip."""
    vgrad(cv, x, y, w, h, (228, 236, 246), (198, 214, 230))
    # boards (top edge) + rink lines + faceoff rings
    cv.fill_rect(x, y, w, 3, (60, 70, 90))
    cv.line(x, y + 22, x + w, y + 22, RED, 1)
    cv.line(x, y + 10, x + w, y + 10, BLUE, 1)
    cv.line(x, y + 34, x + w, y + 34, BLUE, 1)
    cv.ring(x + 26, y + 22, 8, 7, RED)
    cv.ring(x + w - 46, y + 22, 8, 7, BLUE)
    # goal posts, bottom-right (below the 10-0 chip)
    cv.fill_rect(x + w - 16, y + h - 14, 2, 14, RED)
    cv.fill_rect(x + w - 6, y + h - 14, 2, 14, RED)
    cv.fill_rect(x + w - 16, y + h - 14, 12, 2, RED)
    # sledge player 1 (red) + stick + puck near the goal
    px, py = x + 96, y + 26
    cv.fill_rect(px - 10, py + 2, 20, 4, (120, 120, 126))
    cv.fill_rect(px - 6, py - 6, 12, 9, RED_BR)
    cv.circle(px - 2, py - 10, 4, (40, 40, 48))
    cv.line(px + 6, py - 2, px + 18, py + 8, INK, 1)
    cv.circle(px + 24, py + 10, 3, INK)
    # sledge player 2 (blue), chasing from the left
    qx, qy = x + 56, y + 28
    cv.fill_rect(qx - 10, qy + 2, 20, 4, (120, 120, 126))
    cv.fill_rect(qx - 6, qy - 6, 12, 9, BLUE)
    cv.circle(qx - 2, qy - 10, 4, (40, 40, 48))
    cv.line(qx + 6, qy - 2, qx + 16, qy + 6, INK, 1)
    # red chip behind 10-0 (white text, top-right)
    tw = text_width("10-0", 9, True)
    cv.fill_rect(x + w - 7 - tw - 8, y + 3, tw + 12, 15, (120, 20, 20))
    cv.fill_rect(x + w - 8 - tw - 8, y + 2, tw + 12, 15, RED)
    rect_outline(cv, x + w - 8 - tw - 8, y + 2, tw + 12, 15, WHITE, 1)
    cv.text(x + w - 8, y + 12, "10-0", 9, True, WHITE, align="right")


SCENES = {"chart": scene_chart, "rocket": scene_rocket,
          "tanker": scene_tanker, "cpi": scene_cpi,
          "garment": scene_garment, "treaty": scene_treaty,
          "store": scene_store, "tariffs": scene_tariffs,
          "pyongyang": scene_pyongyang, "court": scene_court,
          "mine": scene_mine, "blast": scene_blast,
          "births": scene_births, "macaw": scene_macaw,
          "dragonfly": scene_dragonfly, "iwo": scene_iwo,
          "hockey": scene_hockey}

# (ALSO index, tile label, scene key, story number) — 4 also-list items
# promoted to drawn tiles in the IN BRIEF zone.
ALSO_TILES = [
    (8, "SPIX'S MACAW CHICK HOPE HATCHES", "macaw", 22),
    (10, "DRAGONFLY TITAN PARTS ARRIVE", "dragonfly", 24),
    (18, "IWO JIMA ERUPTION ADDS NEW LAND", "iwo", 32),
    (20, "CANADA WIN PARA HOCKEY 10-0", "hockey", 34),
]

# ---------------------------------------------------------------- layout
def _fit_size(s, sizes, bold, max_w):
    for sz in sizes:
        if text_width(s, sz, bold) <= max_w:
            return sz
    return sizes[-1]


def draw_topstrip(cv):
    cv.fill_rect(0, 0, W, 24, INK)
    cv.text(20, 16, "THE WORLD IN ONE DAY", 10, True, WHITE)
    cv.text(W - 20, 16, "35 STORIES \u00b7 ALL FROM WEDNESDAY 25 NOVEMBER 2026",
            10, True, WHITE, align="right")


def draw_masthead(cv):
    s = "Wednesday 25 November 2026"
    sz = _fit_size(s, [78, 74, 70, 66, 62, 58], True, 992)
    cv.text(512, 98, s, sz, True, INK, align="center")
    cv.fill_rect(M, 106, CW, 2, INK)


def draw_subhead(cv):
    parts = ["Pakistan's first astronaut flies to Tiangong",
             "Asia's chip stocks crash", "Tankers burn in Hormuz"]
    for sz in (16, 15, 14, 13):
        widths = [text_width(p, sz, False) for p in parts]
        total = sum(widths) + 2 * 16
        if total <= 992:
            break
    x = 512 - total / 2
    for i, p in enumerate(parts):
        cv.text(x, 128, p, sz, False, INK)
        x += widths[i]
        if i < 2:
            cx, cy = x + 8, 123
            cv.fill_poly([(cx, cy - 4), (cx + 4, cy), (cx, cy + 4),
                          (cx - 4, cy)], RED)
            x += 16


def draw_region(cv):
    total = sum(c for _, c, _ in REGIONS)
    widths = [c / total * CW for _, c, _ in REGIONS]
    # minimum segment width 64px; take the slack from the largest segment
    for i, w in enumerate(widths):
        if w < 64:
            widths[REGIONS.index(max(REGIONS, key=lambda r: r[1]))] -= (64 - w)
            widths[i] = 64
    x = M
    for (label, count, col), w in zip(REGIONS, widths):
        cv.fill_rect(x, 136, w, 22, col)
        cv.text(x + w / 2, 151, "%s %d" % (label, count), 9, True, WHITE,
                align="center")
        x += w


def draw_timeline(cv):
    cv.fill_rect(M, 162, 84, 20, NAVY)
    cv.text(M + 42, 176, "THE DAY IN UTC", 9, True, WHITE, align="center")
    # one group, fixed gaps: even rhythm, symmetric insets (was per-cell
    # centring: insets 28/22, gaps 44-65; v2.5 gap 54, insets 31/32)
    widths = [text_width(t, 9.5, True) + text_width(" ", 9.5, True)
              + text_width(label, 8.5, False) for (t, label) in TIMELINE]
    gap = 50
    total = sum(widths) + gap * (len(TIMELINE) - 1)
    x = M + 84 + ((CW - 84) - total) / 2
    for i, (t, label) in enumerate(TIMELINE):
        cv.text(x, 176, t, 9.5, True, RED)
        cv.text(x + text_width(t + " ", 9.5, True), 176, label, 8.5, False,
                INK)
        x += widths[i] + gap


def draw_stats(cv):
    cell = CW / 6
    for i, (num, cap, sub) in enumerate(STATS):
        x = M + i * cell
        if i:
            cv.fill_rect(x, 190, 1, 54, RULE)
        sz = _fit_size(num, [40, 36, 32, 28], True, cell - 10)
        cv.text(x + cell / 2, 218, num, sz, True, RED, align="center")
        cv.text(x + cell / 2, 228, cap, 9.5, True, INK, align="center")
        cv.text(x + cell / 2, 238, sub, 8.5, False, INK_SOFT, align="center")


SOURCES = ["(AP, Reuters, Yonhap)", "(Reuters, Xinhua, BBC)",
           "(Mehr News, Al Jazeera)"]


def draw_heroes(cv):
    cols = [M, M + 332, M + 664]
    scene_fns = [scene_chart, scene_rocket, scene_tanker]
    for j, (head, deck, p, kick) in enumerate(LEADS):
        x = cols[j]
        # number badge on the scene, top-left
        scene_fns[j](cv, x, 243, 318, 115)
        num_badge(cv, x + 12, 255, j + 1, 9)
        cv.text(x, 369, kick, 9, True, RED)
        pill_right(cv, x + 318, 359, p, 8)
        lines = wrap_text(head, 22, True, 318)
        for k, ln in enumerate(lines):
            cv.text(x, 390 + k * 24, ln, 22, True, INK)
        dlines = wrap_text(deck, 11, False, 318)
        for k, ln in enumerate(dlines):
            cv.text(x, 427 + k * 12, ln, 11, False, DECK_GREY)
        cv.text(x, 452, SOURCES[j], 9, False, INK_SOFT)


def draw_small(cv):
    for i, (head, deck, p, kick, key) in enumerate(SMALL):
        row, col = divmod(i, 5)
        x = M + col * 196
        y = 460 + row * 164
        SCENES[key](cv, x, y, 186, 65)
        num_badge(cv, x + 12, y + 12, i + 4, 9)
        cv.text(x, y + 74, kick, 9, True, RED)
        lines = wrap_text(head, 15, True, 186)
        for k, ln in enumerate(lines):
            cv.text(x, y + 87 + k * 14, ln, 15, True, INK)
        dlines = wrap_text(deck, 10.5, False, 186)
        for k, ln in enumerate(dlines):
            cv.text(x, y + 113 + k * 11, ln, 10.5, False, DECK_GREY)
        pill(cv, x, y + 146, p, 8)


def _project(lon, lat):
    # map box x 14..336, y 797..919
    x = 14 + (lon + 170) / 360 * 322
    y = 797 + (85 - lat) / 145 * 122
    return x, y


# East-coast bulge (Japan/Taiwan) + Indonesia, so every pin sits on land.
CONTINENTS[3] = ([(-10, 36), (-9, 43), (0, 44), (10, 44), (20, 40), (26, 38),
                  (30, 36), (36, 36), (40, 38), (45, 40), (50, 45), (55, 50),
                  (60, 55), (65, 60), (70, 70), (80, 73), (90, 75), (100, 77),
                  (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
                  (160, 66), (170, 66), (178, 65), (170, 60), (162, 58),
                  (158, 52), (150, 60), (142, 55), (141, 46), (140, 42),
                  (141, 38), (140, 35), (136, 33), (130, 33), (126, 31), (122, 28),
                  (122, 25), (118, 22), (112, 21), (110, 20), (108, 15),
                  (105, 10), (100, 8), (98, 12), (95, 16), (92, 21),
                  (90, 22), (85, 20), (80, 15), (77, 8), (75, 12),
                  (72, 20), (68, 23), (65, 25), (60, 25), (58, 26),
                  (54, 27), (50, 29), (48, 30), (44, 29), (40, 31),
                  (36, 36), (33, 36), (30, 36), (26, 38), (22, 37), (18, 40),
                  (15, 38), (12, 42), (8, 44), (3, 43), (-2, 37), (-6, 36),
                  (-9, 38)])
CONTINENTS.append(
    [(95, 5), (100, 0), (105, -5), (110, -7), (114, -8), (120, -10),
     (125, -8), (130, -4), (135, -2), (140, -4), (136, -8), (130, -9),
     (124, -10), (118, -9), (112, -8), (106, -8), (100, -6), (96, 0)])


def draw_map(cv):
    cv.text(M, 795, "WHERE IT HAPPENED \u00b7 PINS = STORY NUMBERS", 10, True,
            TEAL)
    cv.fill_rect(M, 797, 322, 122, SEA_MAP)
    rect_outline(cv, M, 797, 322, 122, RULE, 1)
    for cont in CONTINENTS:
        pts = [_project(lon, lat) for (lon, lat) in cont]
        cv.fill_poly(pts, LAND)
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            cv.line(ax, ay, bx, by, LAND_LINE, 1)
    label_dx = {"Hormuz": (-8, -9, "right"), "Canberra": (-24, 12, "right"),
                "Cartagena": (-6, 12, "right"), "Washington": (8, -9, "left"),
                "Iowa": (-8, -9, "right")}
    # East Asia pins cluster within ~35px, and Canberra/Sydney are 2px
    # apart: true dots on land + offset numbered badges joined by leader
    # lines (atlas style).
    cluster_dx = {"Tokyo": (9, -8), "Seoul": (-8, -8), "Taipei": (-7, 10),
                  "Jiuquan": (-12, -4), "Pyongyang": (7, 9),
                  "Canberra": (-14, 6), "Sydney": (10, -6)}
    for (name, lat, lon, num, labelled) in PINS:
        x, y = _project(lon, lat)
        if name in cluster_dx:
            dx, dy = cluster_dx[name]
            cv.line(x, y, x + dx, y + dy, LAND_LINE, 1)
            cv.circle(x, y, 3, RED)
            num_badge(cv, x + dx, y + dy, num, 6)
        else:
            num_badge(cv, x, y, num, 7)
        if name in label_dx:
            dx, dy, al = label_dx[name]
            cv.text(x + dx, y + dy, name.upper(), 8, True, TEAL, align=al)
    cv.text(M, 935, "Seoul also story 13 \u00b7 Canberra also story 6",
            8, False, INK_SOFT)


def draw_brief(cv):
    cv.text(346, 795, "IN BRIEF \u00b7 22 MORE FROM 25 NOVEMBER", 10, True,
            TEAL)
    # 18 remaining one-liners: 3 columns x 6 rows (was 2 x 11), freeing
    # the strip below for 4 drawn tiles. Numbers keep ALSO order.
    tiled = {idx for (idx, _, _, _) in ALSO_TILES}
    rest = [(14 + i, item) for i, item in enumerate(ALSO)
            if i not in tiled]
    for j, (num, item) in enumerate(rest):
        col, row = divmod(j, 6)
        x = 346 + col * 221
        y = 810 + row * 11.5
        cv.text(x, y, "%d %s" % (num, item), 10, True, INK)
    # 4 drawn tiles in a row: scene + number badge + label below.
    # Strip y 876..940; HOW SURE legend at 949 (v2.9-fix).
    for t, (idx, label, key, num) in enumerate(ALSO_TILES):
        x = 346 + t * 166
        SCENES[key](cv, x, 876, 162, 44)
        rect_outline(cv, x, 876, 162, 44, RULE, 1)
        num_badge(cv, x + 12, 888, num, 9)
        sz = _fit_size(label, [8.5, 8, 7.5], True, 162)
        cv.text(x, 934, label, sz, True, INK)


def draw_legend(cv):
    # v2.9-fix: whole row up 1px (pills 949, text 959) — buys 1px for the
    # legend->DATE CHECK gap without touching tiles (caption gap stays ~15px)
    # or the map note (still 12px below it). Pill height NOT trimmed: the
    # expl-text descenders reach the same row as the pill fill, so trimming
    # the fill alone would not move the measured legend bottom.
    x = M
    cv.text(x, 959, "HOW SURE \u2014 ", 9, True, INK)
    x += text_width("HOW SURE \u2014 ", 9, True)
    parts = [("OFFICIAL", "govt/company statement"),
             ("CONFIRMED", "2+ major outlets"),
             ("REPORTED", "one outlet"),
             ("CLAIM", "one side, unverified"),
             ("ONGOING", "still unfolding"),
             ("SCHEDULED", "due")]
    for j, (label, expl) in enumerate(parts):
        w = pill(cv, x, 949, label, 8)
        x += w + 4
        cv.text(x, 959, expl, 8.5, False, INK_SOFT)
        x += text_width(expl, 8.5, False)
        if j < len(parts) - 1:
            cv.text(x, 959, " \u00b7 ", 8.5, False, INK_SOFT)
            x += text_width(" \u00b7 ", 8.5, False)


def draw_datecheck(cv):
    # v2.9-fix: box 46 -> 44 tall (966..1009) + prose pitch 10.5 -> 10
    # + header/prose up 1px. Frees 2px for the DATE CHECK->footer gap
    # (now 4px) while the interior keeps 1px clearance top and bottom
    # (header ink 969, last prose ink ~1006, borders 966-967 / 1008-1009).
    rect_outline(cv, M, 966, CW, 44, RED, 2)
    cv.text(26, 976, "DATE CHECK \u2014 LEFT OUT AS EARLIER NEWS. "
            "THESE ARE NOT TODAY'S.", 10, True, RED)
    cv.text(998, 976, "+35 MORE CHECKED", 10, True, RED, align="right")
    # same 12 items, same wording, reflowed as flowing prose (3 lines)
    prose = " \u00b7 ".join(DATECHECK)
    lines = wrap_text(prose, 9.5, False, 972)
    for k, ln in enumerate(lines):
        cv.text(26, 985 + k * 10, ln, 9.5, False, INK)


def draw_footer(cv):
    cv.text(512, 1020,
            "Sources: AP \u00b7 Reuters \u00b7 BBC \u00b7 Al Jazeera \u00b7 Yonhap "
            "\u00b7 ABS \u00b7 Mehr \u00b7 One Turn \u2014 All stories first reported "
            "or developing Wed 25 Nov 2026 unless dated in DATE CHECK \u00b7 "
            "Drawn in code, no photos",
            9, False, INK, align="center")


def build():
    cv = Canvas(W, H, PAPER)
    draw_topstrip(cv)
    draw_masthead(cv)
    draw_subhead(cv)
    draw_region(cv)
    draw_timeline(cv)
    draw_stats(cv)
    draw_heroes(cv)
    draw_small(cv)
    draw_map(cv)
    draw_brief(cv)
    draw_legend(cv)
    draw_datecheck(cv)
    draw_footer(cv)
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    cv = build()
    path = os.path.join(out, "entry.png")
    n = write_png(cv, path)
    print("wrote %s %d bytes" % (path, n))


if __name__ == "__main__":
    main()
