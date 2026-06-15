"""Sprite loaders for pre-rendered UI assets."""

from delivery_ga.ui.assets import load_image, load_scaled


def load_truck_sprite(name):
    return load_image(name)


def load_house_sprite():
    return load_image("house.png")


def load_depot_sprite():
    return load_image("depot.png")


def load_panel_sprite(name, width, height):
    return load_scaled(name, width, height)
