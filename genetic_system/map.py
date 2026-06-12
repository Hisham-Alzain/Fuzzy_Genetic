"""Map generation + chromosome decode/measure for the courier GA.

A "map" is: depot position + array of stop positions, shape (n_stops, 2).
A "chromosome" is two genes:
    assignment : int array (n_stops,) with values in {0..n_couriers-1}
    order      : permutation of range(n_stops) — the global visit sequence
"""

import numpy as np

WORLD = 1000.0  # map is a WORLD x WORLD square


# ---------------------------------------------------------------- maps

def clustered_map(n_stops=100, n_clusters=6, seed=0, spread=70.0):
    """Stops drawn from Gaussian clusters; depot at center."""
    rng = np.random.default_rng(seed)
    centers = rng.uniform(0.15 * WORLD, 0.85 * WORLD, size=(n_clusters, 2))
    which = rng.integers(0, n_clusters, size=n_stops)
    stops = centers[which] + rng.normal(0, spread, size=(n_stops, 2))
    stops = np.clip(stops, 0.02 * WORLD, 0.98 * WORLD)
    depot = np.array([WORLD / 2, WORLD / 2])
    return depot, stops


def sanity_map(n_couriers=5, per_cluster=20, seed=0, spread=25.0):
    """Hand-made validation map: n_couriers tight clusters, evenly spaced on a
    circle around the depot. Obvious best answer: one courier per cluster."""
    rng = np.random.default_rng(seed)
    depot = np.array([WORLD / 2, WORLD / 2])
    angles = np.linspace(0, 2 * np.pi, n_couriers, endpoint=False)
    radius = 0.35 * WORLD
    centers = depot + radius * np.stack([np.cos(angles), np.sin(angles)], axis=1)
    stops = np.concatenate([
        c + rng.normal(0, spread, size=(per_cluster, 2)) for c in centers
    ])
    return depot, np.clip(stops, 0.02 * WORLD, 0.98 * WORLD)


# ---------------------------------------------------------------- decode / measure

def decode(assignment, order, n_couriers):
    """Chromosome -> list of routes. Route c = the stop indices owned by
    courier c, in the order they appear in the order gene."""
    owner_in_seq = assignment[order]          # owner of each stop, in visit order
    return [order[owner_in_seq == c] for c in range(n_couriers)]


def route_length(route, depot, stops):
    """Distance of depot -> stops along route -> depot. Empty route = 0."""
    if len(route) == 0:
        return 0.0
    pts = np.vstack([depot, stops[route], depot])
    return float(np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1)).sum())


def measure(assignment, order, depot, stops, n_couriers):
    """Returns (makespan, total_distance, per-route lengths)."""
    routes = decode(assignment, order, n_couriers)
    lengths = np.array([route_length(r, depot, stops) for r in routes])
    return float(lengths.max()), float(lengths.sum()), lengths


def fitness(assignment, order, depot, stops, n_couriers, w_dist=0.01):
    makespan, total, _ = measure(assignment, order, depot, stops, n_couriers)
    return 1.0 / (makespan + w_dist * total)


# ---------------------------------------------------------------- toy verification

if __name__ == "__main__":
    # 6-stop / 2-courier toy case, hand-checkable.
    depot = np.array([0.0, 0.0])
    stops = np.array([
        [10.0, 0.0],   # 0
        [20.0, 0.0],   # 1
        [30.0, 0.0],   # 2
        [0.0, 10.0],   # 3
        [0.0, 20.0],   # 4
        [0.0, 30.0],   # 5
    ])
    # courier 0 owns the x-axis stops, courier 1 the y-axis stops
    assignment = np.array([0, 0, 0, 1, 1, 1])
    # visit order: 0,1,2 then 3,4,5 (each courier sweeps outward)
    order = np.array([0, 1, 2, 3, 4, 5])

    routes = decode(assignment, order, 2)
    print("routes:", [r.tolist() for r in routes])
    # expected: each route = 10+10+10 out + 30 back = 60
    mk, tot, lens = measure(assignment, order, depot, stops, 2)
    print(f"lengths={lens.tolist()}  makespan={mk}  total={tot}")
    assert lens.tolist() == [60.0, 60.0], "hand-computed lengths wrong"

    # scramble the order gene: courier 0 visits 2,0,1 -> 30 + 20 + 10 + 20 = 80
    order2 = np.array([2, 0, 1, 3, 4, 5])
    mk2, tot2, lens2 = measure(assignment, order2, depot, stops, 2)
    print(f"scrambled courier-0 length={lens2[0]} (expect 80.0)")
    assert lens2[0] == 80.0

    # bad assignment: courier 0 owns everything -> courier 1 length 0
    assignment3 = np.zeros(6, dtype=int)
    mk3, tot3, lens3 = measure(assignment3, order, depot, stops, 2)
    print(f"all-on-one: lengths={lens3.tolist()}  makespan={mk3}")
    assert lens3[1] == 0.0 and mk3 > mk

    f_good = fitness(assignment, order, depot, stops, 2)
    f_bad = fitness(assignment3, order, depot, stops, 2)
    print(f"fitness good={f_good:.6f}  bad={f_bad:.6f}")
    assert f_good > f_bad

    print("\nALL TOY CHECKS PASSED")
