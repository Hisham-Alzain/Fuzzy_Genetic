# Silly Little Delivery Guys — Courier GA

A genetic algorithm that splits 100 delivery stops between 5 couriers and
orders each route, minimizing the makespan (the slowest courier's route), with
a Primer-style pygame "race mode" visualization: every k generations the top 5
children race their couriers live — finish order on screen = fitness order.

## Install

    pip install numpy pygame matplotlib

(Python 3.10+. No ML libraries used — GA is pure numpy/random.)

## Run

    python main.py                          # default: 100 stops, 5 couriers, race UI
    python main.py --sanity                 # hand-made obvious-answer validation map
    python main.py --headless --gens 1500   # no UI: log + fitness.png + best_routes.png + baselines
    python main.py --pop 400 --mut 0.3 --seed 7 --race-every 150 --credit off

Keys in the UI: SPACE pause · B toggle best-routes overlay · S screenshot · Q quit.

## Flags

| flag | default | meaning |
|---|---|---|
| --stops / --clusters / --couriers | 100 / 5 / 5 | problem size |
| --pop / --gens | 300 / 1500 | population, fixed generation count |
| --mut | 0.3 | per-child, per-operator mutation probability |
| --tour-k / --elites | 4 / 3 | tournament size, fitness elites |
| --w-dist | 0.01 | total-distance tiebreaker weight in fitness |
| --race-every / --top | 100 / 5 | race frequency, children per race |
| --credit on/off | on | crossover-credit breeder elitism (see below) |
| --sanity | — | 5 tight clusters, obvious answer: 1 courier per cluster |
| --headless | — | print-only run + matplotlib plots + baseline comparison |
| --seed / --out | 0 / . | reproducibility, output directory |

## Design (maps to the assignment requirements)

1. **Problem**: multi-vehicle routing (mVRP, Dantzig & Ramser 1959); minimize
   makespan = max route length, so all deliveries finish as early as possible.
2. **Chromosome — two genes**: `assignment` (int array, stop -> courier,
   value-encoded) and `order` (permutation of all stops, the global visit
   sequence). Decode: courier c visits its owned stops in the order they
   appear in the order gene.
3. **Operators**: tournament selection (k=4); uniform crossover on the
   assignment gene + order crossover (OX, Davis 1985) on the permutation gene;
   mutations per child: random-reset (assignment), swap/reverse (order), and a
   linkage-aware **relocate** that moves a stop in both genes at once
   (reassign to a nearby stop's courier and re-insert beside it in the order)
   — this crosses fitness valleys that single-gene mutations cannot, which is
   the epistasis problem of the two-gene encoding.
4. **Fitness**: `1 / (makespan + 0.01·total_distance)` — makespan dominates;
   the distance term only breaks ties between equally balanced solutions.
5. **Loop**: generational replacement with elitism (top 3) + optional
   crossover-credit breeder elitism: parents whose UN-mutated children beat
   both parents earn credit (decaying ×0.5/gen); the top-2 by credit survive
   regardless of their own fitness — selecting on combining ability
   (progeny-testing analogue) to counter gene linkage. Toggle: `--credit`.
6. **UI**: pygame race mode (color family = child, shade = courier, a child
   finishes when its slowest truck returns), live makespan/bars/fitness
   sparkline, end-of-run matplotlib fitness curve.
7. **Validation**: `--sanity` map is solved exactly (one courier per cluster,
   makespan ≈ theoretical optimum); GA beats both baselines in `baselines.py`
   (random and greedy nearest-centroid + nearest-neighbour). Reference run,
   seed 42, 1500 gens: random 10,883 / greedy 1,906 / **GA 1,697**.

## Files

    map.py        map generators + decode/measure + toy verification (run it: `python map.py`)
    ga.py         GA core: operators, loop, elitism, crossover-credit
    baselines.py  random + greedy baselines
    viz.py        pygame race-mode UI
    main.py       argparse entry point
