from __future__ import annotations

import random

import pymunk
import pymunk.pygame_util
# from kivy.graphics import Quad, Triangle
from pymunk import SlideJoint, DampedSpring

import LegPartBone
from LegSimulation_v2.Bipedipulator_simulation import LegPartsHelper
from LegSimulation_v2.Bipedipulator_simulation.Leg import Leg
from LegSimulation_v2.Bipedipulator_simulation.LegPartBone import LegPartBone
from LegSimulation_v2.Bipedipulator_simulation.ValuesPerPhase import Equations
from LegSimulation_v2.Bipedipulator_simulation.constants import CORPS_WIDTH, CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALE_WIDTH, CALE_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, MIN_CMFJ, MIN_CMBJ, PATELLA_WIDTH, MIN_PTJ, MIN_PCJ, CORPS_WEIGHT, \
    LEG_HEIGHT, FLOOR_HEIGHT, CORPS_POSITION

random.seed(1)  # make the simulation the same each time, easier to debug


def running_gear(space):
    floor = pymunk.Body()
    floor.body_type = pymunk.Body.KINEMATIC
    floor.shape = pymunk.Segment(floor, (0, 0), (100000, 0), FLOOR_HEIGHT)
    floor.shape.friction = 1.0
    floor.shape.collision_type = 1
    space.add(floor, floor.shape)

    return floor


class Model:
    mode: str
    num_bodies: int = 0

    corps: LegPartBone
    right_leg: Leg
    left_leg: Leg
    floor: pymunk.Body

    pivots: list[pymunk.Body]

    def __init__(self, space: pymunk.Space(), mode: str):
        self.mode = mode
        self.floor = running_gear(space)
        self.corps = LegPartBone(space, self.iterator(), "corps", CORPS_WEIGHT, (CORPS_WIDTH, CORPS_HEIGHT),
                                 CORPS_POSITION)
        self.right_leg = Leg(space, mode, 0)
        self.left_leg = Leg(space, mode, 1)

        self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)
        self.equations = Equations()

    def iterator(self):
        self.num_bodies = self.num_bodies + 1
        return self.num_bodies

    def move_running_gear(self):
        self.floor.velocity = (-30, 0)

    def add_pivot_joints(self, space):
        right_hip_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.corps.body, self.right_leg.thigh.body,
                                                                   (self.corps.body.position.x,
                                                                    self.corps.body.position.y -
                                                                    ((1 / 2) * CORPS_HEIGHT)))
        left_hip_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.corps.body, self.left_leg.thigh.body,
                                                                  (self.corps.body.position.x,
                                                                   self.corps.body.position.y -
                                                                   ((1 / 2) * CORPS_HEIGHT)))

        hip_pivot_joint_body = LegPartsHelper.add_joint_body((self.corps.body.position.x,
                                                              self.corps.body.position.y -
                                                              ((1 / 2) * CORPS_HEIGHT)))
        space.add(hip_pivot_joint_body)
        # pivots = [right_hip_pivot_body]
        self.pivots = [hip_pivot_joint_body]
        pass


    def add_pin_joints_parts(self, space):
        LegPartsHelper.add_body_rotation_center(space, self.corps.body.position)
        # corps_temp_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.corps.body, corps_rotation_center, (0, 0),
        #                                                          (0, 0))

        LegPartsHelper.add_body_pin_joint(space, self.corps.body, self.right_leg.thigh.body,
                                          (0, (-(1 / 2) * CORPS_HEIGHT)),
                                          (0, (1 / 2) * THIGH_HEIGHT))
        LegPartsHelper.add_body_pin_joint(space, self.corps.body, self.left_leg.thigh.body,
                                          (0, (-(1 / 2) * CORPS_HEIGHT)),
                                          (0, (1 / 2) * THIGH_HEIGHT))
        LegPartsHelper.add_body_pin_joint(space, self.corps.body, self.pivots.__getitem__(0),
                                          (0, (-(1 / 2) * CORPS_HEIGHT)),
                                          (0, 0))

