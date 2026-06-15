"""Chromosome decode and route measurement helpers."""

import numpy as np


def decode(assignment, order, n_couriers):
    """Chromosome -> list of route stop indices per courier."""
    owner_in_seq = assignment[order]
    return [order[owner_in_seq == courier] for courier in range(n_couriers)]


def route_length(route, depot, stops):
    """Distance of depot -> route -> depot."""
    if len(route) == 0:
        return 0.0
    pts = np.vstack([depot, stops[route], depot])
    return float(np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1)).sum())


def measure(assignment, order, depot, stops, n_couriers):
    """Return makespan, total distance, and per-route lengths."""
    routes = decode(assignment, order, n_couriers)
    lengths = np.array([route_length(route, depot, stops) for route in routes])
    return float(lengths.max()), float(lengths.sum()), lengths


def fitness(assignment, order, depot, stops, n_couriers, w_dist=0.01):
    makespan, total, _ = measure(assignment, order, depot, stops, n_couriers)
    return 1.0 / (makespan + w_dist * total)

