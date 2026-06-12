"""Baselines the GA must beat (Requirement 7).

random_solution : random assignment + random order (the floor)
greedy_solution : k-means-ish nearest-centroid assignment, then each route
                  ordered by nearest-neighbour (a sane human-ish heuristic)
"""

import numpy as np
from map import measure


def random_solution(depot, stops, k, seed=0):
    rng = np.random.default_rng(seed)
    assign = rng.integers(0, k, size=len(stops))
    order = rng.permutation(len(stops))
    mk, tot, lens = measure(assign, order, depot, stops, k)
    return assign, order, mk, tot


def greedy_solution(depot, stops, k, iters=20, seed=0):
    rng = np.random.default_rng(seed)
    n = len(stops)
    # balanced k-means-style centroids -> assignment
    centroids = stops[rng.choice(n, size=k, replace=False)].astype(float)
    for _ in range(iters):
        d = np.linalg.norm(stops[:, None, :] - centroids[None, :, :], axis=2)
        assign = d.argmin(axis=1)
        for c in range(k):
            mine = stops[assign == c]
            if len(mine):
                centroids[c] = mine.mean(axis=0)
    # nearest-neighbour order within each courier, concatenated into one
    # global permutation (so it's comparable to a GA chromosome)
    order = []
    for c in range(k):
        idx = list(np.where(assign == c)[0])
        cur = depot
        while idx:
            j = min(range(len(idx)),
                    key=lambda t: np.linalg.norm(stops[idx[t]] - cur))
            nxt = idx.pop(j)
            order.append(nxt)
            cur = stops[nxt]
    order = np.array(order)
    mk, tot, lens = measure(assign, order, depot, stops, k)
    return assign, order, mk, tot
