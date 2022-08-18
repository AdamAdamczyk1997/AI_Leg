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
    offset: tuple[float, float] = (0, 360)
    body: pymunk.Body
    moment: float
    shape: Circle
    shape_friction: shape.friction = 1
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

        space.add(self.body, self.shape)

    def add_body_limit_slide_joint(self, space: pymunk.Space(), body, body_rotation_limit):
        body_limit_slide_joint = pymunk.SlideJoint(body, body_rotation_limit, (0, 0), (0, 0), 0, 10)
        space.add(body_limit_slide_joint)
        pass

    def add_body_pin_joint(self, space: pymunk.Space(), body1: Body, body2: Body,
                           how_far_from_body1: tuple[float, float],
                           how_far_from_body2: tuple[float, float]):
        body_pin_joint = pymunk.PinJoint(body1, body2, how_far_from_body1, how_far_from_body2)
        space.add(body_pin_joint)
        pass

    def add_body_rotation_center_and_limit(self, body_rotation_center_position, body_rotation_limit_position):
        self.body_rotation_center = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body_rotation_center.position = body_rotation_center_position
        self.body_rotation_limit = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body_rotation_limit.position = body_rotation_limit_position
        return self.body_rotation_center, self.body_rotation_limit

    def add_patella(self: LegPartJoint):
        static = pymunk.Segment(self.body, (10, 30), (10, -30), 5)
        static.collision_type = 1

        return static
