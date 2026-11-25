#!/usr/bin/env python3
"""Draw a one-image summary of the world news of 25 November 2026.

Running ``python3 main.py`` regenerates ``news-2026-11-25.png``
deterministically: no network access, no randomness, system DejaVu fonts.

The stories were compiled from wire reporting dated 25 November 2026
(see README.md for the full source list for every panel).
"""

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 1600, 1200
MARGIN = 48

BG = (10, 14, 22)            # near-black navy
PANEL_BG = (20, 27, 40)      # card background
PANEL_EDGE = (43, 54, 74)    # card border
INK = (238, 242, 247)        # headline white
BODY = (178, 190, 205)       # summary grey-blue
MUTED = (120, 134, 152)      # footer / kicker grey
GOLD = (240, 193, 75)        # header accent

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_SANS = f"{FONT_DIR}/DejaVuSans.ttf"
F_BOLD = f"{FONT_DIR}/DejaVuSans-Bold.ttf"

# --------------------------------------------------------------------------
# The day's stories: (category, accent colour, headline, summary, source tag)
# --------------------------------------------------------------------------
FEATURED = (
    "CLIMATE — TOP STORY",
    (74, 222, 128),
    "COP31 climate talks collapse with no deal in Antalya",
    "The UN summit in Turkey ended without an agreement — the first COP failure since "
    "Copenhagen in 2009 — after oil and gas producers blocked any mention of fossil "
    "fuels and the EU refused to sign.",
    "Reuters · CNN · BD Global Times",
)

STORIES = [
    (
        "WAR",
        (248, 113, 113),
        "Ukraine sinks Russian warship off Libya",
        "Kyiv's long-range drones hit a warship off Benghazi and a cargo ship in the "
        "Gulf of Finland; Moscow accused Ukraine of \"terrorism\".",
        "Reuters · BD Global Times",
    ),
    (
        "TRADE",
        (251, 191, 36),
        "US readies sweeping new tariffs",
        "Washington is set to release probe findings on \"excess capacity\" at 16 "
        "trading partners, including China and the EU, paving the way for fresh duties.",
        "Reuters · DW",
    ),
    (
        "MIDDLE EAST",
        (251, 146, 60),
        "Houthi drone strike injures 11 in Riyadh",
        "A drone hit a tower in the Saudi capital, injuring 11 people including two "
        "Indian nationals, in a rare attack on the kingdom's heartland.",
        "Reuters · The Hindu",
    ),
    (
        "SPACE",
        (56, 189, 248),
        "First foreign astronaut flies to Tiangong",
        "China's Shenzhou-24 launched from Jiuquan carrying Pakistan's Muhammad "
        "Zeeshan Ali — the first Pakistani in orbit — to the Tiangong station.",
        "Reuters · Xinhua",
    ),
    (
        "INDONESIA",
        (244, 114, 182),
        "Race to reach miners trapped in Bogor",
        "Rescuers searched for some 26 workers trapped 100 m down in an "
        "unauthorised gold mine in West Java, inundated by heavy rain since Monday.",
        "Reuters · ANTARA",
    ),
    (
        "MARKETS",
        (167, 139, 250),
        "AI rally fizzles as tariff fears bite",
        "Asian stocks tumbled — MSCI Asia-Pacific fell 2.3% and Seoul 5.3% — while "
        "Nvidia slid about 6% as the bounce from Jensen Huang's return faded.",
        "Reuters",
    ),
]

FOOTER = ("Sources: Reuters · CNN · Xinhua · ANTARA · The Hindu · DW · BD Global Times"
          "   |   Compiled from reporting dated 25 November 2026")


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------
def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap measured with PIL so nothing overflows its panel."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, xy, lines, fnt, fill, leading):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_body(draw, text, max_width, start_y, max_bottom, sizes=(22, 21, 20, 19)):
    """Wrap ``text`` at the largest size whose lines end above ``max_bottom``.

    Returns (lines, font, leading, end_y). This is the overflow guard: a
    panel can never spill into the source tag pinned at its bottom edge.
    """
    for size in sizes:
        fnt = font(F_SANS, size)
        leading = size + 8
        lines = wrap(draw, text, fnt, max_width)
        end_y = start_y + leading * len(lines)
        if end_y <= max_bottom:
            return lines, fnt, leading, end_y
    raise ValueError("summary does not fit its panel at any size")


# --------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------
def panel(draw, box, accent, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=PANEL_BG, outline=PANEL_EDGE, width=2)
    x0, y0, x1, _ = box
    # accent bar along the top edge of the card
    draw.rounded_rectangle([x0, y0, x1, y0 + 10], radius=radius, fill=accent)
    draw.rectangle([x0, y0 + 5, x1, y0 + 10], fill=accent)


def story_card(draw, box, category, accent, headline, summary, source):
    panel(draw, box, accent)
    x0, y0, x1, y1 = box
    pad = 26
    inner_w = (x1 - x0) - 2 * pad
    source_y = y1 - 40
    y = y0 + 30
    draw.text((x0 + pad, y), category, font=font(F_BOLD, 21), fill=accent)
    y += 36
    head_lines = wrap(draw, headline, font(F_BOLD, 31), inner_w)
    y = draw_lines(draw, (x0 + pad, y), head_lines, font(F_BOLD, 31), INK, 40)
    y += 8
    lines, fnt, leading, _ = fit_body(draw, summary, inner_w, y, source_y - 12)
    draw_lines(draw, (x0 + pad, y), lines, fnt, BODY, leading)
    draw.text((x0 + pad, source_y), source.upper(), font=font(F_BOLD, 16), fill=MUTED)


def featured_card(draw, box, category, accent, headline, summary, source):
    panel(draw, box, accent)
    x0, y0, x1, y1 = box
    pad = 34
    inner_w = (x1 - x0) - 2 * pad
    source_y = y1 - 44
    y = y0 + 30
    draw.text((x0 + pad, y), category, font=font(F_BOLD, 24), fill=accent)
    y += 40
    head_lines = wrap(draw, headline, font(F_BOLD, 46), inner_w)
    y = draw_lines(draw, (x0 + pad, y), head_lines, font(F_BOLD, 46), INK, 56)
    y += 8
    lines, fnt, leading, _ = fit_body(draw, summary, inner_w, y, source_y - 12,
                                      sizes=(25, 24, 23, 22))
    draw_lines(draw, (x0 + pad, y), lines, fnt, BODY, leading)
    draw.text((x0 + pad, source_y), source.upper(), font=font(F_BOLD, 17), fill=MUTED)


# --------------------------------------------------------------------------
# Page composition
# --------------------------------------------------------------------------
def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    content_w = WIDTH - 2 * MARGIN

    # Header -------------------------------------------------------------
    y = 30
    draw.text((MARGIN, y), "WORLD NEWS · ONE IMAGE", font=font(F_BOLD, 26), fill=GOLD)
    date_text = "WEDNESDAY, 25 NOVEMBER 2026"
    draw.text((WIDTH - MARGIN - draw.textlength(date_text, font=font(F_BOLD, 26)), y),
              date_text, font=font(F_BOLD, 26), fill=MUTED)
    y += 40
    draw.text((MARGIN, y), "The World on 25 November", font=font(F_BOLD, 62), fill=INK)
    y += 82
    draw.text((MARGIN, y),
              "The day's biggest stories — climate, war, trade, space and markets — in a single frame.",
              font=font(F_SANS, 26), fill=BODY)
    y += 36
    draw.rectangle([MARGIN, y, WIDTH - MARGIN, y + 3], fill=GOLD)
    y += 20

    # Featured story ------------------------------------------------------
    featured_h = 258
    featured_card(draw, [MARGIN, y, WIDTH - MARGIN, y + featured_h], *FEATURED)
    y += featured_h + 16

    # Grid: two rows of three --------------------------------------------
    gap = 16
    card_w = (content_w - 2 * gap) // 3
    card_h = 318
    for row in range(2):
        for col in range(3):
            story = STORIES[row * 3 + col]
            x0 = MARGIN + col * (card_w + gap)
            story_card(draw, [x0, y, x0 + card_w, y + card_h], *story)
        y += card_h + gap

    # Footer ---------------------------------------------------------------
    draw.text((MARGIN, HEIGHT - 36), FOOTER, font=font(F_SANS, 18), fill=MUTED)

    img.save("news-2026-11-25.png")
    print("wrote news-2026-11-25.png", img.size)


if __name__ == "__main__":
    main()
