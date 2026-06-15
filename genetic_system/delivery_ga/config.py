"""Configuration for the delivery GA app."""

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    stops: int = 100
    clusters: int = 5
    couriers: int = 5
    pop: int = 300
    gens: int = 1500
    mut: float = 0.3
    tour_k: int = 4
    elites: int = 3
    w_dist: float = 0.01
    seed: int = 0
    race_every: int = 100
    top: int = 5
    credit: str = "on"
    sanity: bool = False
    out: str = "."
    max_frames: int | None = None
    shots: str = ""

