from __future__ import annotations
from typing import List
from random import random

import pymunk
from pymunk import Poly, Vec2d, Body

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

        space.add(self.body, self.shape)

    # def tick(self, space) -> None:
    #     """Update the state of the simulation by one time step."""

    def add_body_limit_slide_joint(self, space: pymunk.Space(), body1: Body, body2: Body,
                                   how_far_from_body1: tuple[float, float], how_far_from_body2: tuple[float, float],
                                   min_distance: float, max_distance: float):
        body_limit_slide_joint = pymunk.SlideJoint(body1, body2, how_far_from_body1, how_far_from_body2, min_distance,
                                                   max_distance)
        space.add(body_limit_slide_joint)
        pass

    def add_body_pin_joint(self, space, body1: Body, body2: Body, how_far_from_body1: tuple[float, float],
                           how_far_from_body2: tuple[float, float]):
        body_pin_joint = pymunk.PinJoint(body1, body2, how_far_from_body1, how_far_from_body2)
        space.add(body_pin_joint)
        return body_pin_joint

    def add_body_rotation_center(self, space, body_rotation_center_position):
        body_rotation_center = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_rotation_center.position = body_rotation_center_position
        space.add(body_rotation_center)
        return body_rotation_center

    def add_body_rotation_limit(self, space, body_rotation_limit_position):
        body_rotation_limit = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_rotation_limit.position = body_rotation_limit_position
        space.add(body_rotation_limit)
        return body_rotation_limit

    def add_body_pivot_joint(self, space, body1: Body, body2: Body, position_arg):
        pivot_joint = pymunk.PivotJoint(body1, body2, Vec2d(*position_arg))
        space.add(pivot_joint)
        pivot_joint_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        pivot_joint_body.position = Vec2d(*position_arg)
        return pivot_joint_body

    def get_current_location(self):
        self.position.change_location(self.body.position)
        print(self.position.get_current_location())
        pass

