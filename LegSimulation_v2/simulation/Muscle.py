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
    def add_muscle_pin_joint(space, self_body: Body, other_body: Body,
                             how_far_from_muscle_position: tuple[float, float],
                             how_far_from_body: tuple[float, float]):
        muscle_pin_joint = pymunk.PinJoint(self_body, other_body, how_far_from_muscle_position, how_far_from_body)
        space.add(muscle_pin_joint)

    def add_muscle_limit_slide_joint(self, space: pymunk.Space(), body1: Body, body2: Body,
                                     how_far_from_body1: tuple[float, float], how_far_from_body2: tuple[float, float],
                                     min_distance: float, max_distance: float):
        body_limit_slide_joint = pymunk.SlideJoint(body1, body2, how_far_from_body1, how_far_from_body2, min_distance,
                                                   max_distance)
        space.add(body_limit_slide_joint)
        return body_limit_slide_joint

    def shorten(self, new_size: Vec2d):
        size = self.size.__sub__(new_size)
        x = size.x
        y = size.y
        self.convert_size = (x, y)
        self.body = pymunk.Body(self.mass, self.moment)
        self.shape = pymunk.Poly.create_box(self.body, self.convert_size)

        return self.body, self.shape

    def update(self, space: pymunk.Space()):
        pass
