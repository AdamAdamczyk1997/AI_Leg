from __future__ import annotations
from typing import List
from random import random

import pymunk
from pymunk import Poly, Vec2d, Body

from LegSimulation_v2.simulation.Location import Location


def add_body_dumped_spring(space: pymunk.Space(), body1: Body, body2: Body,
                           how_far_from_body1: tuple[float, float], how_far_from_body2: tuple[float, float],
                           rest_length: float, stiffness: float, damping: float):
    body_dumped_spring = pymunk.DampedSpring(body1, body2, how_far_from_body1, how_far_from_body2, rest_length,
                                             stiffness, damping)
    space.add(body_dumped_spring)
    return body_dumped_spring


def add_body_limit_slide_joint(space: pymunk.Space(), body1: Body, body2: Body,
                               how_far_from_body1: tuple[float, float], how_far_from_body2: tuple[float, float],
                               min_distance: float, max_distance: float):
    body_limit_slide_joint = pymunk.SlideJoint(body1, body2, how_far_from_body1, how_far_from_body2, min_distance,
                                               max_distance)
    space.add(body_limit_slide_joint)
    return body_limit_slide_joint


def add_body_pin_joint(space, body1: Body, body2: Body, how_far_from_body1: tuple[float, float],
                       how_far_from_body2: tuple[float, float]):
    body_pin_joint = pymunk.PinJoint(body1, body2, how_far_from_body1, how_far_from_body2)
    space.add(body_pin_joint)
    return body_pin_joint


def add_body_rotation_center(space, body_rotation_center_position):
    body_rotation_center = pymunk.Body(body_type=pymunk.Body.STATIC)
    body_rotation_center.position = body_rotation_center_position
    space.add(body_rotation_center)
    return body_rotation_center


def add_body_rotation_limit(space, body_rotation_limit_position):
    body_rotation_limit = pymunk.Body(body_type=pymunk.Body.STATIC)
    body_rotation_limit.position = body_rotation_limit_position
    space.add(body_rotation_limit)
    return body_rotation_limit


def add_body_pivot_joint(space, body1: Body, body2: Body, position_arg):
    pivot_joint = pymunk.PivotJoint(body1, body2, Vec2d(*position_arg))
    pivot_joint_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    pivot_joint_body.position = Vec2d(*position_arg)
    space.add(pivot_joint, pivot_joint_body)
    return pivot_joint_body


class LegPartsHelper:

    def __init__(self):
        self.position = None
        self.body = None

    def get_current_location(self):
        self.position.change_location(self.body.part_vector_position)
        self.position.get_current_location()
        pass

    def update(self, position):
        self.position = position
