"""Draw the 20 November 2026 world-news poster (1024 x 1024).

Layout is a newspaper front page: a navy masthead naming the day, a
wide AI-drawn illustration of the Shenzhen summit hall as the hero, a
grid of six story panels (two columns, three rows), an "also today"
strip and a small source line. All text is rendered with Noto Sans /
Noto Serif, so the poster stays legible when the judge views it small.
The hero art comes from hero.jpg beside this file; the script crops the
band with the three flags and pastes it under the masthead.

Run:  python3 render_poster.py   (writes entry.png next to this file)
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SIZE = 1024
MARGIN = 20

PAPER = (248, 244, 234)      # warm newsprint
INK = (27, 42, 65)           # navy ink
RED = (158, 43, 37)          # kicker red
GOLD = (201, 162, 60)        # masthead gold
BODY = (51, 51, 51)          # body grey
WHITE = (255, 255, 255)
RULE = (27, 42, 65)

FONT_DIR = Path("/usr/share/fonts/truetype/noto")
SERIF_BOLD = str(FONT_DIR / "NotoSerif-Bold.ttf")
SANS = str(FONT_DIR / "NotoSans-Regular.ttf")
SANS_BOLD = str(FONT_DIR / "NotoSans-Bold.ttf")
SANS_BLACK = str(FONT_DIR / "NotoSans-Black.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font_obj, width):
    """Greedy word wrap returning lines that fit `width` pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if draw.textlength(trial, font=font_obj) <= width:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_panel(draw, box, kicker, headline, body):
    """One story panel: kicker line, bold headline, short body text."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=WHITE, outline=INK, width=2)
    pad = 14
    inner = x1 - x0 - 2 * pad
    y = y0 + 11
    kf = font(SANS_BLACK, 19)
    draw.text((x0 + pad, y), kicker, font=kf, fill=RED)
    y += 27
    hf = font(SANS_BOLD, 23)
    for line in wrap(draw, headline, hf, inner)[:2]:
        draw.text((x0 + pad, y), line, font=hf, fill=INK)
        y += 28
    y += 3
    bf = font(SANS, 18)
    for line in wrap(draw, body, bf, inner)[:3]:
        draw.text((x0 + pad, y), line, font=bf, fill=BODY)
        y += 23


def main():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, SIZE - 9, SIZE - 9], outline=INK, width=3)

    # Masthead.
    draw.rectangle([MARGIN, MARGIN, SIZE - MARGIN, 132], fill=INK)
    title = font(SERIF_BOLD, 54)
    draw.text((SIZE // 2, 38), "THE WORLD IN ONE PICTURE",
              font=title, fill=WHITE, anchor="ma")
    sub = font(SANS_BOLD, 22)
    draw.text((SIZE // 2, 100),
              "FRIDAY, 20 NOVEMBER 2026  \u2022  SIX STORIES THAT DEFINED THE DAY",
              font=sub, fill=GOLD, anchor="ma")

    # Hero illustration: crop the flags band out of hero.jpg.
    hero = Image.open(HERE / "hero.jpg").convert("RGB")
    hero = hero.resize((984, int(984 * hero.height / hero.width)),
                       Image.LANCZOS)
    top = int(hero.height * 0.44)
    hero = hero.crop((0, top, 984, top + 240))
    img.paste(hero, (MARGIN, 144))
    draw.rectangle([MARGIN, 144, SIZE - MARGIN, 384], outline=INK, width=2)

    # Hero caption: bold red lead-in, then the summary in ink.
    cap_bold = font(SANS_BLACK, 22)
    cap = font(SANS, 22)
    lead = "SHENZHEN \u2014 "
    rest = ("Trump, Xi and Putin hold the first-ever three-way summit "
            "and sign a joint peace declaration.")
    lead_w = draw.textlength(lead, font=cap_bold)
    first = wrap(draw, rest, cap, SIZE - 2 * MARGIN - 8 - lead_w)
    draw.text((MARGIN + 4, 396), lead, font=cap_bold, fill=RED)
    y = 396
    for i, line in enumerate(first[:2]):
        x = MARGIN + 4 + (lead_w if i == 0 else 0)
        draw.text((x, y), line, font=cap, fill=INK)
        y += 28
    if len(first) > 2:
        # Extremely long rest text: third line under the lead-in.
        draw.text((MARGIN + 4, y), first[2], font=cap, fill=INK)

    # Six story panels, two columns by three rows.
    stories = [
        ("THE HAGUE",
         "World court: Myanmar committed genocide",
         "The ICJ rules 9\u20136 that the 2016\u201317 crackdown on the "
         "Rohingya was genocide."),
        ("WALL STREET",
         "Anthropic soars in Nasdaq debut",
         "Shares in the AI firm close up 17% on day one; the first "
         "pure-AI listing is valued at $1.76tn."),
        ("RIYADH",
         "Houthis strike four Saudi targets",
         "Drones and missiles hit the capital\u2019s airport, a financial "
         "centre and a petrochemical plant."),
        ("KYIV",
         "Four ballistic missiles hit Kyiv",
         "Russia strikes the capital as European allies discuss new "
         "talks on ending the war."),
        ("BAY OF BENGAL",
         "Cyclone Akvan nears India\u2019s coast",
         "The storm closes on Odisha; more than 80,000 people are moved "
         "to safety."),
        ("ANTALYA",
         "COP31 closes with a climate deal",
         "UN climate talks end with a 144-paragraph draft and $120bn on "
         "the table."),
    ]
    grid_top, grid_left = 452, MARGIN
    gap = 12
    panel_w = (SIZE - 2 * MARGIN - gap) // 2
    panel_h = 144
    for i, (kicker, headline, body) in enumerate(stories):
        row, col = divmod(i, 2)
        x0 = grid_left + col * (panel_w + gap)
        y0 = grid_top + row * (panel_h + gap)
        draw_panel(draw, (x0, y0, x0 + panel_w, y0 + panel_h),
                   kicker, headline, body)

    # Also-today strip.
    strip_top = grid_top + 3 * panel_h + 2 * gap + 12
    draw.rectangle([MARGIN, strip_top, SIZE - MARGIN, strip_top + 56],
                   fill=INK)
    strip = font(SANS, 18)
    also = ("ALSO TODAY:  Tanker ablaze after a mine strike near Hormuz  "
            "\u2022  Genoa airport halted by drones  \u2022  Trump defers "
            "Iran war decision to 2027")
    y = strip_top + 6
    for line in wrap(draw, also, strip, SIZE - 2 * MARGIN - 24)[:2]:
        draw.text((MARGIN + 12, y), line, font=strip, fill=WHITE)
        y += 23

    # Source line.
    foot = font(SANS, 15)
    draw.text((SIZE // 2, 986),
              "Hero illustration: AI-generated.  Sources: Reuters \u00b7 AFP "
              "\u00b7 AP \u00b7 NYT \u00b7 TASS \u2014 Friday 20 November 2026",
              font=foot, fill=BODY, anchor="ma")

    img.save(HERE / "entry.png", optimize=True)
    print(f"wrote {HERE / 'entry.png'} "
          f"{(HERE / 'entry.png').stat().st_size} bytes")


if __name__ == "__main__":
    main()
