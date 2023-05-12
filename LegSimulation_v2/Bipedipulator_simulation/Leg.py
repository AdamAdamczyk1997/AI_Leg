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
    CALF_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, THIGH_WEIGHT, FOOT_WEIGHT, CALF_WIDTH, \
    CORPS_POSITION

random.seed(1)  # make the simulation the same each time, easier to debug


class Leg:
    name: str

    thigh: LegPartBone
    knee_body: pymunk.Body
    calf: LegPartBone
    ankle_body: pymunk.Body
    foot: LegPartBone

    muscles: list[DampedSpring | SlideJoint]
    bodies: list[pymunk.Body]
    time: int = 0
    mode: str

    relative_values: list[RelativeValues]
    equations: Equations

    def __init__(self, space: pymunk.Space(), name: str):
        # TODO: do something with this
        self.relative_values = [RelativeValues(), RelativeValues(), RelativeValues()]
        self.name = name
        self.equations = Equations(self.name)

        self.thigh = LegPartBone(space, "thigh", THIGH_WEIGHT, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (CORPS_POSITION - (0, (((1 / 2) * CORPS_HEIGHT) + ((1 / 2) * THIGH_HEIGHT)))))
        self.calf = LegPartBone(space, "calf", CALF_WIDTH, (CALF_WIDTH, CALF_HEIGHT),
                                (self.thigh.body.position - (
                                    0, (((1 / 2) * THIGH_HEIGHT) + ((1 / 2) * CALF_HEIGHT)))))
        self.foot = LegPartBone(space, "foot", FOOT_WEIGHT, (FOOT_WIDTH, FOOT_HEIGHT),
                                self.calf.body.position - (
                                    (-1 / 4) * FOOT_WIDTH, (1 / 2) * CALF_HEIGHT + (1 / 2) * FOOT_HEIGHT))

        self.knee_body = LegPartsHelper.add_joint_body((self.thigh.body.position.x,
                                                        self.thigh.body.position.y -
                                                        ((1 / 2) * THIGH_HEIGHT)))
        self.ankle_body = LegPartsHelper.add_joint_body((self.calf.body.position.x,
                                                         self.calf.body.position.y -
                                                         ((1 / 2) * CALF_HEIGHT)))
        self.bodies = [self.thigh.body, self.calf.body, self.foot.body, self.knee_body, self.ankle_body]

        self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)

    def add_pivot_joints(self, space):
        LegPartsHelper.add_body_pivot_joint(space, self.thigh.body, self.calf.body,
                                            self.knee_body.position)
        LegPartsHelper.add_body_pivot_joint(space, self.calf.body, self.foot.body,
                                            self.ankle_body.position)

        space.add(self.knee_body, self.ankle_body)

    def add_pin_joints_parts(self, space):
        LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.calf.body,
                                          (0, (-(1 / 2) * THIGH_HEIGHT)), (0, (1 / 2) * CALF_HEIGHT))
        LegPartsHelper.add_body_pin_joint(space, self.thigh.body, self.knee_body,
                                          (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))
        LegPartsHelper.add_body_pin_joint(space, self.calf.body, self.foot.body,
                                          (0, (-(1 / 2) * CALF_HEIGHT)), ((-1 / 4) * FOOT_WIDTH, (1 / 2) * FOOT_HEIGHT))
        LegPartsHelper.add_body_pin_joint(space, self.calf.body, self.ankle_body,
                                          (0, (-(1 / 2) * CALF_HEIGHT)), (0, 0))
