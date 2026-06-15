"""Selection, crossover, and mutation operators."""

import numpy as np


def tournament(population, k, rng):
    picks = rng.choice(len(population), size=k, replace=False)
    return population[max(picks, key=lambda idx: population[idx].fitness)]


def uniform_crossover(assign_a, assign_b, rng):
    mask = rng.random(len(assign_a)) < 0.5
    return np.where(mask, assign_a, assign_b)


def order_crossover(order_a, order_b, rng):
    n = len(order_a)
    i, j = sorted(rng.choice(n + 1, size=2, replace=False))
    child = np.full(n, -1)
    child[i:j] = order_a[i:j]
    used = np.zeros(n, dtype=bool)
    used[order_a[i:j]] = True
    fill = order_b[~used[order_b]]
    child[:i] = fill[:i]
    child[j:] = fill[i:]
    return child


def mutate_assign(assign, n_couriers, rng):
    stop_idx = rng.integers(len(assign))
    choices = [courier for courier in range(n_couriers) if courier != assign[stop_idx]]
    assign[stop_idx] = rng.choice(choices)


def mutate_relocate(individual, stops, rng):
    n = len(individual.assign)
    stop_idx = rng.integers(n)
    distances = np.linalg.norm(stops - stops[stop_idx], axis=1)
    distances[stop_idx] = np.inf
    target = int(rng.choice(np.argsort(distances)[:5]))
    individual.assign[stop_idx] = individual.assign[target]
    order = individual.order[individual.order != stop_idx]
    target_pos = int(np.where(order == target)[0][0])
    individual.order = np.insert(order, target_pos + 1, stop_idx)


def mutate_order(order, rng, max_rev=20):
    n = len(order)
    if rng.random() < 0.5:
        i, j = rng.choice(n, size=2, replace=False)
        order[i], order[j] = order[j], order[i]
        return
    length = rng.integers(2, max_rev + 1)
    i = rng.integers(0, n - length + 1)
    order[i:i + length] = order[i:i + length][::-1]

