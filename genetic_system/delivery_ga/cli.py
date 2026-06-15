"""CLI launcher for the GUI-first delivery GA."""

import argparse
import os

from delivery_ga.config import AppConfig
from delivery_ga.domain.maps import clustered_map, sanity_map
from delivery_ga.engine.ga import GA
from delivery_ga.ui.app import App


def parse_args():
    parser = argparse.ArgumentParser(
        description="Courier GA with a pygame-first visualization"
    )
    parser.add_argument("--stops", type=int, default=100)
    parser.add_argument("--clusters", type=int, default=5)
    parser.add_argument("--couriers", type=int, default=5)
    parser.add_argument("--pop", type=int, default=300)
    parser.add_argument("--gens", type=int, default=1500)
    parser.add_argument("--mut", type=float, default=0.3)
    parser.add_argument("--tour-k", type=int, default=4)
    parser.add_argument("--elites", type=int, default=3)
    parser.add_argument("--w-dist", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--race-every", type=int, default=100)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--credit", choices=["on", "off"], default="on")
    parser.add_argument("--sanity", action="store_true")
    parser.add_argument("--out", default=".")
    parser.add_argument("--_max-frames", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--_shots", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()
    return AppConfig(
        stops=args.stops,
        clusters=args.clusters,
        couriers=args.couriers,
        pop=args.pop,
        gens=args.gens,
        mut=args.mut,
        tour_k=args.tour_k,
        elites=args.elites,
        w_dist=args.w_dist,
        seed=args.seed,
        race_every=args.race_every,
        top=args.top,
        credit=args.credit,
        sanity=args.sanity,
        out=args.out,
        max_frames=args._max_frames,
        shots=args._shots,
    )


def _build_initial_ga(config):
    if config.sanity:
        depot, stops = sanity_map(config.couriers, config.stops // config.couriers, seed=config.seed)
    else:
        depot, stops = clustered_map(config.stops, config.clusters, seed=config.seed)
    return GA(
        depot,
        stops,
        n_couriers=config.couriers,
        pop_size=config.pop,
        tour_k=config.tour_k,
        mut_p=config.mut,
        elites=config.elites,
        w_dist=config.w_dist,
        seed=config.seed,
        credit_on=(config.credit == "on"),
    )


def _parse_shots(raw_value):
    shots = {}
    if not raw_value:
        return shots
    for part in raw_value.split(","):
        frame, path = part.split(":")
        shots[int(frame)] = path
    return shots


def main():
    config = parse_args()
    ga = _build_initial_ga(config)
    os.makedirs(config.out, exist_ok=True)
    app = App(ga, config.gens, race_every=config.race_every, top_n=config.top, out_dir=config.out)
    app.run(max_frames=config.max_frames, shots=_parse_shots(config.shots))


if __name__ == "__main__":
    main()

