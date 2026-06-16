"""Main pygame application — flat, light dashboard UI."""

import math
import os
import time

import numpy as np
import pygame


def _enable_dpi_awareness():
    """Tell Windows we render our own pixels.

    Without this, a scaled display (125%/150%) makes Windows bitmap-stretch the
    pygame window after the fact, which leaves all small text jagged/blurry. With
    it, pygame draws at the real physical resolution and stays razor-sharp.
    """
    try:
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor aware
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()       # system aware (older Windows)
    except Exception:
        pass  # non-Windows or no ctypes — nothing to do

from delivery_ga.domain.maps import clustered_map
from delivery_ga.domain.routing import decode
from delivery_ga.engine.ga import GA
from delivery_ga.ui.race import Race
from delivery_ga.ui.sprites import (
    load_depot_sprite,
    load_house_sprite,
    load_truck_sprite,
)
from delivery_ga.ui.theme import (
    ACCENT,
    BG,
    BORDER,
    CARD,
    FIELD,
    GRID,
    MUT,
    SUCCESS,
    TXT,
    WARNING,
    courier_hue,
)
from delivery_ga.ui.widgets import Button, Slider

PAD = 20            # card content padding
CARD_RADIUS = 14


class App:
    def __init__(
        self, ga, gens, race_every=100, top_n=5, title="Courier GA", out_dir="."
    ):
        self.ga = ga
        self.gens = gens
        self.race_every = race_every
        self.top_n = top_n
        self.out_dir = out_dir
        _enable_dpi_awareness()  # must run before the window is created
        pygame.init()
        # Render at the display's native resolution whenever the responsive layout
        # fits, so text and sprites stay razor-sharp (no per-frame downscale blur).
        # Only when the screen is genuinely too small do we fall back to drawing on
        # an off-screen canvas and scaling it down to fit.
        desktop = pygame.display.Info()
        avail_w, avail_h = desktop.current_w - 40, desktop.current_h - 90
        self.W = min(1440, max(1100, avail_w))   # design width  (layout needs >= 1100)
        self.H = min(1024, max(820, avail_h))    # design height (layout needs >= 820)
        if avail_w >= self.W and avail_h >= self.H:
            self.win_w, self.win_h = self.W, self.H
            self.window = pygame.display.set_mode((self.win_w, self.win_h))
            self.screen = self.window  # draw straight to the window: crisp, no scaling
        else:
            scale = min(avail_w / self.W, avail_h / self.H)
            self.win_w, self.win_h = int(self.W * scale), int(self.H * scale)
            self.window = pygame.display.set_mode((self.win_w, self.win_h))
            self.screen = pygame.Surface((self.W, self.H))  # scaled down for tiny screens
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

        face = "segoeui,arial"
        self.f_cap = pygame.font.SysFont(face, 13)              # ALL-CAPS labels
        self.f_label = pygame.font.SysFont(face, 15)            # muted labels
        self.f_body = pygame.font.SysFont(face, 16)             # body
        self.f_card = pygame.font.SysFont(face, 19, bold=True)  # card titles
        self.f_stat = pygame.font.SysFont(face, 27, bold=True)  # stat numbers
        self.f_title = pygame.font.SysFont(face, 30, bold=True)  # page / modal title
        self._text_cache = {}  # (text, font_id, color) -> rendered surface

        self.state = "SETUP"
        self.race = None
        self.hold = 0.0
        self.paused = False
        self.show_best = True
        self.frame = 0
        self.layout = {}

        self.trail_overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.car_cache = {}
        self.house_sprite = pygame.transform.smoothscale(load_house_sprite(), (32, 32))
        self.depot_sprite = pygame.transform.smoothscale(load_depot_sprite(), (80, 80))

        self.setup_sliders = [
            Slider(0, 0, 300, 8, 10, 200, len(self.ga.stops), "Delivery Stops"),
            Slider(0, 0, 300, 8, 1, 10, self.ga.k, "Courier Count"),
            Slider(0, 0, 300, 8, 20, 1000, len(self.ga.pop), "Population Size"),
            Slider(0, 0, 300, 8, 10, 3000, self.gens, "Generations"),
            Slider(0, 0, 300, 8, 0.0, 0.5, self.ga.mut_p, "Mutation Rate"),
        ]
        self.btn_start = Button(0, 0, 300, 52, "Launch Simulation", "primary")
        self.mut_slider = Slider(0, 0, 300, 8, 0.0, 0.5, self.ga.mut_p, "Mutation Rate")
        self.speed_slider = Slider(0, 0, 300, 8, 1.0, 200.0, 25.0, "Evolution Speed")
        self.btn_stop = Button(0, 0, 300, 44, "Reconfigure", "secondary")

        self._reflow_layout()

    def _reflow_layout(self):
        margin = 28
        gutter = 24
        sidebar_w = 440
        self.layout["map_outer"] = pygame.Rect(
            margin, margin, self.W - sidebar_w - margin * 2 - gutter, self.H - margin * 2
        )
        self.layout["sidebar"] = pygame.Rect(
            self.layout["map_outer"].right + gutter, margin, sidebar_w, self.H - margin * 2
        )

        outer = self.layout["map_outer"]
        mp = 24
        self.layout["map_header"] = pygame.Rect(outer.x + mp, outer.y + mp, outer.w - mp * 2, 54)
        self.layout["map_footer"] = pygame.Rect(outer.x + mp, outer.bottom - mp - 18, outer.w - mp * 2, 18)
        view_top = self.layout["map_header"].bottom + 12
        view_bottom = self.layout["map_footer"].top - 12
        self.layout["map_view"] = pygame.Rect(outer.x + mp, view_top, outer.w - mp * 2, view_bottom - view_top)

        sidebar = self.layout["sidebar"]
        gap = 18
        y = sidebar.y
        self.layout["status_card"] = pygame.Rect(sidebar.x, y, sidebar.w, 184)
        y += 184 + gap
        self.layout["chart_card"] = pygame.Rect(sidebar.x, y, sidebar.w, 192)
        y += 192 + gap
        self.layout["routes_card"] = pygame.Rect(sidebar.x, y, sidebar.w, 224)
        y += 224 + gap
        self.layout["controls_card"] = pygame.Rect(sidebar.x, y, sidebar.w, sidebar.bottom - y)

        modal = pygame.Rect(0, 0, 760, 660)
        modal.center = (self.W // 2, self.H // 2)
        self.layout["setup_modal"] = modal
        mpad = 56
        slider_x = modal.x + mpad
        slider_w = modal.w - mpad * 2
        start_y = modal.y + 168
        for idx, slider in enumerate(self.setup_sliders):
            slider.set_rect(slider_x, start_y + idx * 72, slider_w, 8)
        self.btn_start.set_rect(modal.x + mpad, modal.bottom - 84, slider_w, 52)

        # Live-control widget rects.
        controls = self.layout["controls_card"]
        cw = controls.w - PAD * 2
        self.mut_slider.set_rect(controls.x + PAD, controls.y + 86, cw, 8)
        self.speed_slider.set_rect(controls.x + PAD, controls.y + 142, cw, 8)
        self.btn_stop.set_rect(controls.x + PAD, controls.bottom - PAD - 44, cw, 44)

        map_view = self.layout["map_view"]
        scale = min(map_view.w, map_view.h) / 1000.0
        offset_x = map_view.x + (map_view.w - 1000 * scale) / 2
        offset_y = map_view.y + (map_view.h - 1000 * scale) / 2
        self._sc = lambda p: (offset_x + p[0] * scale, offset_y + p[1] * scale)

    # ----- primitives -------------------------------------------------------
    def get_car_sprite(self, sprite_name, direction):
        angle = int(math.degrees(math.atan2(-direction[1], direction[0]))) % 360
        key = (sprite_name, angle)
        if key not in self.car_cache:
            base = load_truck_sprite(sprite_name)
            self.car_cache[key] = pygame.transform.rotozoom(base, angle, 0.28)
        return self.car_cache[key]

    def _render_text(self, text, font, col):
        key = (text, id(font), col)
        surf = self._text_cache.get(key)
        if surf is None:
            if len(self._text_cache) > 600:  # cap growth from ever-changing numbers
                self._text_cache.clear()
            surf = font.render(text, True, col)
            self._text_cache[key] = surf
        return surf

    def _text(self, text, x, y, font=None, col=TXT):
        self.screen.blit(self._render_text(text, font or self.f_body, col), (int(x), int(y)))

    def _text_right(self, text, right, y, font=None, col=TXT):
        surf = self._render_text(text, font or self.f_body, col)
        self.screen.blit(surf, surf.get_rect(topright=(int(right), int(y))))

    def _card(self, rect, radius=CARD_RADIUS):
        pygame.draw.rect(self.screen, CARD, rect, border_radius=radius)
        pygame.draw.rect(self.screen, BORDER, rect, width=1, border_radius=radius)

    def _card_title(self, card, title, accent=None):
        x = card.x + PAD
        y = card.y + 18
        if accent is not None:
            pygame.draw.rect(self.screen, accent, (x, y + 2, 4, 16), border_radius=2)
            x += 12
        self._text(title, x, y, self.f_card, TXT)
        return card.y + 18 + 30  # content top

    def _pill(self, center_right_y, text, fill):
        font = self.f_cap
        tw = font.size(text)[0]
        w, h = tw + 24, 24
        right, y = center_right_y
        rect = pygame.Rect(right - w, y, w, h)
        pygame.draw.rect(self.screen, fill, rect, border_radius=h // 2)
        label = font.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _chip(self, rect, text, fill, text_col=(255, 255, 255)):
        pygame.draw.rect(self.screen, fill, rect, border_radius=rect.h // 2)
        label = self.f_cap.render(text, True, text_col)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _stat(self, x, y, label, value, accent=TXT):
        self._text(label.upper(), x, y, self.f_cap, MUT)
        self._text(value, x, y + 16, self.f_stat, accent)

    def _progress_bar(self, rect, fraction, color=ACCENT):
        pygame.draw.rect(self.screen, BORDER, rect, border_radius=rect.h // 2)
        w = max(rect.h, int(rect.w * max(0.0, min(1.0, fraction))))
        pygame.draw.rect(self.screen, color, (rect.x, rect.y, w, rect.h), border_radius=rect.h // 2)

    # ----- map / world ------------------------------------------------------
    def _draw_background(self):
        self.screen.fill(BG)

    def _draw_world(self, flash=None):
        outer = self.layout["map_outer"]
        self._card(outer, radius=16)

        view = self.layout["map_view"]
        pygame.draw.rect(self.screen, FIELD, view, border_radius=12)
        clip = view.inflate(-3, -3)
        self.screen.set_clip(clip)
        for x in range(view.x, view.right, 56):
            pygame.draw.line(self.screen, GRID, (x, view.y), (x, view.bottom), 1)
        for y in range(view.y, view.bottom, 56):
            pygame.draw.line(self.screen, GRID, (view.x, y), (view.right, y), 1)
        self.screen.set_clip(None)
        pygame.draw.rect(self.screen, BORDER, view, width=1, border_radius=12)

        header = self.layout["map_header"]
        self._text("Courier GA", header.x, header.y, self.f_title, TXT)
        self._text("Multi-courier route optimizer", header.x, header.y + 36, self.f_label, MUT)
        if self.paused:
            state, color = "PAUSED", WARNING
        elif self.state == "RACE":
            state, color = "RACE", ACCENT
        else:
            state, color = "OPTIMIZING", SUCCESS
        self._pill((header.right, header.y + 6), state, color)

        footer = self.layout["map_footer"]
        self._text("SPACE pause   B best routes   S screenshot   ESC quit", footer.x, footer.y, self.f_cap, MUT)

        for idx, point in enumerate(self.ga.stops):
            screen_point = self._sc(point)
            rect = self.house_sprite.get_rect(center=screen_point)
            self.screen.blit(self.house_sprite, rect)
            if flash is not None and flash[idx] > 0.05:
                radius = 10 + int(16 * flash[idx])
                pulse = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(pulse, (*ACCENT, int(140 * flash[idx])), (radius + 2, radius + 2), radius, width=3)
                self.screen.blit(pulse, pulse.get_rect(center=screen_point))

        depot_point = self._sc(self.ga.depot)
        self.screen.blit(self.depot_sprite, self.depot_sprite.get_rect(center=depot_point))

    def _routes_of(self, individual, alpha, width=4):
        self.trail_overlay.fill((0, 0, 0, 0))
        routes = decode(individual.assign, individual.order, self.ga.k)
        for courier_idx, route in enumerate(routes):
            if not len(route):
                continue
            color = courier_hue(courier_idx)
            pts = [self._sc(self.ga.depot)]
            pts.extend(self._sc(point) for point in self.ga.stops[route])
            pts.append(self._sc(self.ga.depot))
            if len(pts) > 1:
                pygame.draw.lines(self.trail_overlay, (*color, alpha), False, pts, width)
        self.screen.blit(self.trail_overlay, (0, 0))

    # ----- sidebar cards ----------------------------------------------------
    def _draw_status_card(self):
        card = self.layout["status_card"]
        self._card(card)
        top = self._card_title(card, "Overview", accent=ACCENT)
        x = card.x + PAD
        w = card.w - PAD * 2
        self._text(f"Generation {self.ga.gen:,} / {self.gens:,}", x, top, self.f_body, TXT)
        bar = pygame.Rect(x, top + 24, w, 8)
        self._progress_bar(bar, self.ga.gen / max(1, self.gens))
        best = self.ga.best
        stat_y = bar.bottom + 16
        self._stat(x, stat_y, "Best Makespan", f"{best.makespan:,.0f}", TXT)
        self._stat(x + w // 2, stat_y, "Best Fitness", f"{best.fitness:.5f}", ACCENT)

    def _draw_chart_card(self):
        card = self.layout["chart_card"]
        self._card(card)
        top = self._card_title(card, "Fitness", accent=SUCCESS)
        x = card.x + PAD
        w = card.w - PAD * 2
        # legend
        self._text_right("AVG", card.right - PAD, card.y + 22, self.f_cap, MUT)
        pygame.draw.circle(self.screen, MUT, (card.right - PAD - self.f_cap.size("AVG")[0] - 8, card.y + 28), 4)
        bestlbl_x = card.right - PAD - self.f_cap.size("AVG")[0] - 8 - 18 - self.f_cap.size("BEST")[0]
        self._text(" BEST", bestlbl_x - 4, card.y + 22, self.f_cap, SUCCESS)
        pygame.draw.circle(self.screen, SUCCESS, (bestlbl_x - 10, card.y + 28), 4)

        plot = pygame.Rect(x, top + 4, w, card.bottom - (top + 4) - PAD)
        pygame.draw.rect(self.screen, FIELD, plot, border_radius=10)
        pygame.draw.rect(self.screen, BORDER, plot, width=1, border_radius=10)
        for i in range(1, 3):
            gy = plot.y + plot.h * i / 3
            pygame.draw.line(self.screen, GRID, (plot.x + 6, gy), (plot.right - 6, gy), 1)
        history = self.ga.history
        if len(history) > 2:
            hist = np.array(history[-2000:])
            top_v = max(1e-9, hist[:, :2].max())
            for col_idx, color in ((1, MUT), (0, SUCCESS)):
                ys = hist[:, col_idx] / top_v
                pts = [
                    (
                        plot.x + 8 + i * (plot.w - 16) / max(1, len(ys) - 1),
                        plot.bottom - 8 - y * (plot.h - 16),
                    )
                    for i, y in enumerate(ys)
                ]
                if len(pts) > 1:
                    pygame.draw.aalines(self.screen, color, False, pts)

    def _draw_routes_card(self):
        card = self.layout["routes_card"]
        self._card(card)
        racing = self.state == "RACE" and self.race is not None
        top = self._card_title(card, "Leaderboard" if racing else "Courier Load", accent=WARNING)
        x = card.x + PAD
        w = card.w - PAD * 2

        if racing:
            order = self.race.done_order
            if not order:
                self._text("Race underway — finish order populates live.", x, top + 4, self.f_label, MUT)
                return
            for rank, child_idx in enumerate(order[:5]):
                name, color, makespan = self.race.names[child_idx]
                row_y = top + rank * 32
                self._chip(pygame.Rect(x, row_y, 26, 22), str(rank + 1), color)
                self._text(name.title(), x + 38, row_y + 2, self.f_body, TXT)
                self._text_right(f"{makespan:,.0f}", card.right - PAD, row_y + 2, self.f_body, MUT)
            return

        best = self.ga.best
        if best.lengths is None or best.lengths.max() <= 0:
            return
        max_length = best.lengths.max()
        avail = card.bottom - PAD - top
        stride = min(36, avail / max(1, len(best.lengths)))
        for courier_idx, route_length in enumerate(best.lengths):
            row_y = int(top + courier_idx * stride)
            color = courier_hue(courier_idx)
            self._chip(pygame.Rect(x, row_y, 24, 20), str(courier_idx + 1), color)
            bar = pygame.Rect(x + 36, row_y + 2, w - 36 - 70, 16)
            pygame.draw.rect(self.screen, BORDER, bar, border_radius=8)
            fill_w = max(8, int(bar.w * route_length / max_length))
            pygame.draw.rect(self.screen, color, (bar.x, bar.y, fill_w, bar.h), border_radius=8)
            self._text_right(f"{route_length:,.0f}", card.right - PAD, row_y + 1, self.f_label, TXT)

    def _draw_controls_card(self):
        card = self.layout["controls_card"]
        self._card(card)
        self._card_title(card, "Controls", accent=ACCENT)
        self.mut_slider.draw(self.screen, self.f_body, self.f_cap, f"{self.mut_slider.val:.3f}")
        self.speed_slider.draw(self.screen, self.f_body, self.f_cap, str(int(self.speed_slider.val)))
        self.btn_stop.draw(self.screen, self.f_body)

    def _draw_sidebar(self):
        self._draw_status_card()
        self._draw_chart_card()
        self._draw_routes_card()
        self._draw_controls_card()

    # ----- setup ------------------------------------------------------------
    def _draw_setup_frame(self):
        self._draw_background()
        self._draw_world()
        scrim = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        scrim.fill((15, 20, 30, 150))
        self.screen.blit(scrim, (0, 0))

        modal = self.layout["setup_modal"]
        self._card(modal, radius=18)
        mpad = 56
        self._text("Configure Simulation", modal.x + mpad, modal.y + 52, self.f_title, TXT)
        self._text(
            f"{int(self.setup_sliders[0].val)} stops · "
            f"{int(self.setup_sliders[1].val)} couriers · "
            f"pop {int(self.setup_sliders[2].val)}",
            modal.x + mpad, modal.y + 96, self.f_body, MUT,
        )
        for slider in self.setup_sliders:
            value_text = f"{slider.val:.3f}" if slider.max_val <= 1.0 else str(int(slider.val))
            slider.draw(self.screen, self.f_body, self.f_cap, value_text)
        self._text(
            "Larger population & generations search harder but run slower.",
            modal.x + mpad, modal.bottom - 124, self.f_label, MUT,
        )
        self.btn_start.draw(self.screen, self.f_card)

    def _start_simulation(self):
        stops_val = int(self.setup_sliders[0].val)
        couriers_val = int(self.setup_sliders[1].val)
        pop_val = int(self.setup_sliders[2].val)
        self.gens = int(self.setup_sliders[3].val)
        mut_val = self.setup_sliders[4].val
        depot, stops = clustered_map(stops_val, max(1, stops_val // 10), seed=np.random.randint(10000))
        self.ga = GA(depot, stops, n_couriers=couriers_val, pop_size=pop_val, mut_p=mut_val)
        self.mut_slider.val = mut_val
        self.state = "EVOLVE"
        self.paused = False
        self.frame = 0

    # ----- frames -----------------------------------------------------------
    def _evolve_frame(self, advance=True):
        if advance:
            started = time.time()
            steps = int(self.speed_slider.val)
            for _ in range(steps):
                if self.ga.gen >= self.gens:
                    break
                self.ga.step()
                if self.ga.gen % self.race_every == 0:
                    break
                if time.time() - started > 0.03:
                    break

        self._draw_background()
        self._draw_world()
        if self.show_best:
            self._routes_of(self.ga.best, 170, width=4)
        self._draw_sidebar()
        if self.ga.gen % self.race_every == 0 or self.ga.gen >= self.gens:
            self.race = Race(self.ga.top_distinct(self.top_n), self.ga.depot, self.ga.stops, self.ga.k)
            self.state = "RACE"

    def _race_frame(self, dt):
        done = False if self.paused else self.race.update(dt, self.ga.stops)
        self._draw_background()
        self._draw_world(self.race.flash)
        self.trail_overlay.fill((0, 0, 0, 0))
        distance = self.race.t * self.race.speed
        for truck in self.race.trucks:
            point, _, idx = truck.pos_and_dir(distance)
            pts = [self._sc(p) for p in truck.pts[:idx]] + [self._sc(point)]
            if len(pts) > 1:
                pygame.draw.lines(self.trail_overlay, (*truck.color, 150), False, pts, 4)
        self.screen.blit(self.trail_overlay, (0, 0))
        for truck in self.race.trucks:
            point, direction, _ = truck.pos_and_dir(distance)
            car_surf = self.get_car_sprite(truck.sprite_name, direction)
            self.screen.blit(car_surf, car_surf.get_rect(center=self._sc(point)))
        self._draw_sidebar()
        if done:
            self.hold += dt
            if self.hold > 1.4:
                self.hold = 0.0
                self.state = "END" if self.ga.gen >= self.gens else "EVOLVE"

    def _end_frame(self):
        self._draw_background()
        self._draw_world()
        self._routes_of(self.ga.best, 230, width=5)
        self._draw_sidebar()

    def run(self, max_frames=None, shots=None):
        shots = shots or {}
        running = True
        sx = self.W / self.win_w
        sy = self.H / self.win_h
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                # Map window-space mouse coords back to design-space.
                if hasattr(event, "pos"):
                    event.pos = (int(event.pos[0] * sx), int(event.pos[1] * sy))
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_b:
                        self.show_best = not self.show_best
                    elif event.key == pygame.K_s:
                        path = os.path.join(self.out_dir, f"shot_gen{self.ga.gen}.png")
                        pygame.image.save(self.screen, path)

                if self.state == "SETUP":
                    for slider in self.setup_sliders:
                        slider.handle_event(event)
                    if self.btn_start.handle_event(event):
                        self._start_simulation()
                else:
                    if self.mut_slider.handle_event(event):
                        self.ga.mut_p = self.mut_slider.val
                    self.speed_slider.handle_event(event)
                    if self.btn_stop.handle_event(event):
                        self.state = "SETUP"

            if self.state == "SETUP":
                self._draw_setup_frame()
            elif self.state == "EVOLVE":
                self._evolve_frame(advance=not self.paused)
            elif self.state == "RACE":
                self._race_frame(dt)
            elif self.state == "END":
                self._end_frame()

            if self.screen is not self.window:
                pygame.transform.smoothscale(self.screen, (self.win_w, self.win_h), self.window)
            pygame.display.flip()
            self.frame += 1
            if self.frame in shots:
                pygame.image.save(self.screen, shots[self.frame])
            if max_frames and self.frame >= max_frames:
                running = False
        pygame.quit()
