"""Race-mode animation helpers.

The race animates the single best solution: one truck per courier driving its
route. The number of trucks on screen equals the courier count, and each truck
is colored to match its "Courier Load" bar (courier_hue) so the map and the
sidebar read as one picture.
"""

import numpy as np

from delivery_ga.domain.routing import decode
from delivery_ga.ui.theme import courier_hue, truck_sprite_name


class Truck:
    def __init__(self, pts, color, sprite_name):
        self.pts = pts
        seg = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
        self.cum = np.concatenate([[0.0], np.cumsum(seg)])
        self.total = float(self.cum[-1])
        self.color = color
        self.sprite_name = sprite_name

    def pos_and_dir(self, dist):
        d = min(dist, self.total)
        if self.total == 0:
            return self.pts[0], np.array([1.0, 0.0]), 1
        idx = int(np.searchsorted(self.cum, d, side="right"))
        idx = min(max(idx, 1), len(self.pts) - 1)
        a, b = self.pts[idx - 1], self.pts[idx]
        seg = self.cum[idx] - self.cum[idx - 1]
        fraction = 0.0 if seg == 0 else (d - self.cum[idx - 1]) / seg
        direction = b - a
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm
        else:
            direction = np.array([1.0, 0.0])
        return a + direction * (fraction * norm), direction, idx


class Race:
    def __init__(self, individual, depot, stops, n_couriers, duration=8.0):
        self.trucks = []
        self.finish = []
        self.names = []
        routes = decode(individual.assign, individual.order, n_couriers)
        for courier_idx, route in enumerate(routes):
            if len(route):
                pts = np.vstack([depot, stops[route], depot])
            else:
                pts = np.vstack([depot, depot])
            self.trucks.append(
                Truck(
                    pts,
                    courier_hue(courier_idx),
                    truck_sprite_name(courier_idx, 2),  # base-shade family color
                )
            )

        worst = max((truck.total for truck in self.trucks), default=1.0) or 1.0
        self.speed = worst / duration
        for courier_idx, truck in enumerate(self.trucks):
            self.finish.append(truck.total / self.speed)
            self.names.append(
                (f"courier {courier_idx + 1}", courier_hue(courier_idx), truck.total)
            )

        self.t = 0.0
        self.done_order = []
        self.visited = np.zeros(len(stops), dtype=bool)
        self.flash = np.zeros(len(stops))

    def update(self, dt, stops):
        self.t += dt
        distance = self.t * self.speed
        positions = [truck.pos_and_dir(distance)[0] for truck in self.trucks]
        for pos in positions:
            near = np.linalg.norm(stops - pos, axis=1) < 14
            newly = near & ~self.visited
            self.visited |= near
            self.flash[newly] = 1.0
        self.flash *= 0.92
        for courier_idx, finish_time in enumerate(self.finish):
            if self.t >= finish_time and courier_idx not in self.done_order:
                self.done_order.append(courier_idx)
        return len(self.done_order) == len(self.finish)
