import pygame

# ── Palette ──
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)
ORANGE = (255, 165, 0)
RED = (255, 60, 60)
CYAN = (0, 200, 220)
LIGHT_GRAY = (180, 180, 190)
MED_GRAY = (100, 100, 110)
GRAY = (35, 35, 40)
DARK_GRAY = (20, 20, 24)
PLOT_BG = (18, 18, 22)

MF_COLORS = [
    (100, 149, 237),  # cornflower blue
    (0, 191, 255),  # deep sky blue
    (255, 255, 80),  # yellow
    (255, 165, 0),  # orange
    (255, 69, 0),  # red-orange
]


# ═══════════════════════════════════════════════════════════════
#  TOP BAR  (spans game_width only, above the game area)
# ═══════════════════════════════════════════════════════════════


def draw_top_bar(
    surf,
    metrics,
    manual_mode,
    game_paused,
    game_w,
    top_h,
    font_name,
    active_input=None,
    input_text="",
):
    """Draw the horizontal control bar above the game area.
    Returns list of clickable button rects for manual mode."""

    bar = pygame.Rect(0, 0, game_w, top_h)
    pygame.draw.rect(surf, GRAY, bar)
    pygame.draw.line(surf, LIGHT_GRAY, (0, top_h - 1), (game_w, top_h - 1), 1)

    fh = pygame.font.Font(font_name, 15)
    fb = pygame.font.Font(font_name, 13)
    fs = pygame.font.Font(font_name, 11)

    # ── Row 0: Title + mode + keybinds ──
    y = 5
    surf.blit(fh.render("DDA CONTROL", True, YELLOW), (8, y))

    mode_txt = "MANUAL" if manual_mode else "AUTO"
    mode_clr = GREEN if manual_mode else LIGHT_GRAY
    surf.blit(fb.render(mode_txt, True, mode_clr), (130, y + 1))

    pause_txt = "PAUSED" if game_paused else ""
    surf.blit(fb.render(pause_txt, True, ORANGE), (200, y + 1))

    keys_txt = "[TAB] Pause  [M] Manual  [P] Plots  [ESC] Quit"
    surf.blit(fs.render(keys_txt, True, MED_GRAY), (game_w - 310, y + 3))

    # ── Row 1-2: Crisp Inputs (2 rows × 3 columns) ──
    y = 28
    surf.blit(fs.render("CRISP INPUTS", True, CYAN), (8, y))
    y += 16

    input_fields = [
        ("Kills", "mobs_destroyed", 0, 600, 10),
        ("Time", "session_time_elapsed", 0, 600, 10),
        ("Health", "health", 0, 100, 10),
        ("Lives", "lives", 1, 5, 1),
        ("Gun", "gun_level", 1, 3, 1),
        ("Restarts", "restart_count", 0, 20, 1),
    ]

    btn_rects = []
    input_rects = []  # Track the clickable text boxes
    col_w = game_w // 3

    for idx, (label, key, lo, hi, step) in enumerate(input_fields):
        row = idx // 3
        col = idx % 3
        cx = col * col_w + 12
        cy = y + row * 24

        val = metrics.get(key, 0)

        # Draw the Label
        label_surf = fb.render(f"{label}: ", True, WHITE)
        surf.blit(label_surf, (cx, cy))

        # -- NEW: Draw the Text Input Box --
        box_x = cx + label_surf.get_width()
        box_w = 40
        box_rect = pygame.Rect(box_x, cy - 2, box_w, 18)

        # Highlight the box if the user is currently typing in it
        is_active = active_input == key
        box_color = (80, 80, 100) if is_active else (40, 40, 45)
        pygame.draw.rect(surf, box_color, box_rect, border_radius=3)

        # Determine what text to show (the typing buffer, or the actual value)
        display_str = input_text if is_active else str(val)
        text_color = YELLOW if is_active else WHITE
        surf.blit(fb.render(display_str, True, text_color), (box_rect.x + 4, cy))

        if manual_mode:
            input_rects.append((box_rect, key))  # Save for click detection

            # Shift the + and - buttons to the right of the text box
            bx = box_rect.right + 10
            r_minus = pygame.Rect(bx, cy, 22, 17)
            pygame.draw.rect(surf, RED, r_minus, border_radius=2)
            _blit_centered(surf, fb, "-", WHITE, r_minus.centerx, r_minus.y - 1)

            r_plus = pygame.Rect(bx + 28, cy, 22, 17)
            pygame.draw.rect(surf, GREEN, r_plus, border_radius=2)
            _blit_centered(surf, fb, "+", WHITE, r_plus.centerx, r_plus.y - 1)

            btn_rects.append((r_minus, r_plus, key, lo, hi, step))

    # ── Row 3: Outputs ──
    y = y + 52
    _hline(surf, 8, game_w - 8, y - 4)

    surf.blit(fs.render("DEFUZZIFIED OUTPUTS", True, ORANGE), (8, y))

    spd = metrics.get("current_speed_mult", 1.0)
    dly = metrics.get("current_spawn_delay", 1.5)
    msz = metrics.get("current_mob_size", 1.0)
    spd_clr = GREEN if spd < 1.15 else (ORANGE if spd < 1.35 else RED)

    out_y = y + 15
    surf.blit(fb.render(f"Speed: {spd:.2f}x", True, spd_clr), (12, out_y))
    surf.blit(fb.render(f"Delay: {dly:.2f}s", True, WHITE), (col_w + 12, out_y))
    surf.blit(fb.render(f"Size:  {msz:.2f}x", True, WHITE), (col_w * 2 + 12, out_y))

    # ── Row 4: Fired rules (compact single line) ──
    out_y += 20
    fired = metrics.get("fired_rules", [])
    if fired and "No rules" not in fired[0]:
        # Build compact summary: "R1[0.60] R5[0.60] R8[0.45]"
        compact = []
        for r in fired[:6]:  # max 6 shown
            # Extract "R1" and "[0.60]" from the full description
            parts = r.split(":")
            tag = parts[0].strip() if parts else r[:3]
            # Extract strength from the end
            if "[" in r:
                strength = r[r.rfind("[") :]
                compact.append(f"{tag}{strength}")
            else:
                compact.append(tag)
        line = "Active: " + "  ".join(compact)
    else:
        line = "Active: baseline (no dominant rules)"
    surf.blit(fs.render(line, True, YELLOW), (12, out_y))

    return btn_rects, input_rects


# ═══════════════════════════════════════════════════════════════
#  PLOTS PANEL  (right side, full height — 3×3 MF grid)
# ═══════════════════════════════════════════════════════════════


def draw_plot_panel(
    surf, mf_data, current_values, panel_x, panel_w, panel_h, font_name
):
    """Draw the 9 membership-function plots in a 3×3 grid on the right."""

    # Background
    panel_rect = pygame.Rect(panel_x, 0, panel_w, panel_h)
    pygame.draw.rect(surf, DARK_GRAY, panel_rect)
    pygame.draw.line(surf, LIGHT_GRAY, (panel_x, 0), (panel_x, panel_h), 2)

    cols, rows = 3, 3
    pad = 8
    cell_w = (panel_w - pad * (cols + 1)) // cols
    cell_h = (panel_h - pad * (rows + 1)) // rows

    for idx, mf in enumerate(mf_data):
        row = idx // cols
        col = idx % cols
        cx = panel_x + pad + col * (cell_w + pad)
        cy = pad + row * (cell_h + pad)

        name = mf["name"]
        val = current_values.get(name, None)

        _draw_single_plot(
            surf,
            cx,
            cy,
            cell_w,
            cell_h,
            mf["universe"],
            mf["terms"],
            val,
            name,
            mf["type"],
            font_name,
        )


def _draw_single_plot(
    surf, x, y, w, h, universe, terms, current_val, title, var_type, font_name
):
    """Render one membership function plot using pure pygame."""

    # Background + border
    pygame.draw.rect(surf, PLOT_BG, (x, y, w, h), border_radius=4)
    pygame.draw.rect(surf, (55, 55, 60), (x, y, w, h), 1, border_radius=4)

    # Margins for data area
    ml, mr, mt, mb = 10, 10, 22, 26
    dx = x + ml
    dy = y + mt
    dw = w - ml - mr
    dh = h - mt - mb

    if dw < 20 or dh < 20:
        return

    u_min, u_max = float(universe[0]), float(universe[-1])
    u_range = u_max - u_min if u_max > u_min else 1.0

    # Faint horizontal grid lines at 0.25, 0.5, 0.75
    for frac in (0.25, 0.5, 0.75):
        gy = int(dy + dh - frac * dh)
        pygame.draw.line(surf, (35, 35, 40), (dx, gy), (dx + dw, gy), 1)

    # X-axis
    pygame.draw.line(surf, (70, 70, 75), (dx, dy + dh), (dx + dw, dy + dh), 1)
    # Y-axis
    pygame.draw.line(surf, (70, 70, 75), (dx, dy), (dx, dy + dh), 1)

    # Draw each MF as a polyline
    for ci, (label, mf_arr) in enumerate(terms.items()):
        color = MF_COLORS[ci % len(MF_COLORS)]
        points = []
        step = max(1, len(universe) // max(1, dw))
        for j in range(0, len(universe), step):
            px = dx + (float(universe[j]) - u_min) / u_range * dw
            py = dy + dh - float(mf_arr[j]) * dh
            points.append((int(px), int(py)))
        # Ensure last point
        px = dx + (float(universe[-1]) - u_min) / u_range * dw
        py = dy + dh - float(mf_arr[-1]) * dh
        points.append((int(px), int(py)))
        if len(points) > 1:
            pygame.draw.lines(surf, color, False, points, 2)

    # Current-value indicator
    if current_val is not None:
        import numpy as np

        clamped = max(u_min, min(float(current_val), u_max))
        vx = int(dx + (clamped - u_min) / u_range * dw)

        # Vertical line
        pygame.draw.line(surf, RED, (vx, dy), (vx, dy + dh), 2)

        # Dots + μ labels at each MF intersection
        fs = pygame.font.Font(font_name, 10)
        for ci, (label, mf_arr) in enumerate(terms.items()):
            mu = float(np.interp(clamped, universe, mf_arr))
            if mu > 0.01:
                dot_y = int(dy + dh - mu * dh)
                pygame.draw.circle(surf, RED, (vx, dot_y), 4)
                # μ value label
                mu_surf = fs.render(f"{mu:.2f}", True, WHITE)
                # Alternate label side to avoid overlap
                lx = vx + 6 if ci % 2 == 0 else vx - mu_surf.get_width() - 6
                lx = max(dx, min(lx, dx + dw - mu_surf.get_width()))
                surf.blit(mu_surf, (lx, dot_y - 6))

    # Title
    ft = pygame.font.Font(font_name, 12)
    type_tag = "[IN]" if var_type == "input" else "[OUT]"
    tag_color = CYAN if var_type == "input" else ORANGE
    title_surf = ft.render(title, True, WHITE)
    tag_surf = ft.render(f" {type_tag}", True, tag_color)
    surf.blit(title_surf, (x + 8, y + 4))
    surf.blit(tag_surf, (x + 8 + title_surf.get_width(), y + 4))

    # Legend (term names, compact)
    fl = pygame.font.Font(font_name, 9)
    lx = x + 8
    ly = y + h - 18
    for ci, label in enumerate(terms.keys()):
        color = MF_COLORS[ci % len(MF_COLORS)]
        pygame.draw.line(surf, color, (lx, ly + 6), (lx + 12, ly + 6), 2)
        lbl = fl.render(label, True, LIGHT_GRAY)
        surf.blit(lbl, (lx + 15, ly))
        lx += 18 + lbl.get_width()
        if lx > x + w - 30:
            break  # Ran out of horizontal space

    # Axis labels
    fa = pygame.font.Font(font_name, 9)
    surf.blit(fa.render(f"{u_min:.0f}", True, MED_GRAY), (dx, dy + dh + 3))
    max_lbl = fa.render(f"{u_max:.0f}", True, MED_GRAY)
    surf.blit(max_lbl, (dx + dw - max_lbl.get_width(), dy + dh + 3))

    # Current value (center, below axis)
    if current_val is not None:
        if isinstance(current_val, float):
            vtxt = f"= {current_val:.2f}"
        else:
            vtxt = f"= {current_val}"
        val_lbl = fa.render(vtxt, True, YELLOW)
        surf.blit(val_lbl, (dx + dw // 2 - val_lbl.get_width() // 2, dy + dh + 3))

    # Y-axis "1.0" label
    surf.blit(fa.render("1.0", True, MED_GRAY), (dx - 2, dy - 10))


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════


def _blit_centered(surf, font, text, color, cx, y):
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width() // 2, y))


def _hline(surf, x1, x2, y):
    pygame.draw.line(surf, (70, 70, 75), (int(x1), int(y)), (int(x2), int(y)), 1)
