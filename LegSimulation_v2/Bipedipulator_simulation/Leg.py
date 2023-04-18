from __future__ import annotations

import random

import pymunk
import pymunk.pygame_util
from pymunk import SlideJoint, DampedSpring

import LegPartBone
from LegSimulation_v2.Bipedipulator_simulation import LegPartsHelper
from LegSimulation_v2.Bipedipulator_simulation.LegPartBone import LegPartBone
from LegSimulation_v2.Bipedipulator_simulation.RelativeValues import RelativeValues
from LegSimulation_v2.Bipedipulator_simulation.ValuesPerPhase import Equations
from LegSimulation_v2.Bipedipulator_simulation.constants import CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALF_WIDTH, CALF_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, PATELLA_HEIGHT, \
    PATELLA_WIDTH, THIGH_WEIGHT, FOOT_WEIGHT, PATELLA_WEIGHT, CALF_WIDTH, \
    CORPS_POSITION

random.seed(1)  # make the simulation the same each time, easier to debug


class Leg:
    name: str
    num_bodies: int = 0

    thigh: LegPartBone
    knee_body: pymunk.Body
    calf: LegPartBone
    ankle_body: pymunk.Body
    foot: LegPartBone

    patella_thigh_part: LegPartBone
    patella_calf_part: LegPartBone

    pivots: list[pymunk.Body]
    muscles: list[DampedSpring | SlideJoint]
    bodies: list[pymunk.Body]
    time: int = 0
    mode: str

    relative_values: list[RelativeValues]
    equations: Equations

    def __init__(self, space: pymunk.Space(), mode: str, leg_id):
        self.relative_values = [RelativeValues(), RelativeValues(), RelativeValues(), RelativeValues(), RelativeValues(), RelativeValues(), RelativeValues()]
        self.name = "right" if leg_id == 0 else "left"
        self.equations = Equations(self.name)
        self.thigh = LegPartBone(space, self.iterator(), "thigh", THIGH_WEIGHT, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (CORPS_POSITION - (0, (((1 / 2) * CORPS_HEIGHT) + ((1 / 2) * THIGH_HEIGHT)))))
        self.calf = LegPartBone(space, self.iterator(), "calf", CALF_WIDTH, (CALF_WIDTH, CALF_HEIGHT),
                                (self.thigh.body.position - (
                                    0, (((1 / 2) * THIGH_HEIGHT) + ((1 / 2) * CALF_HEIGHT)))))
        self.foot = LegPartBone(space, self.iterator(), "foot", FOOT_WEIGHT, (FOOT_WIDTH, FOOT_HEIGHT),
                                self.calf.body.position - (
                                    (-1 / 4) * FOOT_WIDTH, (1 / 2) * CALF_HEIGHT + (1 / 2) * FOOT_HEIGHT))

        self.knee_body = LegPartsHelper.add_joint_body((self.thigh.body.position.x,
                                                        self.thigh.body.position.y -
                                                        ((1 / 2) * THIGH_HEIGHT)))
        self.ankle_body = LegPartsHelper.add_joint_body((self.calf.body.position.x,
                                                         self.calf.body.position.y -
                                                         ((1 / 2) * CALF_HEIGHT)))
        self.bodies = [self.thigh.body, self.calf.body, self.foot.body, self.knee_body, self.ankle_body]

        self.mode = mode
        if self.mode == "AI mode":
            if self.name == "right":
                self.patella_thigh_part = LegPartBone(space, self.iterator(), "patella", PATELLA_WEIGHT,
                                                      (PATELLA_WIDTH, PATELLA_HEIGHT), self.thigh.body.position + (
                                                          ((0.5 * THIGH_WIDTH) + (0.5 * PATELLA_WIDTH)),
                                                          -((3 / 8) * THIGH_HEIGHT)))
                self.patella_calf_part = LegPartBone(space, self.iterator(), "patella", PATELLA_WEIGHT,
                                                     (PATELLA_WIDTH, PATELLA_HEIGHT), self.calf.body.position + (
                                                         ((0.5 * CALF_WIDTH) + 0.5 * PATELLA_WIDTH),
                                                         ((3 / 8) * CALF_HEIGHT)))
                self.bodies.append(self.patella_thigh_part.body)
                self.bodies.append(self.patella_calf_part.body)

        self.pivots = self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)

    def iterator(self):
        self.num_bodies = self.num_bodies + 1
        return self.num_bodies

    def add_pivot_joints(self, space):
        knee_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.thigh.body, self.calf.body,
                                                              self.knee_body.position)
        ankle_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.calf.body, self.foot.body,
                                                               self.ankle_body.position)
        # foot_center_pivot_joint_body = LegPartsHelper.add_joint_body((self.foot.body.position.x -
        #                                                               ((1 / 4) * FOOT_WIDTH),
        #                                                               self.foot.body.position.y - (0.5 * FOOT_HEIGHT)))

        space.add(self.knee_body, self.ankle_body)
        pivots = [self.knee_body, self.ankle_body]

        if self.mode == "AI mode":
            if self.name == "right":
                patella_thigh_pivot_body = \
                    LegPartsHelper.add_body_pivot_joint(space, self.patella_thigh_part.body, self.thigh.body,
                                                        ((self.patella_thigh_part.body.position.x - (
                                                                0.5 * PATELLA_WIDTH)),
                                                         self.patella_thigh_part.body.position.y))
                patella_calf_pivot_body = \
                    LegPartsHelper.add_body_pivot_joint(space, self.patella_calf_part.body, self.calf.body,
                                                        ((self.patella_calf_part.body.position.x - (
                                                                0.5 * PATELLA_WIDTH)),
                                                         self.patella_calf_part.body.position.y))

        return pivots

    def add_pin_joints_parts(self, space):
        # s_knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.knee_body,
        #                                                      (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))
        # knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.knee_body, self.calf.body,
        #                                                    (0, 0), (0, (1 / 2) * CALF_HEIGHT))
        #
        # s_ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.calf.body, self.ankle_body,
        #                                                       (0, (-(1 / 2) * CALF_HEIGHT)), (0, 0))
        # ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.ankle_body, self.foot.body,
        #                                                     (0, 0), ((-1 / 4) * FOOT_WIDTH, (1 / 2) * FOOT_HEIGHT))

        # zmien spowrotem na udo do calf bo model się chwieje jak jest połączony na stawach a nie potrzebnie
        knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.calf.body,
                                                           (0, (-(1 / 2) * THIGH_HEIGHT)), (0, (1 / 2) * CALF_HEIGHT))
        s_knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.knee_body,
                                                             (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))

        ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.calf.body, self.foot.body,
                                                            (0, (-(1 / 2) * CALF_HEIGHT)),
                                                            ((-1 / 4) * FOOT_WIDTH, (1 / 2) * FOOT_HEIGHT))
        s_ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.calf.body, self.ankle_body,
                                                              (0, (-(1 / 2) * CALF_HEIGHT)), (0, 0))
        # fot_center_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.foot.body, self.pivots.__getitem__(2),
        #                                                          (-(1 / 4) * FOOT_WIDTH, (-(1 / 2) * FOOT_HEIGHT)),
        #                                                          (0, 0))

        pin_joints = [knee_pin_joint, ankle_pin_joint]
        return pin_joints
