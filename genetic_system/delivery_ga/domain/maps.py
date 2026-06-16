"""Map generation helpers for the courier routing problem."""

import numpy as np

WORLD = 1000.0


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

