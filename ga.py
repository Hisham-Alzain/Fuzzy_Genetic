"""GA core for the courier problem.

Chromosome = two genes (see map.py). Operators:
    selection : tournament (k=4)
    crossover : uniform on assignment gene, OX on order gene
    mutation  : per-child events — random-reset (assignment), swap/reverse (order)
Replacement: generational with fitness elitism + optional crossover-credit
breeder elitism (parents whose UN-mutated children beat both parents survive,
even if their own fitness is poor).
"""

import numpy as np
from map import measure


class Individual:
    __slots__ = ("assign", "order", "fitness", "makespan", "lengths", "credit")

    def __init__(self, assign, order):
        self.assign = assign
        self.order = order
        self.fitness = None
        self.makespan = None
        self.lengths = None
        self.credit = 0.0

    def copy(self):
        c = Individual(self.assign.copy(), self.order.copy())
        c.fitness, c.makespan, c.lengths = self.fitness, self.makespan, self.lengths
        return c


# ---------------------------------------------------------------- operators

def tournament(pop, k, rng):
    """Pick k random individuals, return the fittest (Requirement 3: selection)."""
    picks = rng.choice(len(pop), size=k, replace=False)
    return pop[max(picks, key=lambda i: pop[i].fitness)]


def uniform_crossover(a1, a2, rng):
    """Assignment gene: per-stop coin flip between parents. Always valid."""
    mask = rng.random(len(a1)) < 0.5
    return np.where(mask, a1, a2)


def order_crossover(o1, o2, rng):
    """OX for the permutation gene: copy a random slice from parent 1 in place,
    fill remaining positions left-to-right in parent 2's order, skipping
    duplicates. Always yields a valid permutation."""
    n = len(o1)
    i, j = sorted(rng.choice(n + 1, size=2, replace=False))
    child = np.full(n, -1)
    child[i:j] = o1[i:j]
    used = np.zeros(n, dtype=bool)
    used[o1[i:j]] = True
    fill = o2[~used[o2]]
    child[:i] = fill[:i]
    child[j:] = fill[i:]
    return child


def mutate_assign(assign, n_couriers, rng):
    """Random reset: one stop changes owner."""
    s = rng.integers(len(assign))
    choices = [c for c in range(n_couriers) if c != assign[s]]
    assign[s] = rng.choice(choices)


def mutate_relocate(ind, stops, rng):
    """Linkage-aware mutation: moves a stop in BOTH genes at once.

    Pick a random stop s, find its nearest other stop t; give s to t's
    courier (assignment gene) and re-insert s right after t in the order
    gene. A coordinated move like this can cross fitness valleys that
    single-gene mutations cannot (the epistasis problem)."""
    n = len(ind.assign)
    s = rng.integers(n)
    d = np.linalg.norm(stops - stops[s], axis=1)
    d[s] = np.inf
    t = int(rng.choice(np.argsort(d)[:5]))   # one of the 5 nearest stops
    ind.assign[s] = ind.assign[t]
    order = ind.order[ind.order != s]
    pos_t = int(np.where(order == t)[0][0])
    ind.order = np.insert(order, pos_t + 1, s)


def mutate_order(order, rng, max_rev=20):
    """50/50: swap two positions, or reverse a segment (<= max_rev stops)."""
    n = len(order)
    if rng.random() < 0.5:
        i, j = rng.choice(n, size=2, replace=False)
        order[i], order[j] = order[j], order[i]
    else:
        ln = rng.integers(2, max_rev + 1)
        i = rng.integers(0, n - ln + 1)
        order[i:i + ln] = order[i:i + ln][::-1]


# ---------------------------------------------------------------- the loop

class GA:
    def __init__(self, depot, stops, n_couriers=5, pop_size=300, tour_k=4,
                 mut_p=0.3, elites=3, w_dist=0.01, seed=0,
                 credit_on=True, breeder_elites=2, credit_decay=0.5):
        self.depot, self.stops, self.k = depot, stops, n_couriers
        self.n = len(stops)
        self.pop_size, self.tour_k, self.mut_p = pop_size, tour_k, mut_p
        self.elites, self.w_dist = elites, w_dist
        self.credit_on = credit_on
        self.breeder_elites = breeder_elites
        self.credit_decay = credit_decay
        self.rng = np.random.default_rng(seed)
        self.gen = 0
        self.history = []          # per gen: (best_fit, avg_fit, best_makespan)
        self.pop = [self._random_individual() for _ in range(pop_size)]
        for ind in self.pop:
            self._evaluate(ind)
        self.pop.sort(key=lambda x: -x.fitness)

    # -- helpers -------------------------------------------------------
    def _random_individual(self):
        return Individual(
            self.rng.integers(0, self.k, size=self.n),
            self.rng.permutation(self.n))

    def _evaluate(self, ind):
        mk, tot, lens = measure(ind.assign, ind.order, self.depot,
                                self.stops, self.k)
        ind.makespan, ind.lengths = mk, lens
        ind.fitness = 1.0 / (mk + self.w_dist * tot)

    @property
    def best(self):
        return self.pop[0]

    def top(self, n):
        return self.pop[:n]

    def top_distinct(self, n):
        """Top n individuals with distinct genomes — for the race view, so we
        don't race five elitism-clones of the same solution."""
        out = []
        for ind in self.pop:
            if not any(np.array_equal(ind.assign, o.assign) and
                       np.array_equal(ind.order, o.order) for o in out):
                out.append(ind)
            if len(out) == n:
                break
        return out

    # -- one generation --------------------------------------------------
    def step(self):
        rng = self.rng
        # decay stale breeding credit
        for ind in self.pop:
            ind.credit *= self.credit_decay

        # breed
        children, records = [], []
        n_children = self.pop_size - self.elites - \
            (self.breeder_elites if self.credit_on else 0)
        for _ in range(n_children):
            pa = tournament(self.pop, self.tour_k, rng)
            pb = tournament(self.pop, self.tour_k, rng)
            child = Individual(
                uniform_crossover(pa.assign, pb.assign, rng),
                order_crossover(pa.order, pb.order, rng))
            mutated = False
            if rng.random() < self.mut_p:
                mutate_assign(child.assign, self.k, rng); mutated = True
            if rng.random() < self.mut_p:
                mutate_order(child.order, rng); mutated = True
            if rng.random() < self.mut_p:
                mutate_relocate(child, self.stops, rng); mutated = True
            self._evaluate(child)
            children.append(child)
            records.append((pa, pb, mutated, child))

        # crossover-credit: un-mutated child beat BOTH parents
        # -> the pairing recombined cleanly; both parents earn the improvement
        if self.credit_on:
            for pa, pb, mutated, child in records:
                if not mutated:
                    base = max(pa.fitness, pb.fitness)
                    if child.fitness > base:
                        gain = child.fitness - base
                        pa.credit += gain
                        pb.credit += gain

        # next generation = fitness elites + breeder elites + children
        new = [self.pop[i].copy() for i in range(self.elites)]
        for i in range(self.elites):       # carry credit through the copy
            new[i].credit = self.pop[i].credit
        if self.credit_on:
            chosen = set(id(x) for x in self.pop[:self.elites])
            breeders = sorted((x for x in self.pop if id(x) not in chosen),
                              key=lambda x: -x.credit)[:self.breeder_elites]
            for b in breeders:             # survive on combining ability alone
                nb = b.copy(); nb.credit = b.credit; new.append(nb)
        new.extend(children)
        new.sort(key=lambda x: -x.fitness)
        self.pop = new
        self.gen += 1
        avg = float(np.mean([x.fitness for x in self.pop]))
        self.history.append((self.best.fitness, avg, self.best.makespan))
        return self.history[-1]
