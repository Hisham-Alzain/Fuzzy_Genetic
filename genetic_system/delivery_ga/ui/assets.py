"""Helpers for loading pre-rendered UI assets."""

from functools import lru_cache
from pathlib import Path

import pygame


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "ui"


def asset_path(name):
    return ASSET_DIR / name


@lru_cache(maxsize=None)
def load_image(name):
    path = asset_path(name)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing UI asset: {path}. Run tools/generate_ui_assets.py first."
        )
    return pygame.image.load(str(path)).convert_alpha()


@lru_cache(maxsize=None)
def load_scaled(name, width, height):
    return pygame.transform.smoothscale(load_image(name), (width, height))

