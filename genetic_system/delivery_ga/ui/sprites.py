"""Sprite loaders for pre-rendered UI assets."""

from delivery_ga.ui.assets import load_image


def load_truck_sprite(name):
    return load_image(name)


def load_house_sprite():
    return load_image("house.png")


def load_depot_sprite():
    return load_image("depot.png")
