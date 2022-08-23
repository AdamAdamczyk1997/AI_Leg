from __future__ import annotations
from typing import List
from random import random

import pymunk
from pymunk import Poly, Vec2d, Body

from LegSimulation_v2.simulation.Location import Location


class Muscle:
    time: int = 0

    """An individual subject in the simulation."""
    name: str
    mass: float
    size: Vec2d
    x: float
    y: float
    convert_size: tuple[float, float]
    moment: float
    body: pymunk.Body
    shape: Poly
    shape_friction: shape.friction = 1
    shape_color: shape.color = "black"
    position: Location

    def __init__(self, space: pymunk.Space(), name, mass, size: Vec2d, vector: Vec2d):
        self.value = None
        self.name = name
        self.mass = mass
        self.size = size
        self.x = self.size.x
        self.y = self.size.y
        self.convert_size = (self.x, self.y)
        self.moment = pymunk.moment_for_box(mass, self.convert_size)
        self.body = pymunk.Body(mass, self.moment)
        self.body.position = vector
        self.shape = pymunk.Poly.create_box(self.body, self.convert_size)
        self.body_rotation_limit = None
        self.body_rotation_center = None
        self.position = Location(vector)

        space.add(self.body, self.shape)

    @staticmethod
    def add_muscle_pin_joint(space, self_body: Body, other_body: Body, how_far_from_muscle_position: tuple[float, float],
                             how_far_from_body: tuple[float, float]):
        muscle_pin_joint = pymunk.PinJoint(self_body, other_body, how_far_from_muscle_position, how_far_from_body)
        space.add(muscle_pin_joint)

    def shorten(self, space, new_size: Vec2d):
        size = self.size.__sub__(new_size)
        x = size.x
        y = size.y
        self.convert_size = (x, y)
        self.moment = pymunk.moment_for_box(self.mass, self.convert_size)
        self.body = pymunk.Body(self.mass, self.moment)
        self.shape = pymunk.Poly.create_box(self.body, self.convert_size)

        space.add(self.body, self.shape)

        return space

    def update(self, space: pymunk.Space()):
        pass


