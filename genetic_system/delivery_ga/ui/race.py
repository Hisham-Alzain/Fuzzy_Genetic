"""Race-mode animation helpers."""

import numpy as np

from delivery_ga.domain.routing import decode
from delivery_ga.ui.theme import FAMILIES, courier_color, truck_sprite_name


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
    def __init__(self, individuals, depot, stops, n_couriers, duration=8.0):
        self.trucks = []
        self.finish = []
        self.names = []
        worst = 1.0
        per_child = []
        for child_idx, individual in enumerate(individuals):
            routes = decode(individual.assign, individual.order, n_couriers)
            trucks = []
            for courier_idx, route in enumerate(routes):
                if len(route):
                    pts = np.vstack([depot, stops[route], depot])
                else:
                    pts = np.vstack([depot, depot])
                trucks.append(
                    Truck(
                        pts,
                        courier_color(child_idx, courier_idx),
                        truck_sprite_name(child_idx, courier_idx),
                    )
                )
            per_child.append(trucks)
            worst = max(worst, individual.makespan)
        self.speed = worst / duration
        for child_idx, trucks in enumerate(per_child):
            self.trucks.extend(trucks)
            self.finish.append(max(truck.total for truck in trucks) / self.speed)
            self.names.append(
                (
                    f"child {child_idx + 1}",
                    FAMILIES[child_idx % len(FAMILIES)],
                    individuals[child_idx].makespan,
                )
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
        for child_idx, finish_time in enumerate(self.finish):
            if self.t >= finish_time and child_idx not in self.done_order:
                self.done_order.append(child_idx)
        return len(self.done_order) == len(self.finish)
