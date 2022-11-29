from __future__ import annotations
from typing import List
from random import random

import pymunk
from pymunk import Poly, Vec2d, Body


class LegPartBone:
    time: int = 0

    """An individual subject in the simulation."""
    id: int
    name: str
    mass: float
    size: tuple[int, int]
    moment: float
    shape: Poly
    shape_friction: float
    shape_color: shape.color = "black"
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
        self.shape.collision_type = 0
        self.shape.friction = 0.61
        self.shape.collision_type = 0

        space.add(self.body, self.shape)

    def add_bone_part(self: LegPartBone, place, height, width):
        static = pymunk.Segment(self.body, (width, place), (-width, place), height)
        static.collision_type = 0
        return static
