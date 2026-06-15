"""Main genetic algorithm loop."""

import numpy as np

from delivery_ga.domain.routing import measure
from delivery_ga.engine.individual import Individual
from delivery_ga.engine.operators import (
    mutate_assign,
    mutate_order,
    mutate_relocate,
    order_crossover,
    tournament,
    uniform_crossover,
)


class GA:
    def __init__(
        self,
        depot,
        stops,
        n_couriers=5,
        pop_size=300,
        tour_k=4,
        mut_p=0.3,
        elites=3,
        w_dist=0.01,
        seed=0,
        credit_on=True,
        breeder_elites=2,
        credit_decay=0.5,
    ):
        self.depot = depot
        self.stops = stops
        self.k = n_couriers
        self.n = len(stops)
        self.pop_size = pop_size
        self.tour_k = tour_k
        self.mut_p = mut_p
        self.elites = elites
        self.w_dist = w_dist
        self.credit_on = credit_on
        self.breeder_elites = breeder_elites
        self.credit_decay = credit_decay
        self.rng = np.random.default_rng(seed)
        self.gen = 0
        self.history = []
        self.pop = [self._random_individual() for _ in range(pop_size)]
        for individual in self.pop:
            self._evaluate(individual)
        self.pop.sort(key=lambda candidate: -candidate.fitness)

    def _random_individual(self):
        return Individual(
            self.rng.integers(0, self.k, size=self.n),
            self.rng.permutation(self.n),
        )

    def _evaluate(self, individual):
        makespan, total_distance, lengths = measure(
            individual.assign, individual.order, self.depot, self.stops, self.k
        )
        individual.makespan = makespan
        individual.lengths = lengths
        individual.fitness = 1.0 / (makespan + self.w_dist * total_distance)

    @property
    def best(self):
        return self.pop[0]

    def top_distinct(self, n):
        out = []
        for individual in self.pop:
            duplicate = any(
                np.array_equal(individual.assign, other.assign)
                and np.array_equal(individual.order, other.order)
                for other in out
            )
            if not duplicate:
                out.append(individual)
            if len(out) == n:
                break
        return out

    def step(self):
        rng = self.rng
        for individual in self.pop:
            individual.credit *= self.credit_decay

        children = []
        records = []
        n_children = self.pop_size - self.elites - (
            self.breeder_elites if self.credit_on else 0
        )
        for _ in range(n_children):
            parent_a = tournament(self.pop, self.tour_k, rng)
            parent_b = tournament(self.pop, self.tour_k, rng)
            child = Individual(
                uniform_crossover(parent_a.assign, parent_b.assign, rng),
                order_crossover(parent_a.order, parent_b.order, rng),
            )
            mutated = False
            if rng.random() < self.mut_p:
                mutate_assign(child.assign, self.k, rng)
                mutated = True
            if rng.random() < self.mut_p:
                mutate_order(child.order, rng)
                mutated = True
            if rng.random() < self.mut_p:
                mutate_relocate(child, self.stops, rng)
                mutated = True
            self._evaluate(child)
            children.append(child)
            records.append((parent_a, parent_b, mutated, child))

        if self.credit_on:
            for parent_a, parent_b, mutated, child in records:
                if mutated:
                    continue
                base = max(parent_a.fitness, parent_b.fitness)
                if child.fitness > base:
                    gain = child.fitness - base
                    parent_a.credit += gain
                    parent_b.credit += gain

        new_population = [self.pop[i].copy() for i in range(self.elites)]
        if self.credit_on:
            chosen = {id(candidate) for candidate in self.pop[:self.elites]}
            breeders = sorted(
                (candidate for candidate in self.pop if id(candidate) not in chosen),
                key=lambda candidate: -candidate.credit,
            )[:self.breeder_elites]
            new_population.extend(breeder.copy() for breeder in breeders)

        new_population.extend(children)
        new_population.sort(key=lambda candidate: -candidate.fitness)
        self.pop = new_population
        self.gen += 1
        avg_fitness = float(np.mean([candidate.fitness for candidate in self.pop]))
        self.history.append((self.best.fitness, avg_fitness, self.best.makespan))
        return self.history[-1]

