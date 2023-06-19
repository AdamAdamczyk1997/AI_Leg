from __future__ import annotations

import pymunk.pygame_util

from Bipedipulator_simulation import LegMethodsHelper
from Bipedipulator_simulation.Leg import Leg, LegPartBone
from Bipedipulator_simulation.constants import CORPS_WIDTH, CORPS_HEIGHT, THIGH_HEIGHT, \
    CORPS_WEIGHT, CORPS_POSITION, FLOOR_VELOCITY


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

    def add_pivot_joints(self, space: pymunk.Space()):
        LegMethodsHelper.add_body_pivot_joint(space, self.corps.body, self.right_leg.thigh.body,
                                              (self.corps.body.position.x,
                                               self.corps.body.position.y - (CORPS_HEIGHT / 2)))
        LegMethodsHelper.add_body_pivot_joint(space, self.corps.body, self.left_leg.thigh.body,
                                              (self.corps.body.position.x,
                                               self.corps.body.position.y - (CORPS_HEIGHT / 2)))

        self.hip_body = LegMethodsHelper.add_joint_body(space, (self.corps.body.position.x,
                                                                self.corps.body.position.y - (CORPS_HEIGHT / 2)))

    def add_pin_joints_parts(self, space: pymunk.Space()):
        LegMethodsHelper.add_body_rotation_center(space, self.corps.body.position)
        LegMethodsHelper.add_body_pin_joint(space, self.corps.body, self.right_leg.thigh.body,
                                            (0, (-CORPS_HEIGHT / 2)), (0, THIGH_HEIGHT / 2))
        LegMethodsHelper.add_body_pin_joint(space, self.corps.body, self.left_leg.thigh.body,
                                            (0, (-CORPS_HEIGHT / 2)), (0, THIGH_HEIGHT / 2))
        LegMethodsHelper.add_body_pin_joint(space, self.corps.body, self.hip_body,
                                            (0, (-CORPS_HEIGHT / 2)), (0, 0))

    def move_running_gear(self):
        self.floor.velocity = (FLOOR_VELOCITY, 0)
