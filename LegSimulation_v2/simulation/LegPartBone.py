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
    id: int
    name: str
    mass: float
    size: tuple[int, int]
    moment: float
    shape: Poly
    shape_friction: shape.friction = 1
    shape_color: shape.color = "black"
    part_vector_position: Location
    body: Body

    # helper: LegPartsHelper

    def __init__(self, space: pymunk.Space(), body_id, name, mass, size, vector: Vec2d):
        self.id = body_id
        self.name = name
        self.mass = mass
        self.size = size
        self.moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, self.moment)
        self.body.body_type = pymunk.Body.DYNAMIC
        self.body.position = vector
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.body_rotation_limit = None
        self.body_rotation_center = None
        self.part_vector_position = Location(vector)
        self.shape.collision_type = 0
        self.shape.friction = 0.61

        space.add(self.body, self.shape)

    def get_location(self):
        self.part_vector_position.change_location(self.body.position)
        self.part_vector_position.body_position = self.body.position._get_position()

        pass

    def update(self, position):
        self.part_vector_position = position

    def add_bone_part(self: LegPartBone, place, height, width):
        static = pymunk.Segment(self.body, (width, place), (-width, place), height)
        static.collision_type = 0
        return static
