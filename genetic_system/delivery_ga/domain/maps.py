"""Map generation helpers for the courier routing problem."""

import numpy as np

WORLD = 1000.0


def scattered_map(n_stops=100, seed=0, margin=0.05, jitter=0.6):
    """Stops spread evenly across the world via a jittered grid.

    Gives normalized, even coverage with a roughly uniform minimum spacing (no
    tight clumps or overlapping nodes), then jitters each point inside its cell
    so it doesn't look like a rigid grid. Depot sits at the center.
    """
    rng = np.random.default_rng(seed)
    lo, hi = margin * WORLD, (1.0 - margin) * WORLD
    cols = int(np.ceil(np.sqrt(n_stops)))
    rows = int(np.ceil(n_stops / cols))
    xs = np.linspace(lo, hi, cols)
    ys = np.linspace(lo, hi, rows)
    cell_w = (hi - lo) / max(1, cols - 1)
    cell_h = (hi - lo) / max(1, rows - 1)
    cells = np.array([(x, y) for y in ys for x in xs], dtype=float)
    rng.shuffle(cells)
    pts = cells[:n_stops]
    pts[:, 0] += rng.uniform(-0.5, 0.5, len(pts)) * cell_w * jitter
    pts[:, 1] += rng.uniform(-0.5, 0.5, len(pts)) * cell_h * jitter
    pts = np.clip(pts, 0.02 * WORLD, 0.98 * WORLD)
    depot = np.array([WORLD / 2, WORLD / 2])
    return depot, pts


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
    """Validation map with one obvious cluster per courier."""
    rng = np.random.default_rng(seed)
    depot = np.array([WORLD / 2, WORLD / 2])
    angles = np.linspace(0, 2 * np.pi, n_couriers, endpoint=False)
    radius = 0.35 * WORLD
    centers = depot + radius * np.stack([np.cos(angles), np.sin(angles)], axis=1)
    stops = np.concatenate([
        center + rng.normal(0, spread, size=(per_cluster, 2))
        for center in centers
    ])
    return depot, np.clip(stops, 0.02 * WORLD, 0.98 * WORLD)

