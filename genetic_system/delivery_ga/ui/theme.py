"""Shared UI palette and color helpers.

Flat, light, dashboard-style theme: solid surfaces, hairline borders, one
accent. No gradients, gloss, or drop shadows.
"""

# Neutrals
BG = (244, 246, 248)        # app background (light gray)
CARD = (255, 255, 255)      # card / panel surface
FIELD = (247, 248, 250)     # map field + chart plot background
BORDER = (228, 231, 235)    # hairline border
GRID = (235, 238, 241)      # faint grid lines

# Text
TXT = (31, 41, 51)          # primary slate
MUT = (123, 135, 148)       # muted / secondary

# Accents (tuned to read on white)
ACCENT = (59, 111, 224)     # calm blue
SUCCESS = (32, 165, 105)    # calm green
WARNING = (214, 158, 46)    # amber

FAMILIES = [
    (230, 60, 80),
    (40, 140, 240),
    (40, 200, 80),
    (250, 180, 40),
    (140, 70, 210),
]
SHADE_F = [0.4, 0.2, 0.0, -0.2, -0.4]


def shade(color, factor):
    if factor >= 0:
        return tuple(int(channel + (255 - channel) * factor) for channel in color)
    return tuple(int(max(0, channel * (1 + factor))) for channel in color)


def courier_color(child_idx, courier_idx):
    """Color matching the pre-rendered truck sprites (lightened spread)."""
    return shade(FAMILIES[child_idx % len(FAMILIES)], SHADE_F[courier_idx % 5])


def courier_hue(courier_idx):
    """Distinct, readable hue per courier for the champion overlay + load bars.

    One color per courier (red/blue/green/amber/purple) so a load bar maps to
    its route at a glance. Race mode keeps the family=child scheme separately.
    """
    return shade(FAMILIES[courier_idx % len(FAMILIES)], -0.12)


def truck_sprite_name(child_idx, courier_idx):
    return f"truck_c{child_idx % len(FAMILIES)}_q{courier_idx % 5}.png"
