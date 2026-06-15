import os
import math
import time
import numpy as np
import pygame
import pygame.gfxdraw as gfx

# Game-like Palette
BG      = (240, 245, 250)      # Outer background
PANEL   = (255, 255, 255)      # UI panel
PANEL2  = (245, 248, 250)      # UI elements
MAP_BG  = (160, 210, 160)      # Grass green for the map area
TXT     = (40, 45, 50)
MUT     = (100, 110, 120)
DIM     = (180, 190, 200)

FAMILIES = [(230, 60, 80), (40, 140, 240), (40, 200, 80),
            (250, 180, 40), (140, 70, 210)]
SHADE_F = [0.4, 0.2, 0.0, -0.2, -0.4]

def shade(col, f):
    if f >= 0:
        return tuple(int(c + (255 - c) * f) for c in col)
    return tuple(int(max(0, c * (1 + f))) for c in col)

def courier_color(child_i, courier_i):
    return shade(FAMILIES[child_i % len(FAMILIES)], SHADE_F[courier_i % 5])

# -- High Quality Sprite Generators --
def create_car_sprite(color):
    # Supersampling 4x for smooth anti-aliasing
    surf = pygame.Surface((160, 80), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.rect(surf, (0, 0, 0, 60), (8, 16, 136, 56), border_radius=16)
    # Tires
    pygame.draw.rect(surf, (30, 30, 30), (24, 0, 24, 16), border_radius=8)
    pygame.draw.rect(surf, (30, 30, 30), (104, 0, 24, 16), border_radius=8)
    pygame.draw.rect(surf, (30, 30, 30), (24, 64, 24, 16), border_radius=8)
    pygame.draw.rect(surf, (30, 30, 30), (104, 64, 24, 16), border_radius=8)
    # Body
    pygame.draw.rect(surf, (245, 245, 250), (8, 8, 136, 64), border_radius=16)
    # Cargo (Color)
    pygame.draw.rect(surf, color, (8, 8, 80, 64), border_radius=16)
    # Cab Roof
    pygame.draw.rect(surf, (255, 255, 255), (96, 16, 32, 48), border_radius=8)
    # Windshield
    pygame.draw.rect(surf, (160, 200, 220), (120, 16, 16, 48), border_radius=4)
    # Headlights
    pygame.draw.circle(surf, (255, 255, 200), (140, 20), 8)
    pygame.draw.circle(surf, (255, 255, 200), (140, 60), 8)
    return pygame.transform.smoothscale(surf, (40, 20))

def create_house_sprite():
    # Supersampling 4x for smooth anti-aliasing
    surf = pygame.Surface((96, 96), pygame.SRCALPHA)
    # Shadow
    pygame.draw.circle(surf, (0, 0, 0, 40), (48, 56), 32)
    # Base
    pygame.draw.rect(surf, (240, 240, 245), (16, 32, 64, 48), border_radius=8)
    # Roof
    pygame.draw.polygon(surf, (220, 90, 90), [(8, 32), (48, 8), (88, 32)])
    # Window
    pygame.draw.rect(surf, (170, 210, 240), (32, 48, 32, 24), border_radius=4)
    return pygame.transform.smoothscale(surf, (24, 24))

def create_depot_sprite():
    # Supersampling 4x for smooth anti-aliasing
    surf = pygame.Surface((192, 192), pygame.SRCALPHA)
    # Shadow
    pygame.draw.rect(surf, (0, 0, 0, 50), (16, 24, 160, 160), border_radius=24)
    # Base
    pygame.draw.rect(surf, (90, 100, 110), (16, 16, 160, 160), border_radius=24)
    pygame.draw.rect(surf, (110, 120, 130), (32, 32, 128, 128), border_radius=16)
    # Bays
    pygame.draw.rect(surf, (60, 65, 70), (48, 48, 40, 96), border_radius=8)
    pygame.draw.rect(surf, (60, 65, 70), (104, 48, 40, 96), border_radius=8)
    return pygame.transform.smoothscale(surf, (48, 48))

# -- UI Components --
class Button:
    def __init__(self, x, y, w, h, text, color=(40, 167, 69)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hovered = False

    def draw(self, screen, font):
        c = shade(self.color, 0.1) if self.hovered else self.color
        # Shadow
        pygame.draw.rect(screen, (0, 0, 0, 40), (self.rect.x, self.rect.y + 4, self.rect.w, self.rect.h), border_radius=8)
        # Button face
        pygame.draw.rect(screen, c, self.rect, border_radius=8)
        txt = font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered: return True
        return False

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, val, label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = val
        self.label = label
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_val(event.pos[0])
                return True
        return False

    def _update_val(self, mx):
        f = max(0.0, min(1.0, (mx - self.rect.x) / self.rect.width))
        self.val = self.min_val + f * (self.max_val - self.min_val)

    def draw(self, screen, font):
        pygame.draw.rect(screen, DIM, self.rect, border_radius=self.rect.height//2)
        f = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * f), self.rect.height)
        if fill_rect.width > 0:
            pygame.draw.rect(screen, FAMILIES[1], fill_rect, border_radius=self.rect.height//2)
        kx = self.rect.x + int(self.rect.width * f)
        pygame.draw.circle(screen, TXT, (kx, self.rect.centery), int(self.rect.height * 0.8))
        text = font.render(f"{self.label}: {self.val:.3f}" if self.max_val <= 1.0 else f"{self.label}: {int(self.val)}", True, TXT)
        screen.blit(text, (self.rect.x, self.rect.y - 20))

# -- Race Engine --
class Truck:
    def __init__(self, pts, color):
        self.pts = pts
        seg = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
        self.cum = np.concatenate([[0.0], np.cumsum(seg)])
        self.total = float(self.cum[-1])
        self.color = color

    def pos_and_dir(self, dist):
        d = min(dist, self.total)
        if self.total == 0:
            return self.pts[0], np.array([1.0, 0.0]), 1
        i = int(np.searchsorted(self.cum, d, side="right"))
        i = min(max(i, 1), len(self.pts) - 1)
        a, b = self.pts[i - 1], self.pts[i]
        seg = self.cum[i] - self.cum[i - 1]
        f = 0.0 if seg == 0 else (d - self.cum[i - 1]) / seg
        direction = b - a
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm
        else:
            direction = np.array([1.0, 0.0])
        return a + direction * (f * norm), direction, i

class Race:
    def __init__(self, inds, depot, stops, k, duration=8.0):
        self.trucks, self.finish, self.names = [], [], []
        from map import decode
        worst = 1.0
        per_child = []
        for ci, ind in enumerate(inds):
            routes = decode(ind.assign, ind.order, k)
            tks = []
            for cc, r in enumerate(routes):
                pts = np.vstack([depot, stops[r], depot]) if len(r) else np.vstack([depot, depot])
                tks.append(Truck(pts, courier_color(ci, cc)))
            per_child.append(tks)
            worst = max(worst, ind.makespan)
        self.speed = worst / duration
        for ci, tks in enumerate(per_child):
            self.trucks.extend(tks)
            self.finish.append(max(t.total for t in tks) / self.speed)
            self.names.append((f"child {ci + 1}", FAMILIES[ci % len(FAMILIES)], inds[ci].makespan))
        self.t = 0.0
        self.done_order = []
        self.visited = np.zeros(len(stops), dtype=bool)
        self.flash = np.zeros(len(stops))

    def update(self, dt, stops):
        self.t += dt
        d = self.t * self.speed
        pts = [t.pos_and_dir(d)[0] for t in self.trucks]
        for p in pts:
            near = np.linalg.norm(stops - p, axis=1) < 14
            newly = near & ~self.visited
            self.visited |= near
            self.flash[newly] = 1.0
        self.flash *= 0.92
        for ci, ft in enumerate(self.finish):
            if self.t >= ft and ci not in self.done_order:
                self.done_order.append(ci)
        return len(self.done_order) == len(self.finish)

class App:
    MAPW = 640

    def __init__(self, ga, gens, race_every=100, top_n=5, title="Courier GA Simulation", out_dir="."):
        self.ga, self.gens = ga, gens
        self.race_every, self.top_n = race_every, top_n
        self.out_dir = out_dir
        pygame.init()
        self.W, self.H = 1100, 660
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption(title)
        
        # High quality system fonts
        self.f14 = pygame.font.SysFont("segoeui,arial", 16)
        self.f12 = pygame.font.SysFont("segoeui,arial", 13)
        self.f20 = pygame.font.SysFont("segoeui,arial", 22, bold=True)
        self.clock = pygame.time.Clock()
        
        self.state = "SETUP"  # We start in the Setup menu now
        self.race = None
        self.hold = 0.0
        self.paused = False
        self.show_best = True
        self.frame = 0
        scale = (self.MAPW - 30) / 1000.0
        self._sc = lambda p: (15 + p[0] * scale, 15 + p[1] * scale)
        
        self.trail_overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.car_cache = {}
        self.house_sprite = create_house_sprite()
        self.depot_sprite = create_depot_sprite()
        
        # Setup Menu Sliders
        cx = self.W // 2 - 150
        cy = self.H // 2 - 140
        self.setup_sliders = [
            Slider(cx, cy, 300, 14, 10, 200, len(self.ga.stops), "Number of Stops"),
            Slider(cx, cy+60, 300, 14, 1, 10, self.ga.k, "Number of Couriers"),
            Slider(cx, cy+120, 300, 14, 20, 1000, len(self.ga.pop), "Population Size"),
            Slider(cx, cy+180, 300, 14, 10, 3000, self.gens, "Max Generations"),
            Slider(cx, cy+240, 300, 14, 0.0, 0.5, self.ga.mut_p, "Mutation Rate"),
        ]
        self.btn_start = Button(self.W // 2 - 125, cy + 300, 250, 45, "START SIMULATION", FAMILIES[2])
        
        # In-game Sliders & Buttons
        self.mut_slider = Slider(self.MAPW + 24, 510, 200, 10, 0.0, 0.5, self.ga.mut_p, "Mutation Rate")
        self.speed_slider = Slider(self.MAPW + 24, 560, 200, 10, 1.0, 200.0, 25.0, "Evolution Speed")
        self.btn_stop = Button(self.MAPW + 24, 600, 200, 40, "PAUSE / CONFIGURE", FAMILIES[0])

    def get_car_sprite(self, color, direction):
        angle = int(math.degrees(math.atan2(-direction[1], direction[0]))) % 360
        key = (color, angle)
        if key not in self.car_cache:
            base = create_car_sprite(color)
            self.car_cache[key] = pygame.transform.rotozoom(base, angle, 1.0)
        return self.car_cache[key]

    def _text(self, s, x, y, font=None, col=TXT):
        self.screen.blit((font or self.f14).render(s, True, col), (x, y))

    def _routes_of(self, ind, alpha, width=4, family=None):
        from map import decode
        self.trail_overlay.fill((0,0,0,0))
        routes = decode(ind.assign, ind.order, self.ga.k)
        for cc, r in enumerate(routes):
            if not len(r): continue
            col = courier_color(family, cc) if family is not None else shade(FAMILIES[cc], 0.0)
            pts = [self._sc(self.ga.depot)] + [self._sc(p) for p in self.ga.stops[r]] + [self._sc(self.ga.depot)]
            if len(pts) > 1:
                pygame.draw.lines(self.trail_overlay, (*col, alpha), False, pts, width)
        self.screen.blit(self.trail_overlay, (0, 0))

    def _draw_map_bg(self):
        self.screen.fill(BG)
        map_rect = pygame.Rect(8, 8, self.MAPW, self.H - 16)
        pygame.draw.rect(self.screen, MAP_BG, map_rect, border_radius=10)
        
        # Subtle grid overlay
        grid_surf = pygame.Surface((self.MAPW, self.H - 16), pygame.SRCALPHA)
        for x in range(0, self.MAPW, 40):
            pygame.draw.line(grid_surf, (255, 255, 255, 30), (x, 0), (x, self.H - 16))
        for y in range(0, self.H - 16, 40):
            pygame.draw.line(grid_surf, (255, 255, 255, 30), (0, y), (self.MAPW, y))
        self.screen.blit(grid_surf, (8, 8))

    def _draw_stops(self, flash=None):
        for i, p in enumerate(self.ga.stops):
            sp = self._sc(p)
            rect = self.house_sprite.get_rect(center=sp)
            self.screen.blit(self.house_sprite, rect)
            if flash is not None and flash[i] > 0.05:
                r = 10 + int(10 * flash[i])
                s = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 150, int(150 * flash[i])), (r*2, r*2), r*2)
                s = pygame.transform.smoothscale(s, (r*2, r*2))
                self.screen.blit(s, (int(sp[0]-r), int(sp[1]-r)))

        dp = self._sc(self.ga.depot)
        rect = self.depot_sprite.get_rect(center=dp)
        self.screen.blit(self.depot_sprite, rect)

    def _side_panel(self):
        x0 = self.MAPW + 18
        pygame.draw.rect(self.screen, PANEL, (x0 - 6, 8, self.W - x0 - 4, self.H - 16), border_radius=10)
        self._text("Delivery Simulation", x0 + 6, 18, self.f20)
        self._text(f"Generation {self.ga.gen} / {self.gens}", x0 + 6, 48, self.f14, MUT)
        
        b = self.ga.best
        self._text(f"Best Makespan: {b.makespan:,.0f}", x0 + 6, 72)
        self._text(f"Best Fitness:  {b.fitness:.6f}", x0 + 6, 94, self.f12, MUT)

        self._text("Child Route Lengths", x0 + 6, 126, self.f12, MUT)
        if b.lengths is not None and b.lengths.max() > 0:
            mx = b.lengths.max()
            for c, L in enumerate(b.lengths):
                y = 146 + c * 22
                col = shade(FAMILIES[0], SHADE_F[c])
                w = int(240 * L / mx)
                pygame.draw.rect(self.screen, col, (x0 + 26, y, w, 9), border_radius=3)
                self._text(str(c + 1), x0 + 8, y - 3, self.f12, col)
                self._text(f"{L:,.0f}", x0 + 274, y - 3, self.f12, MUT)

        bx, by, bw, bh = x0 + 6, 276, self.W - x0 - 24, 110
        pygame.draw.rect(self.screen, PANEL2, (bx, by, bw, bh), border_radius=6)
        h = self.ga.history
        if len(h) > 2:
            hist = np.array(h[-2000:])
            top = hist[:, 0].max()
            for col_i, colr in ((1, DIM), (0, (40, 167, 69))):
                ys = hist[:, col_i] / top
                pts = [(bx + 4 + i * (bw - 8) / (len(ys) - 1), by + bh - 6 - y * (bh - 12)) for i, y in enumerate(ys)]
                if len(pts) > 1:
                    pygame.draw.aalines(self.screen, colr, False, pts)
        self._text("Fitness: Best / Avg", bx + 6, by + bh + 6, self.f12, DIM)

        self.mut_slider.draw(self.screen, self.f12)
        self.speed_slider.draw(self.screen, self.f12)
        self.btn_stop.draw(self.screen, self.f14)
        return x0

    def _setup_frame(self):
        self._draw_map_bg()
        self._draw_stops()

        # Dark overlay
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Menu Panel
        mw, mh = 400, 450
        mx, my = self.W // 2 - mw // 2, self.H // 2 - mh // 2
        
        # Panel shadow & base
        pygame.draw.rect(self.screen, (0, 0, 0, 80), (mx+4, my+4, mw, mh), border_radius=16)
        pygame.draw.rect(self.screen, PANEL, (mx, my, mw, mh), border_radius=16)
        
        self._text("SIMULATION SETUP", mx + 110, my + 30, self.f20)

        for sl in self.setup_sliders:
            sl.draw(self.screen, self.f14)

        self.btn_start.draw(self.screen, self.f14)

    def _start_simulation(self):
        stops_val = int(self.setup_sliders[0].val)
        couriers_val = int(self.setup_sliders[1].val)
        pop_val = int(self.setup_sliders[2].val)
        self.gens = int(self.setup_sliders[3].val)
        mut_val = self.setup_sliders[4].val

        from map import clustered_map
        from ga import GA
        
        # Regenerate Map and GA
        depot, stops = clustered_map(stops_val, max(1, stops_val//10), seed=np.random.randint(10000))
        self.ga = GA(depot, stops, n_couriers=couriers_val, pop_size=pop_val, mut_p=mut_val)
        
        self.mut_slider.val = mut_val
        self.state = "EVOLVE"
        self.paused = False
        self.frame = 0

    def _evolve_frame(self):
        t0 = time.time()
        steps = int(self.speed_slider.val)
        for _ in range(steps):
            if self.ga.gen >= self.gens: break
            self.ga.step()
            if self.ga.gen % self.race_every == 0: break
            if time.time() - t0 > 0.03:
                break

        self._draw_map_bg()
        if self.show_best:
            b = self.ga.best
            self._routes_of(b, 150, width=4, family=0)
        self._draw_stops()
        
        x0 = self._side_panel()
        self._text("Evolving...", x0 + 6, 410, self.f14, MUT)
        self._text(f"Next race at gen {min(((self.ga.gen // self.race_every) + 1) * self.race_every, self.gens)}", x0 + 6, 432, self.f12, DIM)
        if self.ga.gen % self.race_every == 0 or self.ga.gen >= self.gens:
            self.race = Race(self.ga.top_distinct(self.top_n), self.ga.depot, self.ga.stops, self.ga.k)
            self.state = "RACE"

    def _race_frame(self, dt):
        done = False if self.paused else self.race.update(dt, self.ga.stops)
        self._draw_map_bg()

        self.trail_overlay.fill((0,0,0,0))
        d = self.race.t * self.race.speed
        for t in self.race.trucks:
            p, _, i = t.pos_and_dir(d)
            pts = [self._sc(q) for q in t.pts[:i]] + [self._sc(p)]
            if len(pts) > 1:
                pygame.draw.lines(self.trail_overlay, (*t.color, 120), False, pts, 4)
        self.screen.blit(self.trail_overlay, (0, 0))
        
        self._draw_stops(self.race.flash)

        # Draw cars on top
        for t in self.race.trucks:
            p, direction, _ = t.pos_and_dir(d)
            car_surf = self.get_car_sprite(t.color, direction)
            rect = car_surf.get_rect(center=self._sc(p))
            self.screen.blit(car_surf, rect)

        x0 = self._side_panel()
        self._text(f"RACE — Top {self.top_n} Children", x0 + 6, 410, self.f14)
        for rank, ci in enumerate(self.race.done_order):
            name, col, mk = self.race.names[ci]
            self._text(f"{rank + 1}. {name}   {mk:,.0f}", x0 + 16, 434 + rank * 20, self.f12, col)
        self._text("A child finishes when its slowest", x0 + 6, 555, self.f12, DIM)
        self._text("truck returns — Finish Order = Fitness", x0 + 6, 573, self.f12, DIM)
        
        if done:
            self.hold += dt
            if self.hold > 1.4:
                self.hold = 0.0
                self.state = "END" if self.ga.gen >= self.gens else "EVOLVE"

    def _end_frame(self):
        self._draw_map_bg()
        b = self.ga.best
        self._routes_of(b, 220, width=4, family=0)
        self._draw_stops()
        x0 = self._side_panel()
        self._text("DONE — Best Solution Shown", x0 + 6, 410, self.f14)
        self._text("Fitness curve saved to fitness.png", x0 + 6, 432, self.f12, DIM)

    def run(self, max_frames=None, shots=None):
        shots = shots or {}
        saved_plot = False
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
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
                        pygame.image.save(self.screen, os.path.join(self.out_dir, f"shot_gen{self.ga.gen}.png"))

                # Route events based on state
                if self.state == "SETUP":
                    for sl in self.setup_sliders:
                        sl.handle_event(e)
                    if self.btn_start.handle_event(e):
                        self._start_simulation()
                else:
                    if self.mut_slider.handle_event(e):
                        self.ga.mut_p = self.mut_slider.val
                    self.speed_slider.handle_event(e)
                    if self.btn_stop.handle_event(e):
                        self.state = "SETUP"

            if self.state == "SETUP":
                self._setup_frame()
            elif self.state == "EVOLVE" and not self.paused:
                self._evolve_frame()
            elif self.state == "RACE":
                self._race_frame(dt)
            elif self.state == "END":
                self._end_frame()
                if not saved_plot:
                    self._save_plot()
                    saved_plot = True
            
            # Keep setup frame static if paused/setup (no logic loop needed)
            if self.state == "SETUP" or (self.state == "EVOLVE" and self.paused):
                pass 
                
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
        if not len(h): return
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(h[:, 0], label="best fitness", color="#1D9E75")
        ax.plot(h[:, 1], label="avg fitness", color="#888", ls="--")
        ax.set_xlabel("generation"); ax.set_ylabel("fitness")
        ax.set_title("fitness vs generation"); ax.legend(); fig.tight_layout()
        fig.savefig(os.path.join(self.out_dir, "fitness.png"), dpi=130)
        plt.close(fig)