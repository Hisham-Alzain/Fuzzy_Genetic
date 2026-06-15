"""Generate pre-rendered PNG assets for the delivery GA UI."""

from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "delivery_ga" / "assets" / "ui"

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


def ensure_dir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def gradient_fill(surface, top_color, bottom_color):
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top_color[i] * (1 - t) + bottom_color[i] * t) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (width, y))


def radial_glow(size, center, radius, color):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    for step in range(radius, 0, -12):
        alpha = int(255 * (step / radius) ** 2 * 0.12)
        pygame.draw.circle(surf, (*color, alpha), center, step)
    return surf


def pill_surface(size, top_color, bottom_color, border_color, radius, gloss_alpha=55):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    base = pygame.Surface(size, pygame.SRCALPHA)
    gradient_fill(base, top_color, bottom_color)
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, *size), border_radius=radius)
    base.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(base, (0, 0))
    pygame.draw.rect(surf, border_color, (0, 0, size[0], size[1]), width=2, border_radius=radius)
    gloss = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(gloss, (255, 255, 255, gloss_alpha), (12, 8, size[0] - 24, size[1] // 2), border_radius=radius)
    surf.blit(gloss, (0, 0))
    return surf


def glass_panel(size, top_color, bottom_color, radius, border=(255, 255, 255, 24)):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    gradient_fill(surf, top_color, bottom_color)
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(overlay, (255, 255, 255, 16), (0, 0, size[0], size[1]), border_radius=radius)
    pygame.draw.rect(overlay, border, (1, 1, size[0] - 2, size[1] - 2), border_radius=radius, width=2)
    pygame.draw.rect(overlay, (255, 255, 255, 20), (18, 14, size[0] - 36, size[1] * 0.22), border_radius=radius)
    surf.blit(overlay, (0, 0))
    return surf


def shadow_surface(size, alpha=90, radius=22, inset=12, offset_y=6):
    surf = pygame.Surface((size[0] + inset * 2, size[1] + inset * 2), pygame.SRCALPHA)
    for grow, fade in ((10, alpha // 4), (6, alpha // 2), (0, alpha)):
        rect = pygame.Rect(
            inset - grow,
            inset + offset_y - grow,
            size[0] + grow * 2,
            size[1] + grow * 2,
        )
        pygame.draw.rect(surf, (12, 18, 32, fade), rect, border_radius=radius + grow)
    return surf


def save(name, surface):
    pygame.image.save(surface, OUT_DIR / name)


def build_buttons():
    save("button_shadow.png", shadow_surface((480, 72), alpha=100, radius=24, inset=16, offset_y=8))
    green_idle = pill_surface((480, 72), (60, 220, 120), (20, 160, 80), (150, 255, 200), 24, 40)
    green_hover = pill_surface((480, 72), (80, 240, 140), (30, 180, 100), (180, 255, 220), 24, 60)
    red_idle = pill_surface((480, 72), (240, 80, 100), (180, 40, 60), (255, 180, 190), 24, 40)
    red_hover = pill_surface((480, 72), (255, 100, 120), (200, 50, 70), (255, 200, 210), 24, 60)
    save("button_green_idle.png", green_idle)
    save("button_green_hover.png", green_hover)
    save("button_red_idle.png", red_idle)
    save("button_red_hover.png", red_hover)


def build_sliders():
    track = pill_surface((720, 16), (20, 26, 40), (10, 15, 25), (60, 75, 100), 8, 0)
    fill = pill_surface((720, 16), (40, 180, 255), (20, 120, 255), (120, 220, 255), 8, 20)
    knob = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(knob, (0, 0, 0, 80), (24, 28), 16)
    pygame.draw.circle(knob, (255, 255, 255), (24, 24), 16)
    pygame.draw.circle(knob, (40, 160, 255), (24, 24), 8)
    save("slider_track.png", track)
    save("slider_fill.png", fill)
    save("slider_knob.png", knob)


def build_panels():
    side = pygame.Surface((520, 980), pygame.SRCALPHA)
    gradient_fill(side, (18, 24, 40), (10, 14, 26))
    pygame.draw.rect(side, (45, 55, 80), (0, 0, 520, 980), width=2, border_radius=24)
    side.blit(radial_glow(side.get_size(), (260, -100), 400, (40, 120, 255)), (0, 0))
    save("side_panel.png", side)

    modal = pygame.Surface((900, 900), pygame.SRCALPHA)
    gradient_fill(modal, (22, 30, 50), (12, 18, 34))
    pygame.draw.rect(modal, (60, 80, 110), (0, 0, 900, 900), width=2, border_radius=32)
    pygame.draw.rect(modal, (255, 255, 255, 10), (4, 4, 892, 180), border_radius=28)
    modal.blit(radial_glow(modal.get_size(), (450, 0), 500, (40, 120, 255)), (0, 0))
    save("setup_modal.png", modal)

    card = pygame.Surface((520, 210), pygame.SRCALPHA)
    gradient_fill(card, (26, 34, 56), (16, 22, 38))
    pygame.draw.rect(card, (55, 65, 90), (0, 0, 520, 210), width=2, border_radius=20)
    save("chart_card.png", card)


def build_house():
    surf = pygame.Surface((96, 96), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (12, 60, 72, 24))
    pygame.draw.rect(surf, (240, 244, 250), (20, 36, 56, 36), border_radius=6)
    pygame.draw.polygon(surf, (255, 80, 90), [(12, 40), (48, 10), (84, 40)])
    pygame.draw.rect(surf, (100, 200, 255), (38, 46, 20, 14), border_radius=3)
    pygame.draw.rect(surf, (120, 80, 50), (28, 56, 12, 16), border_radius=2)
    save("house.png", surf)


def build_depot():
    surf = pygame.Surface((164, 164), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (18, 120, 128, 30))
    pygame.draw.rect(surf, (70, 80, 95), (22, 34, 120, 90), border_radius=16)
    pygame.draw.rect(surf, (90, 105, 125), (16, 26, 132, 24), border_radius=8)
    pygame.draw.rect(surf, (40, 48, 60), (40, 64, 30, 60), border_radius=4)
    pygame.draw.rect(surf, (40, 48, 60), (94, 64, 30, 60), border_radius=4)
    pygame.draw.rect(surf, (255, 210, 80), (50, 50, 10, 6), border_radius=3)
    pygame.draw.rect(surf, (255, 210, 80), (104, 50, 10, 6), border_radius=3)
    save("depot.png", surf)


def build_truck(color):
    surf = pygame.Surface((184, 104), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (16, 70, 140, 26))
    pygame.draw.rect(surf, (245, 250, 255), (100, 26, 46, 46), border_radius=12)
    pygame.draw.rect(surf, color, (20, 20, 86, 58), border_radius=10)
    pygame.draw.rect(surf, (120, 190, 255), (124, 32, 16, 34), border_radius=6)
    pygame.draw.rect(surf, (30, 35, 45), (34, 12, 30, 14), border_radius=6)
    pygame.draw.rect(surf, (30, 35, 45), (100, 12, 30, 14), border_radius=6)
    pygame.draw.rect(surf, (30, 35, 45), (34, 72, 30, 14), border_radius=6)
    pygame.draw.rect(surf, (30, 35, 45), (100, 72, 30, 14), border_radius=6)
    pygame.draw.circle(surf, (255, 240, 150), (146, 36), 8)
    pygame.draw.circle(surf, (255, 240, 150), (146, 62), 8)
    pygame.draw.circle(surf, (255, 255, 255, 180), (63, 49), 12)
    return surf


def build_trucks():
    for child_idx, family in enumerate(FAMILIES):
        for courier_idx, factor in enumerate(SHADE_F):
            color = shade(family, factor)
            truck = build_truck(color)
            save(f"truck_c{child_idx}_q{courier_idx}.png", truck)


def main():
    pygame.init()
    ensure_dir()
    build_buttons()
    build_sliders()
    build_panels()
    build_house()
    build_depot()
    build_trucks()
    pygame.quit()
    print(f"Generated UI assets in {OUT_DIR}")


if __name__ == "__main__":
    main()
