from __future__ import annotations

from typing import Union

import pymunk
from pymunk import Vec2d, Body

from Bipedipulator_simulation.Model import Model
from Bipedipulator_simulation.constants import FLOOR_HEIGHT


def limit_velocity(bodies: list[pymunk.Body], gravity, dt):
    damping = 0.99
    for x in range(len(bodies)):
        max_velocity = 100
        pymunk.Body.update_velocity(bodies[x], gravity, damping, dt)
        if bodies[x].velocity.length > max_velocity:
            bodies[x].velocity = bodies[x].velocity * 0.99


def motor_leg(model_entity: Model, space: pymunk.Space()):
    corps_motor = pymunk.SimpleMotor(model_entity.corps.body, model_entity.floor, 0)

    left_thigh_motor = pymunk.SimpleMotor(model_entity.left_leg.thigh.body, model_entity.corps.body, 0)
    left_calf_motor = pymunk.SimpleMotor(model_entity.left_leg.calf.body, model_entity.left_leg.thigh.body, 0)
    left_foot_motor = pymunk.SimpleMotor(model_entity.left_leg.foot.body, model_entity.floor, 0)

    right_thigh_motor = pymunk.SimpleMotor(model_entity.right_leg.thigh.body, model_entity.corps.body, 0)
    right_calf_motor = pymunk.SimpleMotor(model_entity.right_leg.calf.body, model_entity.right_leg.thigh.body, 0)
    right_foot_motor = pymunk.SimpleMotor(model_entity.right_leg.foot.body, model_entity.floor, 0)

    space.add(right_thigh_motor, right_calf_motor,
              right_foot_motor, left_thigh_motor, left_calf_motor, left_foot_motor, corps_motor)

    motors = [right_thigh_motor, right_calf_motor, right_foot_motor,
              left_thigh_motor, left_calf_motor, left_foot_motor, corps_motor]

    return motors


def running_gear(space):
    floor = pymunk.Body()
    floor.body_type = pymunk.Body.KINEMATIC
    floor.shape = pymunk.Segment(floor, (0, 0), (100000, 0), FLOOR_HEIGHT)
    floor.shape.friction = 1.0
    space.add(floor, floor.shape)

    return floor


def add_test_ball():
    """Add a ball to the given space at a random position"""
    mass = 1
    radius = 20
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
    body = pymunk.Body(mass, inertia)
    body.position = 200, 1000
    shape = pymunk.Circle(body, radius, (0, 0))
    shape.friction = 1
    return [body, shape]


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
    space.add(pivot_joint)
    return pivot_joint


def add_joint_body(position: Union[Vec2d, tuple[float, float]]):
    # TODO: add space to this method like on methods above
    mass = 1
    size = (1, 1)
    moment = pymunk.moment_for_box(mass, size)
    pivot_joint_body = pymunk.Body(mass, moment)
    pivot_joint_body.body_type = pymunk.Body.DYNAMIC
    pivot_joint_body.position = position
    return pivot_joint_body


def show_counters(model_entity: Model):
    model_entity.right_leg.relative_values[0].counters.show_counters()
    model_entity.left_leg.relative_values[0].counters.show_counters()
    model_entity.right_leg.relative_values[1].counters.show_counters()
    model_entity.left_leg.relative_values[1].counters.show_counters()
    model_entity.right_leg.relative_values[2].counters.show_counters()
    model_entity.left_leg.relative_values[2].counters.show_counters()
