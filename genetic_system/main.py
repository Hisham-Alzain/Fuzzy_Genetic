"""Silly Little Delivery Guys — entry point.

Examples:
    python main.py                            # 100 stops, 5 couriers, race UI
    python main.py --sanity                   # obvious-answer validation map
    python main.py --headless --gens 1500     # no UI: log + plots + baselines
    python main.py --pop 400 --mut 0.3 --seed 7 --race-every 150
"""

import argparse
import os
import numpy as np


def parse():
    p = argparse.ArgumentParser(description="Courier GA (mVRP) with race-mode "
                                            "pygame visualization")
    p.add_argument("--stops", type=int, default=100)
    p.add_argument("--clusters", type=int, default=5)
    p.add_argument("--couriers", type=int, default=5)
    p.add_argument("--pop", type=int, default=300)
    p.add_argument("--gens", type=int, default=1500)
    p.add_argument("--mut", type=float, default=0.3,
                   help="per-child, per-operator mutation probability")
    p.add_argument("--tour-k", type=int, default=4)
    p.add_argument("--elites", type=int, default=3)
    p.add_argument("--w-dist", type=float, default=0.01,
                   help="total-distance tiebreaker weight in fitness")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--race-every", type=int, default=100)
    p.add_argument("--top", type=int, default=5,
                   help="how many children race (color families)")
    p.add_argument("--credit", choices=["on", "off"], default="on",
                   help="crossover-credit breeder elitism")
    p.add_argument("--sanity", action="store_true",
                   help="use the hand-made obvious-answer map")
    p.add_argument("--headless", action="store_true",
                   help="no pygame: print log, save plots, compare baselines")
    p.add_argument("--out", default=".", help="output dir for plots/screenshots")
    # hidden: automated capture for testing
    p.add_argument("--_max-frames", type=int, default=None,
                   help=argparse.SUPPRESS)
    p.add_argument("--_shots", default="", help=argparse.SUPPRESS)
    return p.parse_args()


def main():
    args = parse()
    from map import clustered_map, sanity_map
    from ga import GA

    if args.sanity:
        depot, stops = sanity_map(args.couriers, args.stops // args.couriers,
                                  seed=args.seed)
    else:
        depot, stops = clustered_map(args.stops, args.clusters, seed=args.seed)

    ga = GA(depot, stops, n_couriers=args.couriers, pop_size=args.pop,
            tour_k=args.tour_k, mut_p=args.mut, elites=args.elites,
            w_dist=args.w_dist, seed=args.seed,
            credit_on=(args.credit == "on"))

    os.makedirs(args.out, exist_ok=True)

    if args.headless:
        from baselines import random_solution, greedy_solution
        _, _, mk_r, _ = random_solution(depot, stops, args.couriers,
                                        seed=args.seed)
        _, _, mk_g, _ = greedy_solution(depot, stops, args.couriers,
                                        seed=args.seed)
        print(f"baselines  random {mk_r:,.0f}   greedy {mk_g:,.0f}")
        conv_gen = 0
        best_seen = np.inf
        for g in range(args.gens):
            bf, af, bm = ga.step()
            if bm < best_seen - 1e-9:
                best_seen, conv_gen = bm, g
            if g % max(1, args.gens // 15) == 0 or g == args.gens - 1:
                print(f"gen {g:5d}  best_makespan {bm:9,.1f}  "
                      f"best_fit {bf:.6f}  avg_fit {af:.6f}")
        b = ga.best
        print(f"\nGA best makespan {b.makespan:,.1f}  "
              f"(random {mk_r:,.0f} / greedy {mk_g:,.0f})")
        print(f"route lengths: {np.round(b.lengths, 1)}")
        print(f"last improvement at generation {conv_gen}")
        # plots
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        h = np.array(ga.history)
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(h[:, 0], label="best fitness", color="#1D9E75")
        ax.plot(h[:, 1], label="avg fitness", color="#888", ls="--")
        ax.set_xlabel("generation"); ax.set_ylabel("fitness")
        ax.set_title("fitness vs generation"); ax.legend(); fig.tight_layout()
        fig.savefig(os.path.join(args.out, "fitness.png"), dpi=130)
        from map import decode
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#e67e22", "#9b59b6",
                  "#1abc9c", "#f1c40f"]
        for c, r in enumerate(decode(b.assign, b.order, args.couriers)):
            pts = np.vstack([depot, stops[r], depot])
            ax.plot(pts[:, 0], pts[:, 1], "-", color=colors[c % 7], lw=1.2)
            ax.plot(stops[r][:, 0], stops[r][:, 1], "o",
                    color=colors[c % 7], ms=4)
        ax.plot(*depot, "ks", ms=9)
        ax.set_title(f"best solution — makespan {b.makespan:,.0f}")
        ax.set_aspect("equal"); fig.tight_layout()
        fig.savefig(os.path.join(args.out, "best_routes.png"), dpi=130)
        print(f"saved fitness.png and best_routes.png to {args.out}")
        return

    from viz import App
    shots = {}
    if args._shots:
        for part in args._shots.split(","):
            fr, path = part.split(":")
            shots[int(fr)] = path
    App(ga, args.gens, race_every=args.race_every, top_n=args.top,
        out_dir=args.out).run(max_frames=args._max_frames, shots=shots)


if __name__ == "__main__":
    main()
