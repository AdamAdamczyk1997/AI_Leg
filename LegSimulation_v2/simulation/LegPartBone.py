from __future__ import annotations
from typing import List
from random import random

import pymunk
from pymunk import Poly, Vec2d, Body

from LegSimulation_v2.simulation import LegPartsHelper
from LegSimulation_v2.simulation.Location import Location


class LegPartBone:
    time: int = 0

    """An individual subject in the simulation."""
    name: str
    mass: float
    size: tuple[int, int]
    moment: float
    shape: Poly
    shape_friction: shape.friction = 1
    shape_color: shape.color = "black"
    position: Location
    # helper: LegPartsHelper

    def __init__(self, space: pymunk.Space(), name, mass, size, vector: Vec2d):
        self.name = name
        self.mass = mass
        self.size = size
        self.moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, self.moment)
        self.body.position = vector
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.body_rotation_limit = None
        self.body_rotation_center = None
        self.position = Location(vector)
        self.shape.collision_type = 0

        space.add(self.body, self.shape)

    # def tick(self, space) -> None:
    #     """Update the state of the simulation by one time step."""

    def get_location(self):
        self.position.change_location(self.body.position)
        self.position.get_current_location()
        pass

    def update(self, position):
        self.position = position

    def add_bone_part(self: LegPartBone, place, height, width):
        static = pymunk.Segment(self.body, (width, place), (-width, place), height)
        static.collision_type = 0

        return static
