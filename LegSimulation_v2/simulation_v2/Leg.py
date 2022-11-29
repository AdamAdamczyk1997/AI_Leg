from __future__ import annotations

import random

import pymunk
import pymunk.pygame_util
from pymunk import SlideJoint, DampedSpring

import LegPartBone
from LegSimulation_v2.simulation_v2 import LegPartsHelper
from LegSimulation_v2.simulation_v2.LegPartBone import LegPartBone
from LegSimulation_v2.simulation_v2.RelativeValues import RelativeValues
from LegSimulation_v2.simulation_v2.constants import CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALE_WIDTH, CALE_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, PATELLA_HEIGHT, \
    PATELLA_WIDTH, THIGH_WEIGHT, FOOT_WEIGHT, PATELLA_WEIGHT, CALE_WEIGHT, \
    CORPS_POSITION

random.seed(1)  # make the simulation the same each time, easier to debug


class Leg:
    name: str
    num_bodies: int = 0

    thigh: LegPartBone
    knee_body: pymunk.Body
    cale: LegPartBone
    ankle_body: pymunk.Body
    foot: LegPartBone

    patella_thigh_part: LegPartBone
    patella_cale_part: LegPartBone

    pivots: list[pymunk.Body]
    muscles: list[DampedSpring | SlideJoint]
    bodies: list[pymunk.Body]
    time: int = 0
    mode: str

    relative_values: RelativeValues

    def __init__(self, space: pymunk.Space(), mode: str, leg_id):
        self.relative_values = RelativeValues()
        self.name = "right" if leg_id == 0 else "left"
        self.thigh = LegPartBone(space, self.iterator(), "thigh", THIGH_WEIGHT, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (CORPS_POSITION - (0, (((1 / 2) * CORPS_HEIGHT) + ((1 / 2) * THIGH_HEIGHT)))))
        self.cale = LegPartBone(space, self.iterator(), "cale", CALE_WEIGHT, (CALE_WIDTH, CALE_HEIGHT),
                                (self.thigh.body.position - (
                                    0, (((1 / 2) * THIGH_HEIGHT) + ((1 / 2) * CALE_HEIGHT)))))
        self.foot = LegPartBone(space, self.iterator(), "foot", FOOT_WEIGHT, (FOOT_WIDTH, FOOT_HEIGHT),
                                self.cale.body.position - (
                                    (-1 / 4) * FOOT_WIDTH, (1 / 2) * CALE_HEIGHT + (1 / 2) * FOOT_HEIGHT))

        self.knee_body = LegPartsHelper.add_joint_body((self.thigh.body.position.x,
                                                        self.thigh.body.position.y -
                                                        ((1 / 2) * THIGH_HEIGHT)))
        self.ankle_body = LegPartsHelper.add_joint_body((self.cale.body.position.x,
                                                         self.cale.body.position.y -
                                                         ((1 / 2) * CALE_HEIGHT)))
        self.bodies = [self.thigh.body, self.cale.body, self.foot.body, self.knee_body, self.ankle_body]

        self.mode = mode
        if self.mode == "AI mode":
            if self.name == "right":
                self.patella_thigh_part = LegPartBone(space, self.iterator(), "patella", PATELLA_WEIGHT,
                                                      (PATELLA_WIDTH, PATELLA_HEIGHT), self.thigh.body.position + (
                                                          ((0.5 * THIGH_WIDTH) + (0.5 * PATELLA_WIDTH)),
                                                          -((3 / 8) * THIGH_HEIGHT)))
                self.patella_cale_part = LegPartBone(space, self.iterator(), "patella", PATELLA_WEIGHT,
                                                     (PATELLA_WIDTH, PATELLA_HEIGHT), self.cale.body.position + (
                                                         ((0.5 * CALE_WIDTH) + 0.5 * PATELLA_WIDTH),
                                                         ((3 / 8) * CALE_HEIGHT)))
                self.bodies.append(self.patella_thigh_part.body)
                self.bodies.append(self.patella_cale_part.body)

        self.pivots = self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)

    def iterator(self):
        self.num_bodies = self.num_bodies + 1
        return self.num_bodies

    def add_pivot_joints(self, space):
        knee_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.thigh.body, self.cale.body,
                                                              self.knee_body.position)
        ankle_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.cale.body, self.foot.body,
                                                               self.ankle_body.position)
        foot_toe_pivot_joint_body = LegPartsHelper.add_joint_body((self.foot.body.position.x +
                                                                   ((1 / 2) * FOOT_WIDTH),
                                                                   self.foot.body.position.y - (0.5 * FOOT_HEIGHT)))
        foot_heel_pivot_joint_body = LegPartsHelper.add_joint_body((self.foot.body.position.x -
                                                                    ((1 / 2) * FOOT_WIDTH),
                                                                    self.foot.body.position.y - (0.5 * FOOT_HEIGHT)))
        foot_center_pivot_joint_body = LegPartsHelper.add_joint_body((self.foot.body.position.x -
                                                                      ((1 / 4) * FOOT_WIDTH),
                                                                      self.foot.body.position.y - (0.5 * FOOT_HEIGHT)))
        space.add(self.knee_body, self.ankle_body, foot_toe_pivot_joint_body,
                  foot_heel_pivot_joint_body, foot_center_pivot_joint_body)
        pivots = [self.knee_body, self.ankle_body, foot_toe_pivot_joint_body,
                  foot_heel_pivot_joint_body, foot_center_pivot_joint_body]

        if self.mode == "AI mode":
            if self.name == "right":
                patella_thigh_pivot_body = \
                    LegPartsHelper.add_body_pivot_joint(space, self.patella_thigh_part.body, self.thigh.body,
                                                        ((self.patella_thigh_part.body.position.x - (
                                                                0.5 * PATELLA_WIDTH)),
                                                         self.patella_thigh_part.body.position.y))
                patella_cale_pivot_body = \
                    LegPartsHelper.add_body_pivot_joint(space, self.patella_cale_part.body, self.cale.body,
                                                        ((self.patella_cale_part.body.position.x - (
                                                                0.5 * PATELLA_WIDTH)),
                                                         self.patella_cale_part.body.position.y))

        return pivots

    def add_pin_joints_parts(self, space):
        s_knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.knee_body,
                                                             (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))
        knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.knee_body, self.cale.body,
                                                           (0, 0), (0, (1 / 2) * CALE_HEIGHT))

        s_ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.cale.body, self.ankle_body,
                                                              (0, (-(1 / 2) * CALE_HEIGHT)), (0, 0))
        ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.ankle_body, self.foot.body,
                                                            (0, 0), ((-1 / 4) * FOOT_WIDTH, (1 / 2) * FOOT_HEIGHT))

        s_toe_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.foot.body, self.pivots.__getitem__(2),
                                                            ((1 / 2) * FOOT_WIDTH, (-(1 / 2) * FOOT_HEIGHT)), (0, 0))
        s_heel_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.foot.body, self.pivots.__getitem__(3),
                                                             (-(1 / 2) * FOOT_WIDTH, (-(1 / 2) * FOOT_HEIGHT)), (0, 0))
        fot_center_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.foot.body, self.pivots.__getitem__(4),
                                                                 (-(1 / 4) * FOOT_WIDTH, (-(1 / 2) * FOOT_HEIGHT)),
                                                                 (0, 0))

        pin_joints = [knee_pin_joint, ankle_pin_joint]
        return pin_joints
