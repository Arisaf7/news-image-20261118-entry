#!/usr/bin/env python3
"""news-image-20261118 entry.

Draws a one-day world-news summary graphic for Wednesday, 18 November
2026 and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Pure standard library: the bitmap font and the PNG encoder (zlib + CRC)
are written here from scratch. No network, no randomness, no time:
two runs produce identical bytes.
"""

import binascii
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 234)
INK = (22, 30, 40)
NAVY = (16, 42, 67)
RED = (178, 34, 34)
TEAL = (14, 116, 110)
GOLD = (176, 132, 30)
GREY = (120, 112, 98)
LINE = (203, 195, 180)
SKY = (178, 214, 232)
SEA = (28, 84, 128)
WHITE = (255, 255, 255)
ORANGE = (232, 122, 32)
YELLOW = (244, 196, 66)

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 bits written as strings; "1" is an inked pixel.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

CHAR_W = 5
CHAR_H = 7


def text_width(text, scale):
    """Pixel width of text at the given scale (1px tracking)."""
    return len(text) * (CHAR_W * scale + scale) - scale


def draw_text(px, x, y, text, scale, color):
    """Draw uppercase text; unknown chars fall back to a blank."""
    cx = x
    step = CHAR_W * scale + scale
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(CHAR_H):
            bits = glyph[row]
            for col in range(CHAR_W):
                if bits[col] == "1":
                    fill_rect(px, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += step


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ------------------------------------------------------------- canvas -----
def new_canvas():
    return bytearray(PAPER * WIDTH * HEIGHT)


def set_px(px, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def fill_rect(px, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    for yy in range(y0, y1):
        base = (yy * WIDTH + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def draw_hline(px, x, y, w, color):
    fill_rect(px, x, y, w, 1, color)


def draw_vline(px, x, y, h, color):
    fill_rect(px, x, y, 1, h, color)


def draw_line(px, x0, y0, x1, y1, color):
    """Bresenham line, 1px wide."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(px, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(px, xx, yy, color)


def draw_star(px, cx, cy, r, color):
    """Eight-point starburst (explosion) made of triangles of lines."""
    for ang in range(0, 360, 45):
        import math
        rad = math.radians(ang)
        x1 = int(cx + r * math.cos(rad))
        y1 = int(cy + r * math.sin(rad))
        draw_line(px, cx, cy, x1, y1, color)
    fill_circle(px, cx, cy, r // 3, color)


# -------------------------------------------------------------- png ------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(px):
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)  # filter: none
        raw += px[y * WIDTH * 3:(y + 1) * WIDTH * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------ artwork ----
def draw_tanker_scene(px, x, y, w, h):
    """Small scene: sky, sea, a tanker with a blast above its funnel."""
    fill_rect(px, x, y, w, h, SKY)
    # sun
    fill_circle(px, x + 46, y + 34, 20, YELLOW)
    # sea
    sea_y = y + h - 62
    fill_rect(px, x, sea_y, w, 62, SEA)
    # wave lines
    for k, wy in enumerate((sea_y + 14, sea_y + 30, sea_y + 46)):
        for wx in range(x + 8 + (k % 2) * 22, x + w - 8, 44):
            draw_hline(px, wx, wy, 22, (120, 180, 210))
    # hull
    hull_y = sea_y - 26
    fill_rect(px, x + 34, hull_y, w - 68, 26, INK)
    fill_rect(px, x + 34, hull_y + 20, w - 68, 6, RED)
    # deck + superstructure
    fill_rect(px, x + w - 108, hull_y - 30, 62, 30, WHITE)
    fill_rect(px, x + w - 108, hull_y - 30, 62, 4, RED)
    fill_rect(px, x + w - 96, hull_y - 44, 16, 14, INK)  # funnel
    # containers
    for i, col in enumerate((RED, TEAL, GOLD, RED)):
        fill_rect(px, x + 52 + i * 52, hull_y - 22, 46, 22, col)
    # explosion above the funnel
    ex, ey = x + w - 88, hull_y - 78
    draw_star(px, ex, ey, 30, ORANGE)
    draw_star(px, ex, ey, 18, YELLOW)
    fill_circle(px, ex, ey, 7, RED)


def story_block(px, x, y, w, tag, tag_color, headline, body, icon):
    fill_rect(px, x, y, w, 3, tag_color)
    draw_text(px, x + 2, y + 14, tag, 2, tag_color)
    lines = wrap_text(headline, 3, w - 84)
    ty = y + 44
    for ln in lines[:2]:
        draw_text(px, x + 2, ty, ln, 3, INK)
        ty += 34
    body_lines = wrap_text(body, 2, w - 4)
    by = ty + 6
    for ln in body_lines[:4]:
        draw_text(px, x + 2, by, ln, 2, (52, 60, 72))
        by += 20
    icon(px, x + w - 66, y + 14)


def icon_bridge(px, x, y):
    # bridge deck + two towers + cables
    draw_hline(px, x, y + 26, 56, INK)
    draw_vline(px, x + 8, y, 26, INK)
    draw_vline(px, x + 46, y, 26, INK)
    draw_line(px, x + 8, y, x + 28, y + 26, INK)
    draw_line(px, x + 46, y, x + 28, y + 26, INK)


def icon_shelter(px, x, y):
    # tent / shelter triangle + snow dots
    draw_line(px, x + 4, y + 30, x + 28, y + 2, INK)
    draw_line(px, x + 52, y + 30, x + 28, y + 2, INK)
    draw_hline(px, x + 4, y + 30, 48, INK)
    fill_circle(px, x + 12, y + 8, 2, TEAL)
    fill_circle(px, x + 46, y + 12, 2, TEAL)
    fill_circle(px, x + 28, y + 20, 2, TEAL)


def icon_leaf(px, x, y):
    # globe: circle + latitude lines + leaf
    fill_circle(px, x + 22, y + 16, 15, TEAL)
    draw_hline(px, x + 8, y + 16, 28, WHITE)
    draw_vline(px, x + 22, y + 2, 28, WHITE)
    draw_line(px, x + 40, y + 26, x + 52, y + 12, (34, 120, 60))
    fill_circle(px, x + 50, y + 10, 5, (34, 120, 60))


def icon_columns(px, x, y):
    # parliament: pediment + three columns
    draw_line(px, x + 4, y + 12, x + 28, y, INK)
    draw_line(px, x + 52, y + 12, x + 28, y, INK)
    draw_hline(px, x + 4, y + 12, 48, INK)
    for cx in (8, 24, 40):
        draw_vline(px, x + cx, y + 14, 16, INK)
    draw_hline(px, x + 4, y + 30, 48, INK)


# -------------------------------------------------------------- build ----
def build():
    px = new_canvas()

    # masthead
    fill_rect(px, 0, 0, WIDTH, 118, NAVY)
    title = "THE WORLD IN ONE DAY"
    draw_text(px, (WIDTH - text_width(title, 5)) // 2, 24, title, 5, WHITE)
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    draw_text(px, (WIDTH - text_width(date, 2)) // 2, 78, date, 2, GOLD)
    fill_rect(px, 0, 118, WIDTH, 6, RED)

    # lead story
    draw_text(px, 48, 146, "LEAD STORY - MIDDLE EAST", 2, RED)
    headline = "U.S. SINKS FIVE IRANIAN TANKERS AS GULF WAR ESCALATES"
    hl = wrap_text(headline, 4, WIDTH - 96)
    hy = 178
    for ln in hl:
        draw_text(px, 48, hy, ln, 4, INK)
        hy += 40
    body = (
        "U.S. CENTRAL COMMAND SAID IT DESTROYED FIVE IRANIAN OIL TANKERS "
        "IN THE GULF OF OMAN AND NEAR KHARG ISLAND AFTER IRAN'S "
        "REVOLUTIONARY GUARD TWICE TRIED TO HIT A U.S. WARSHIP WITH "
        "BALLISTIC MISSILES. IRAN HIT BACK AT TEN SHIPS NEAR THE STRAIT "
        "OF HORMUZ AND FIRED MISSILES AT U.S. FORCES AT AL-AZRAQ BASE IN "
        "JORDAN. BRENT CRUDE ROSE ABOVE $100 A BARREL."
    )
    bl = wrap_text(body, 2, 596)
    by = hy + 12
    for ln in bl:
        draw_text(px, 48, by, ln, 2, (52, 60, 72))
        by += 20
    draw_tanker_scene(px, 680, hy + 8, 296, 172)

    # divider
    draw_hline(px, 48, 456, WIDTH - 96, LINE)

    # four story blocks, 2 x 2
    bw = 456
    story_block(
        px, 48, 472, bw, "UKRAINE", NAVY,
        "KERCH BRIDGE HIT FOR SECOND NIGHT",
        "UKRAINE STRUCK THE BRIDGE TO OCCUPIED CRIMEA AGAIN AS RUSSIA "
        "HIT BRIDGES OF ITS OWN. TRUMP, PUTIN AND XI MEET IN SHENZHEN "
        "ON THURSDAY.",
        icon_bridge,
    )
    story_block(
        px, 520, 472, bw, "GAZA", RED,
        "UN WARNS OF WINTER DEATHS IN GAZA",
        "MORE THAN 1.7 MILLION PEOPLE REMAIN DISPLACED AND 1.4 MILLION "
        "FACE ACUTE HUNGER. AUSTRALIA, CANADA, ITALY AND BRITAIN URGE "
        "ISRAEL TO LET AID IN.",
        icon_shelter,
    )
    story_block(
        px, 48, 682, bw, "CLIMATE - COP31", TEAL,
        "COP31 ENTERS DECISIVE PHASE",
        "NEGOTIATORS IN ANTALYA WORK THROUGH A DRAFT DEAL WITH 144 "
        "DISPUTED ITEMS AS THE SUMMIT NEARS ITS SCHEDULED END ON "
        "FRIDAY.",
        icon_leaf,
    )
    story_block(
        px, 520, 682, bw, "ISRAEL", GOLD,
        "EISENKOT TAPPED TO FORM GOVERNMENT",
        "PRESIDENT HERZOG ASKED EX-ARMY CHIEF GADI EISENKOT TO TRY TO "
        "BUILD A COALITION, PASSING OVER CARETAKER PM NETANYAHU.",
        icon_columns,
    )

    # also-today strip
    fill_rect(px, 0, 884, WIDTH, 2, LINE)
    draw_text(px, 48, 898, "ALSO TODAY", 2, RED)
    also = (
        "QUAD LEADERS MEET IN MANILA - RUSSIAN AN-12 CRASH KILLS 19 IN "
        "KEMEROVO - ROBERT PATTINSON NAMED THE NEW JAMES BOND"
    )
    al = wrap_text(also, 2, WIDTH - 96)
    ay = 922
    for ln in al:
        draw_text(px, 48, ay, ln, 2, INK)
        ay += 20

    # footer
    fill_rect(px, 0, 976, WIDTH, 2, LINE)
    footer = "SOURCES: AL JAZEERA, AP, REUTERS, CENTCOM, UNITED NATIONS"
    draw_text(px, (WIDTH - text_width(footer, 2)) // 2, 986, footer, 2,
              GREY)
    return encode_png(px)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = build()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
