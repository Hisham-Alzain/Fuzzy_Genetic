"""Race-mode pygame visualization (Primer / evolution-sim vibe).

The GA evolves in the background; every `race_every` generations the top N
children race their couriers live from the depot. Color family = child,
shade = courier. A child finishes when its SLOWEST truck returns, so the
finish order on screen IS the makespan ranking — fitness made visible.

Keys:  SPACE pause   B toggle best-routes overlay   S screenshot   Q/ESC quit
"""

import os
import numpy as np
import pygame
import pygame.gfxdraw as gfx

BG      = (21, 21, 26)
PANEL   = (31, 31, 38)
PANEL2  = (23, 23, 28)
TXT     = (216, 216, 222)
MUT     = (154, 154, 165)
DIM     = (106, 106, 117)
STOPCOL = (125, 125, 136)
DEPOT   = (240, 240, 240)

FAMILIES = [(231, 76, 60), (52, 152, 219), (46, 204, 113),
            (230, 126, 34), (155, 89, 182)]
SHADE_F = [0.50, 0.25, 0.0, -0.22, -0.42]


def shade(col, f):
    if f >= 0:
        return tuple(int(c + (255 - c) * f) for c in col)
    return tuple(int(c * (1 + f)) for c in col)


def courier_color(child_i, courier_i):
    return shade(FAMILIES[child_i % len(FAMILIES)], SHADE_F[courier_i % 5])


# ---------------------------------------------------------------- race engine

class Truck:
    def __init__(self, pts, color):
        self.pts = pts                       # (m,2) world coords incl. depot ends
        seg = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
        self.cum = np.concatenate([[0.0], np.cumsum(seg)])
        self.total = float(self.cum[-1])
        self.color = color

    def pos(self, dist):
        d = min(dist, self.total)
        if self.total == 0:
            return self.pts[0], 1
        i = int(np.searchsorted(self.cum, d, side="right"))
        i = min(max(i, 1), len(self.pts) - 1)
        a, b = self.pts[i - 1], self.pts[i]
        seg = self.cum[i] - self.cum[i - 1]
        f = 0.0 if seg == 0 else (d - self.cum[i - 1]) / seg
        return a + (b - a) * f, i


class Race:
    """One race between the snapshot top-N individuals."""

    def __init__(self, inds, depot, stops, k, duration=8.0):
        self.trucks, self.finish, self.names = [], [], []
        from map import decode
        worst = 1.0
        per_child = []
        for ci, ind in enumerate(inds):
            routes = decode(ind.assign, ind.order, k)
            tks = []
            for cc, r in enumerate(routes):
                pts = np.vstack([depot, stops[r], depot]) if len(r) else \
                    np.vstack([depot, depot])
                tks.append(Truck(pts, courier_color(ci, cc)))
            per_child.append(tks)
            worst = max(worst, ind.makespan)
        self.speed = worst / duration        # world units / s, normalized per race
        for ci, tks in enumerate(per_child):
            self.trucks.extend(tks)
            self.finish.append(max(t.total for t in tks) / self.speed)
            self.names.append((f"child {ci + 1}", FAMILIES[ci % len(FAMILIES)],
                               inds[ci].makespan))
        self.t = 0.0
        self.done_order = []
        self.visited = np.zeros(len(stops), dtype=bool)
        self.flash = np.zeros(len(stops))

    def update(self, dt, stops):
        self.t += dt
        d = self.t * self.speed
        pts = [t.pos(d)[0] for t in self.trucks]
        for p in pts:                               # stop "pop" on first visit
            near = np.linalg.norm(stops - p, axis=1) < 14
            newly = near & ~self.visited
            self.visited |= near
            self.flash[newly] = 1.0
        self.flash *= 0.92
        for ci, ft in enumerate(self.finish):
            if self.t >= ft and ci not in self.done_order:
                self.done_order.append(ci)
        return len(self.done_order) == len(self.finish)


# ---------------------------------------------------------------- app

class App:
    MAPW = 640

    def __init__(self, ga, gens, race_every=100, top_n=5, title="courier GA",
                 out_dir="."):
        self.ga, self.gens = ga, gens
        self.race_every, self.top_n = race_every, top_n
        self.out_dir = out_dir
        pygame.init()
        self.W, self.H = 1100, 660
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption(title)
        self.f14 = pygame.font.SysFont("dejavusans,arial", 15)
        self.f12 = pygame.font.SysFont("dejavusans,arial", 13)
        self.f20 = pygame.font.SysFont("dejavusans,arial", 20, bold=True)
        self.clock = pygame.time.Clock()
        self.state = "EVOLVE"            # EVOLVE -> RACE -> ... -> END
        self.race = None
        self.hold = 0.0
        self.paused = False
        self.show_best = True
        self.frame = 0
        scale = (self.MAPW - 30) / 1000.0
        self._sc = lambda p: (15 + p[0] * scale, 15 + p[1] * scale)

    # -- drawing helpers ------------------------------------------------
    def _dot(self, p, r, col):
        x, y = int(p[0]), int(p[1])
        gfx.filled_circle(self.screen, x, y, r, col)
        gfx.aacircle(self.screen, x, y, r, col)

    def _text(self, s, x, y, font=None, col=TXT):
        self.screen.blit((font or self.f14).render(s, True, col), (x, y))

    def _routes_of(self, ind, alpha, width=2, family=None):
        from map import decode
        surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        routes = decode(ind.assign, ind.order, self.ga.k)
        for cc, r in enumerate(routes):
            if not len(r):
                continue
            col = courier_color(family, cc) if family is not None else \
                shade(FAMILIES[cc], 0.0)
            pts = [self._sc(self.ga.depot)] + [self._sc(p) for p in
                                               self.ga.stops[r]] + \
                  [self._sc(self.ga.depot)]
            pygame.draw.aalines(surf, (*col, alpha), False, pts)
            if width > 1:
                pygame.draw.lines(surf, (*col, alpha), False, pts, width)
        self.screen.blit(surf, (0, 0))

    # -- panels ----------------------------------------------------------
    def _draw_map_bg(self):
        self.screen.fill(BG)
        pygame.draw.rect(self.screen, PANEL2, (8, 8, self.MAPW, self.H - 16),
                         border_radius=10)

    def _draw_stops(self, colors=None, flash=None):
        for i, p in enumerate(self.ga.stops):
            sp = self._sc(p)
            col = colors[i] if colors is not None else STOPCOL
            r = 4
            if flash is not None and flash[i] > 0.05:
                col = tuple(int(c + (255 - c) * flash[i]) for c in col)
                r = 4 + int(3 * flash[i])
            self._dot(sp, r, col)
        dp = self._sc(self.ga.depot)
        pygame.draw.rect(self.screen, DEPOT,
                         (dp[0] - 6, dp[1] - 6, 12, 12), border_radius=2)

    def _side_panel(self):
        x0 = self.MAPW + 18
        pygame.draw.rect(self.screen, PANEL,
                         (x0 - 6, 8, self.W - x0 - 4, self.H - 16),
                         border_radius=10)
        self._text("Silly little delivery guys", x0 + 6, 18, self.f20)
        self._text(f"generation {self.ga.gen} / {self.gens}", x0 + 6, 48,
                   self.f14, MUT)
        b = self.ga.best
        self._text(f"best makespan  {b.makespan:,.0f}", x0 + 6, 72)
        self._text(f"best fitness   {b.fitness:.6f}", x0 + 6, 94, self.f12, MUT)

        # route-length bars of the current best
        self._text("best child route lengths", x0 + 6, 126, self.f12, MUT)
        if b.lengths is not None and b.lengths.max() > 0:
            mx = b.lengths.max()
            for c, L in enumerate(b.lengths):
                y = 146 + c * 22
                col = shade(FAMILIES[0], SHADE_F[c])
                w = int(240 * L / mx)
                pygame.draw.rect(self.screen, col, (x0 + 26, y, w, 9),
                                 border_radius=3)
                self._text(str(c + 1), x0 + 8, y - 3, self.f12, col)
                self._text(f"{L:,.0f}", x0 + 274, y - 3, self.f12, MUT)

        # fitness sparkline (best solid, avg dim)
        bx, by, bw, bh = x0 + 6, 276, self.W - x0 - 24, 110
        pygame.draw.rect(self.screen, PANEL2, (bx, by, bw, bh), border_radius=6)
        h = self.ga.history
        if len(h) > 2:
            hist = np.array(h[-2000:])
            top = hist[:, 0].max()
            for col_i, colr in ((1, DIM), (0, (29, 158, 117))):
                ys = hist[:, col_i] / top
                pts = [(bx + 4 + i * (bw - 8) / (len(ys) - 1),
                        by + bh - 6 - y * (bh - 12)) for i, y in enumerate(ys)]
                if len(pts) > 1:
                    pygame.draw.aalines(self.screen, colr, False, pts)
        self._text("fitness: best / avg", bx + 6, by + bh + 6, self.f12, DIM)

        return x0

    # -- states -----------------------------------------------------------
    def _evolve_frame(self):
        # run as many generations as fit in ~25 ms, stop at race checkpoints
        import time
        t0 = time.time()
        while time.time() - t0 < 0.025 and self.ga.gen < self.gens:
            self.ga.step()
            if self.ga.gen % self.race_every == 0:
                break
        self._draw_map_bg()
        if self.show_best:
            b = self.ga.best
            cols = [shade(FAMILIES[0], SHADE_F[c]) for c in b.assign]
            self._routes_of(b, 150, width=2, family=0)
            self._draw_stops(cols)
        else:
            self._draw_stops()
        x0 = self._side_panel()
        self._text("evolving…", x0 + 6, 410, self.f14, MUT)
        self._text(f"next race at gen "
                   f"{min(((self.ga.gen // self.race_every) + 1) * self.race_every, self.gens)}",
                   x0 + 6, 432, self.f12, DIM)
        if self.ga.gen % self.race_every == 0 or self.ga.gen >= self.gens:
            self.race = Race(self.ga.top_distinct(self.top_n), self.ga.depot,
                             self.ga.stops, self.ga.k)
            self.state = "RACE"

    def _race_frame(self, dt):
        done = False if self.paused else \
            self.race.update(dt, self.ga.stops)
        self._draw_map_bg()
        # trails + trucks
        d = self.race.t * self.race.speed
        surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        for t in self.race.trucks:
            p, i = t.pos(d)
            pts = [self._sc(q) for q in t.pts[:i]] + [self._sc(p)]
            if len(pts) > 1:
                pygame.draw.aalines(surf, (*t.color, 70), False, pts)
        self.screen.blit(surf, (0, 0))
        cols = [STOPCOL] * len(self.ga.stops)
        self._draw_stops(cols, self.race.flash)
        for t in self.race.trucks:
            p, _ = t.pos(d)
            self._dot(self._sc(p), 5, t.color)

        x0 = self._side_panel()
        self._text(f"RACE — top {self.top_n} children", x0 + 6, 410, self.f14)
        for rank, ci in enumerate(self.race.done_order):
            name, col, mk = self.race.names[ci]
            self._text(f"{rank + 1}. {name}   {mk:,.0f}", x0 + 16,
                       434 + rank * 20, self.f12, col)
        nxt = len(self.race.done_order)
        self._text("a child finishes when its slowest", x0 + 6, 560, self.f12,
                   DIM)
        self._text("truck returns — finish order = fitness", x0 + 6, 578,
                   self.f12, DIM)
        if done:
            self.hold += dt
            if self.hold > 1.4:
                self.hold = 0.0
                self.state = "END" if self.ga.gen >= self.gens else "EVOLVE"

    def _end_frame(self):
        self._draw_map_bg()
        b = self.ga.best
        cols = [shade(FAMILIES[0], SHADE_F[c]) for c in b.assign]
        self._routes_of(b, 220, width=2, family=0)
        self._draw_stops(cols)
        x0 = self._side_panel()
        self._text("DONE — best solution shown", x0 + 6, 410, self.f14)
        self._text("fitness curve saved to fitness.png", x0 + 6, 432,
                   self.f12, DIM)

    # -- main loop ----------------------------------------------------------
    def run(self, max_frames=None, shots=None):
        shots = shots or {}
        saved_plot = False
        running = True
        while running:
            dt = self.clock.tick(50) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                    elif e.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif e.key == pygame.K_b:
                        self.show_best = not self.show_best
                    elif e.key == pygame.K_s:
                        pygame.image.save(self.screen, os.path.join(
                            self.out_dir, f"shot_gen{self.ga.gen}.png"))

            if self.state == "EVOLVE" and not self.paused:
                self._evolve_frame()
            elif self.state == "RACE":
                self._race_frame(dt)
            elif self.state == "END":
                self._end_frame()
                if not saved_plot:
                    self._save_plot()
                    saved_plot = True
            pygame.display.flip()

            self.frame += 1
            if self.frame in shots:
                pygame.image.save(self.screen, shots[self.frame])
            if max_frames and self.frame >= max_frames:
                running = False
        if not saved_plot:
            self._save_plot()
        pygame.quit()

    def _save_plot(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        h = np.array(self.ga.history)
        if not len(h):
            return
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(h[:, 0], label="best fitness", color="#1D9E75")
        ax.plot(h[:, 1], label="avg fitness", color="#888", ls="--")
        ax.set_xlabel("generation"); ax.set_ylabel("fitness")
        ax.set_title("fitness vs generation"); ax.legend(); fig.tight_layout()
        fig.savefig(os.path.join(self.out_dir, "fitness.png"), dpi=130)
        plt.close(fig)
