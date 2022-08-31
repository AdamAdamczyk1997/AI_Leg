from __future__ import annotations
from typing import List
from random import random

import pymunk
from typing import List
import random
import pymunk
import pymunk.pygame_util
# from kivy.graphics import Quad, Triangle
from pygame import Color
from pymunk import Vec2d, SlideJoint
import LegPartBone
import self as self
from LegSimulation_v2.simulation import constants, LegPartsHelper
from math import sin, cos, pi, sqrt

from LegSimulation_v2.simulation.LegPartBone import LegPartBone
from LegSimulation_v2.simulation.LegPartJoint import LegPartJoint
from LegSimulation_v2.simulation.constants import JOINT_RADIUS, CORPS_WIDTH, CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALE_WIDTH, CALE_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, MIN_CTBJ, MIN_CORPS_THIGH

random.seed(1)  # make the simulation the same each time, easier to debug


class Model:
    corps: LegPartBone
    hip: LegPartJoint
    thigh: LegPartBone
    knee: LegPartJoint
    cale: LegPartBone
    ankle: LegPartJoint
    foot: LegPartBone
    muscles: list[SlideJoint]
    time: int = 0

    def __init__(self, space):
        self.corps = LegPartBone(space, "corps", 100, (CORPS_WIDTH, CORPS_HEIGHT), Vec2d(1000, 700))
        self.thigh = LegPartBone(space, "thigh", 50, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (self.corps.body.position - (
                                     0, (((1 / 2) * CORPS_HEIGHT) + 2 * JOINT_RADIUS + ((1 / 2) * THIGH_HEIGHT)))))
        self.cale = LegPartBone(space, "cale", 50, (CALE_WIDTH, CALE_HEIGHT),
                                (self.thigh.body.position - (
                                    0, (((1 / 2) * THIGH_HEIGHT) + 2 * JOINT_RADIUS + ((1 / 2) * CALE_HEIGHT)))))
        self.foot = LegPartBone(space, "foot", 20, (FOOT_WIDTH, FOOT_HEIGHT),
                                (self.cale.body.position - (JOINT_RADIUS + (-(1 / 2) * FOOT_WIDTH), (
                                        ((1 / 2) * CALE_HEIGHT) + 2 * JOINT_RADIUS + ((1 / 2) * FOOT_HEIGHT)))))

        pivots = self.add_pivot_joints(space)
        self.hip = LegPartJoint(space, "hip", 10, JOINT_RADIUS, pivots[0].position)
        self.knee = LegPartJoint(space, "knee", 10, JOINT_RADIUS, pivots[1].position)
        self.ankle = LegPartJoint(space, "ankle", 10, JOINT_RADIUS, pivots[2].position)

        add_pin_joints_parts(space, self.corps, self.hip, self.thigh, self.knee, self.cale, self.ankle, self.foot)
        self.muscles = self.add_muscles_joints(space)

        patella = self.knee.add_patella((1 / 2) * THIGH_WIDTH + 4, 10, 4)
        part1 = self.thigh.add_bone_part(((1 / 2) * THIGH_HEIGHT) - 2, 4, THIGH_WIDTH)
        part2 = self.cale.add_bone_part(((1 / 2) * CALE_HEIGHT) - 2, 4, CALE_WIDTH)
        space.add(patella, part1, part2)

        add_floor(space)

    def tick(self):
        self.muscles[2].max -= 10
        pass

    def move_muscles(self, index):
        if index == 0:
            self.muscles.__getitem__(index).max -= 10
            self.muscles.__getitem__(index + 1).max += 10
        elif index == 1:
            self.muscles.__getitem__(index).max -= 10
            self.muscles.__getitem__(index - 1).max += 10
        elif index == 2:
            self.muscles.__getitem__(index).max -= 10
            self.muscles.__getitem__(index + 1).max += 10
        elif index == 3:
            self.muscles.__getitem__(index).max -= 10
            self.muscles.__getitem__(index - 1).max += 10
        elif index == 4:
            self.muscles.__getitem__(index).max -= 10
            self.muscles.__getitem__(index + 1).max += 10
        elif index == 5:
            self.muscles.__getitem__(index).max -= 10
            self.muscles.__getitem__(index - 1).max += 10
        pass

    def add_pivot_joints(self, space):
        hip_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.corps.body, self.thigh.body,
                                                             (self.corps.position.x,
                                                              self.corps.position.y -
                                                              (JOINT_RADIUS + ((1 / 2) * CORPS_HEIGHT))))
        knee_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.thigh.body, self.cale.body,
                                                              (self.thigh.position.x,
                                                               self.thigh.position.y -
                                                               (JOINT_RADIUS + ((1 / 2) * THIGH_HEIGHT))))
        ankle_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.cale.body, self.foot.body,
                                                               (self.cale.position.x,
                                                                self.cale.position.y -
                                                                (JOINT_RADIUS + ((1 / 2) * CALE_HEIGHT))))
        pivots = [hip_pivot_body, knee_pivot_body, ankle_pivot_body]
        return pivots

    def add_muscles_joints(self, space):
        cale_muscle_front_joint = LegPartsHelper.add_body_limit_slide_joint(space, self.cale.body, self.foot.body,
                                                                            (CALE_WIDTH, (1 / 2) * CALE_HEIGHT),
                                                                            (0, 0.5 * FOOT_HEIGHT),
                                                                            CALE_HEIGHT + 2 * JOINT_RADIUS,
                                                                            220)
        cale_muscle_back_joint = LegPartsHelper.add_body_limit_slide_joint(space, self.cale.body, self.foot.body,
                                                                           (-CALE_WIDTH, (1 / 2) * CALE_HEIGHT),
                                                                           (-0.5 * FOOT_WIDTH, 0.5 * FOOT_HEIGHT),
                                                                           CALE_HEIGHT + 2 * JOINT_RADIUS,
                                                                           220)
        thigh_cale_muscle_front_joint = LegPartsHelper.add_body_limit_slide_joint(space, self.thigh.body, self.cale.body,
                                                                             (THIGH_WIDTH, (0.5 * THIGH_HEIGHT)),
                                                                             (CALE_WIDTH, (0.5 * CALE_HEIGHT)),
                                                                             THIGH_HEIGHT + 2 * JOINT_RADIUS,
                                                                             300)
        thigh_cale_muscle_back_joint = LegPartsHelper.add_body_limit_slide_joint(space, self.thigh.body, self.cale.body,
                                                                            (-THIGH_WIDTH, (0.5 * THIGH_HEIGHT)),
                                                                            (-CALE_WIDTH, (0.5 * CALE_HEIGHT)),
                                                                            THIGH_HEIGHT + 2 * JOINT_RADIUS,
                                                                             300)
        thigh_corps_muscle_front_joint = LegPartsHelper.add_body_limit_slide_joint(space, self.corps.body, self.thigh.body,
                                                                                   (0.5 * CORPS_WIDTH,
                                                                                    (-0.5 * CORPS_HEIGHT)),
                                                                                   (THIGH_WIDTH,
                                                                                    (0.5 * THIGH_HEIGHT)),
                                                                                   (sqrt(pow(((1 / 2) * CORPS_WIDTH - (2 * JOINT_RADIUS)), 2) + pow((2 * JOINT_RADIUS), 2))), 150)
        thigh_cops_muscle_back_joint = LegPartsHelper.add_body_limit_slide_joint(space, self.corps.body,
                                                                                 self.thigh.body,
                                                                                 (-0.5 * CORPS_WIDTH,
                                                                                  (-0.5 * CORPS_HEIGHT)),
                                                                                 (-THIGH_WIDTH,
                                                                                  (0.5 * THIGH_HEIGHT)),
                                                                                 (sqrt(pow(((1 / 2) * CORPS_WIDTH - (2 * JOINT_RADIUS)), 2) + pow((2 * JOINT_RADIUS), 2))), 150)

        slides_joints = [cale_muscle_front_joint, cale_muscle_back_joint,
                         thigh_cale_muscle_front_joint, thigh_cale_muscle_back_joint,
                         thigh_corps_muscle_front_joint, thigh_cops_muscle_back_joint]
        return slides_joints

    def release(self):
        self.corps.body.body_type = pymunk.Body.DYNAMIC
        pass


def add_pin_joints_parts(space, corps, hip, thigh, knee, cale, ankle, foot):
    corps_rotation_center = LegPartsHelper.add_body_rotation_center(space, corps.body.position)
    corps_temp_pin_joint = LegPartsHelper.add_body_pin_joint(space, corps.body, corps_rotation_center, (0, 0), (0, 0))
    corps_hip_pin_joint = LegPartsHelper.add_body_pin_joint(space, corps.body, hip.body,
                                                            (0, (-(1 / 2) * CORPS_HEIGHT)), (0, 0))
    hip_thigh_pin_joint = LegPartsHelper.add_body_pin_joint(space, hip.body, thigh.body,
                                                            (0, 0), (0, ((1 / 2) * THIGH_HEIGHT)))
    thigh_knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, thigh.body, knee.body,
                                                             (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))
    knee_cale_pin_joint = LegPartsHelper.add_body_pin_joint(space, knee.body, cale.body,
                                                            (0, 0), (0, ((1 / 2) * CALE_HEIGHT)))
    cale_ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, cale.body, ankle.body,
                                                             (0, (-(1 / 2) * CALE_HEIGHT)), (0, 0))
    ankle_foot_pin_joint = LegPartsHelper.add_body_pin_joint(space, ankle.body, foot.body,
                                                             (0, 0),
                                                             (JOINT_RADIUS + (-((1 / 2) * FOOT_WIDTH)),
                                                              ((1 / 2) * FOOT_HEIGHT)))

    return space


def add_floor(space):
    floor = pymunk.Segment(space.static_body, (-100, 0), (2000, 0), 5)
    floor.friction = 1.0
    space.add(floor)

    return space


def add_ball(space):
    """Add a ball to the given space at a random position"""
    mass = 3
    radius = 25
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
    body = pymunk.Body(mass, inertia)
    x = random.randint(400, 1500)
    body.position = x, 900
    shape = pymunk.Circle(body, radius, (0, 0))
    shape.friction = 1
    space.add(body, shape)
    return shape


def ball_controller(space, balls: [], ticks_to_next_ball):
    ticks_to_next_ball -= 1
    if ticks_to_next_ball <= 0:
        ticks_to_next_ball = 1000
        ball_shape = add_ball(space)
        balls.append(ball_shape)

    balls_to_remove = []
    for ball in balls:
        if ball.body.position.y == constants.MIN_Y:
            balls_to_remove.append(ball)

    for ball in balls_to_remove:
        space.remove(ball, ball.body)
        balls.remove(ball)

    return ticks_to_next_ball
