from __future__ import annotations
from typing import List
from random import random

import pymunk
from pymunk import Poly, Circle, Vec2d, Body

from LegSimulation_v2.simulation.Location import Location


class LegPartJoint:
    time: int = 0

    name: str
    mass: float
    inner_radius: float = 20
    outer_radius: int
    offset: tuple[float, float] = (0, 0)
    body: pymunk.Body
    moment: float
    shape: Circle
    shape_friction: shape.friction = 0
    shape_color: shape.color = "black"
    position: Location

    def __init__(self, space: pymunk.Space(), name, mass, radius, body_position):
        self.body_rotation_limit = None
        self.body_rotation_center = None
        self.name = name
        self.mass = mass
        self.outer_radius = radius
        self.moment = pymunk.moment_for_circle(mass, self.inner_radius, radius, self.offset)
        self.body = pymunk.Body(mass, self.moment)
        self.body.position = Vec2d(*body_position)
        self.shape = pymunk.Circle(self.body, radius)
        self.position = Location(body_position)
        self.shape.collision_type = 0

        space.add(self.body, self.shape)

    def add_patella(self: LegPartJoint, place, height, width):
        static = pymunk.Segment(self.body, (place, height), (place, -height), width)
        static.collision_type = 1

        return static
