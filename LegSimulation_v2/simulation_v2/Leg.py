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
from pymunk import Vec2d, SlideJoint, DampedSpring
import LegPartBone
import self as self
from LegSimulation_v2.simulation_v2 import constants, LegPartsHelper
from math import sin, cos, pi, sqrt

from LegSimulation_v2.simulation_v2.LegPartBone import LegPartBone
from LegSimulation_v2.simulation_v2.constants import JOINT_RADIUS, CORPS_WIDTH, CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALE_WIDTH, CALE_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, MIN_CORPS_THIGH, MIN_CMFJ, MIN_CMBJ, PATELLA_HEIGHT, \
    PATELLA_WIDTH, MIN_PTJ, MIN_PCJ, CORPS_WEIGHT, THIGH_WEIGHT, FOOT_WEIGHT, PATELLA_WEIGHT, CALE_WEIGHT, \
    HANDLER_LENGTH, LEG_HEIGHT, FLOOR_HEIGHT, CORPS_POSITION
from LegSimulation_v2.simulation_v2.RelativeValues import RelativeValues

random.seed(1)  # make the simulation the same each time, easier to debug


class Leg:
    name: str
    num_bodies: int = 0
    thigh: LegPartBone
    cale: LegPartBone
    foot: LegPartBone
    patella_thigh_part: LegPartBone
    patella_cale_part: LegPartBone
    pivots: list[pymunk.Body]
    muscles: list[DampedSpring | SlideJoint]
    bodies: list[pymunk.Body]
    time: int = 0

    relative_values: RelativeValues

    def __init__(self, space: pymunk.Space(), leg_id):
        self.relative_values = RelativeValues()
        self.name = "right" if leg_id == 0 else "left"
        self.thigh = LegPartBone(space, self.iterator(), "thigh", THIGH_WEIGHT, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (CORPS_POSITION - (
                                     0, (((1 / 2) * CORPS_HEIGHT) + ((1 / 2) * THIGH_HEIGHT)))))
        self.patella_thigh_part = LegPartBone(space, self.iterator(), "patella", PATELLA_WEIGHT,
                                              (PATELLA_WIDTH, PATELLA_HEIGHT),
                                              self.thigh.body.position + (((0.5 * THIGH_WIDTH) + (0.5 * PATELLA_WIDTH)),
                                                                          -((3 / 8) * THIGH_HEIGHT)))
        self.cale = LegPartBone(space, self.iterator(), "cale", CALE_WEIGHT, (CALE_WIDTH, CALE_HEIGHT),
                                (self.thigh.body.position - (
                                    0, (((1 / 2) * THIGH_HEIGHT) + ((1 / 2) * CALE_HEIGHT)))))
        self.patella_cale_part = LegPartBone(space, self.iterator(), "patella", PATELLA_WEIGHT,
                                             (PATELLA_WIDTH, PATELLA_HEIGHT),
                                             self.cale.body.position + (((0.5 * CALE_WIDTH) + 0.5 * PATELLA_WIDTH),
                                                                        ((3 / 8) * CALE_HEIGHT)))
        self.foot = LegPartBone(space, self.iterator(), "foot", FOOT_WEIGHT, (FOOT_WIDTH, FOOT_HEIGHT),
                                self.cale.body.position - (0, (1 / 2) * CALE_HEIGHT + (1 / 2) * FOOT_HEIGHT))

        self.pivots = self.add_pivot_joints(space)

        self.add_pin_joints_parts(space)

        self.bodies = [self.thigh.body, self.patella_thigh_part.body, self.patella_cale_part.body,
                       self.cale.body, self.foot.body]

    def iterator(self):
        self.num_bodies = self.num_bodies + 1
        return self.num_bodies

    def add_pivot_joints(self, space):
        knee_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.thigh.body, self.cale.body,
                                                              (self.thigh.part_vector_position.x,
                                                               self.thigh.part_vector_position.y -
                                                               ((1 / 2) * THIGH_HEIGHT)))
        ankle_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.cale.body, self.foot.body,
                                                               (self.cale.part_vector_position.x,
                                                                self.cale.part_vector_position.y -
                                                                ((1 / 2) * CALE_HEIGHT)))

        patella_thigh_pivot_body = \
            LegPartsHelper.add_body_pivot_joint(space, self.patella_thigh_part.body, self.thigh.body,
                                                ((self.patella_thigh_part.part_vector_position.x - (
                                                        0.5 * PATELLA_WIDTH)),
                                                 self.patella_thigh_part.part_vector_position.y))
        patella_cale_pivot_body = \
            LegPartsHelper.add_body_pivot_joint(space, self.patella_cale_part.body, self.cale.body,
                                                (
                                                    (self.patella_cale_part.part_vector_position.x - (
                                                            0.5 * PATELLA_WIDTH)),
                                                    self.patella_cale_part.part_vector_position.y))

        knee_pivot_joint_body = LegPartsHelper.add_joint_body((self.thigh.body.position.x,
                                                               self.thigh.body.position.y -
                                                               ((1 / 2) * THIGH_HEIGHT)))
        ankle_pivot_joint_body = LegPartsHelper.add_joint_body((self.cale.body.position.x,
                                                                self.cale.body.position.y -
                                                                ((1 / 2) * CALE_HEIGHT)))
        foot_toe_pivot_joint_body = LegPartsHelper.add_joint_body((self.foot.body.position.x +
                                                                   ((1 / 2) * FOOT_WIDTH),
                                                                   self.foot.body.position.y + (0.5 * FOOT_HEIGHT)))
        foot_heel_pivot_joint_body = LegPartsHelper.add_joint_body((self.foot.body.position.x -
                                                                    ((1 / 2) * FOOT_WIDTH),
                                                                    self.foot.body.position.y + (0.5 * FOOT_HEIGHT)))
        space.add(knee_pivot_joint_body, ankle_pivot_joint_body, foot_toe_pivot_joint_body,
                  foot_heel_pivot_joint_body)
        pivots = [knee_pivot_joint_body, ankle_pivot_joint_body, foot_toe_pivot_joint_body,
                  foot_heel_pivot_joint_body]

        return pivots

    def add_pin_joints_parts(self, space):
        knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.cale.body,
                                                           (0, (-(1 / 2) * THIGH_HEIGHT)), (0, (1 / 2) * CALE_HEIGHT))
        ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.cale.body, self.foot.body,
                                                            (0, (-(1 / 2) * CALE_HEIGHT)), (0, (1 / 2) * FOOT_HEIGHT))
        s_knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.pivots.__getitem__(0),
                                                             (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))
        s_ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.cale.body, self.pivots.__getitem__(1),
                                                              (0, (-(1 / 2) * CALE_HEIGHT)), (0, 0))
        s_toe_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.foot.body, self.pivots.__getitem__(2),
                                                            ((1 / 2) * FOOT_WIDTH, ((1 / 2) * FOOT_HEIGHT)), (0, 0))
        s_heel_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.foot.body, self.pivots.__getitem__(3),
                                                             (-(1 / 2) * FOOT_WIDTH, ((1 / 2) * FOOT_HEIGHT)), (0, 0))

        pin_joints = [knee_pin_joint, ankle_pin_joint]
        return pin_joints
