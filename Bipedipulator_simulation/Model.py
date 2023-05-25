from __future__ import annotations

import pymunk
import pymunk.pygame_util

from LegSimulation_v2.Bipedipulator_simulation import LegMethodsHelper
from LegSimulation_v2.Bipedipulator_simulation.Leg import Leg, LegPartBone
from LegSimulation_v2.Bipedipulator_simulation.constants import CORPS_WIDTH, CORPS_HEIGHT, THIGH_HEIGHT, \
    CORPS_WEIGHT, CORPS_POSITION


class Model:
    corps: LegPartBone
    hip_body: pymunk.Body
    right_leg: Leg
    left_leg: Leg
    floor: pymunk.Body

    def __init__(self, space: pymunk.Space()):
        self.floor = LegMethodsHelper.running_gear(space)

        self.corps = LegPartBone(space, "corps", CORPS_WEIGHT, (CORPS_WIDTH, CORPS_HEIGHT), CORPS_POSITION)
        self.right_leg = Leg(space, "right")
        self.left_leg = Leg(space, "left")

        self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)

    def move_running_gear(self):
        self.floor.velocity = (-80, 0)

    def add_pivot_joints(self, space: pymunk.Space()):
        LegMethodsHelper.add_body_pivot_joint(space, self.corps.body, self.right_leg.thigh.body,
                                              (self.corps.body.position.x,
                                               self.corps.body.position.y - ((1 / 2) * CORPS_HEIGHT)))
        LegMethodsHelper.add_body_pivot_joint(space, self.corps.body, self.left_leg.thigh.body,
                                              (self.corps.body.position.x,
                                               self.corps.body.position.y - ((1 / 2) * CORPS_HEIGHT)))

        self.hip_body = LegMethodsHelper.add_joint_body((self.corps.body.position.x,
                                                         self.corps.body.position.y - ((1 / 2) * CORPS_HEIGHT)))
        space.add(self.hip_body)

    def add_pin_joints_parts(self, space):
        LegMethodsHelper.add_body_rotation_center(space, self.corps.body.position)
        LegMethodsHelper.add_body_pin_joint(space, self.corps.body, self.right_leg.thigh.body,
                                            (0, (-(1 / 2) * CORPS_HEIGHT)),
                                            (0, (1 / 2) * THIGH_HEIGHT))
        LegMethodsHelper.add_body_pin_joint(space, self.corps.body, self.left_leg.thigh.body,
                                            (0, (-(1 / 2) * CORPS_HEIGHT)),
                                            (0, (1 / 2) * THIGH_HEIGHT))
        LegMethodsHelper.add_body_pin_joint(space, self.corps.body, self.hip_body,
                                            (0, (-(1 / 2) * CORPS_HEIGHT)),
                                            (0, 0))
