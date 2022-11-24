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
from LegSimulation_v2.simulation_v2 import constants, LegPartsHelper
from math import sin, cos, pi, sqrt

from LegSimulation_v2.simulation_v2.LegPartBone import LegPartBone
from LegSimulation_v2.simulation_v2.constants import JOINT_RADIUS, CORPS_WIDTH, CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALE_WIDTH, CALE_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, MIN_CORPS_THIGH, MIN_CMFJ, MIN_CMBJ, PATELLA_HEIGHT, \
    PATELLA_WIDTH, MIN_PTJ, MIN_PCJ, CORPS_WEIGHT, THIGH_WEIGHT, FOOT_WEIGHT, PATELLA_WEIGHT, CALE_WEIGHT, \
    HANDLER_LENGTH, LEG_HEIGHT, FLOOR_HEIGHT, CORPS_POSITION
from LegSimulation_v2.simulation_v2.Leg import Leg

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
    num_bodies: int = 0
    corps: LegPartBone
    right_leg: Leg
    left_leg: Leg

    muscles: list[DampedSpring | SlideJoint]
    bodies: list[pymunk.Body]
    time: int = 0
    floor: pymunk.Body
    pivots: list[pymunk.Body]

    left_thigh: pymunk.Body
    left_cale: pymunk.Body
    left_foot: pymunk.Body

    def __init__(self, space: pymunk.Space(), mode: str):
        self.floor = running_gear(space)
        self.corps = LegPartBone(space, self.iterator(), "corps", CORPS_WEIGHT, (CORPS_WIDTH, CORPS_HEIGHT),
                                 CORPS_POSITION)
        self.right_leg = Leg(space, mode, 0)
        self.left_leg = Leg(space, mode, 1)

        self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)
        self.bodies = [self.corps.body, self.right_leg.bodies]
        if mode == "AI mode":
            self.muscles = self.add_muscles_joints(space)

    def iterator(self):
        self.num_bodies = self.num_bodies + 1
        return self.num_bodies

    def move_muscles(self, index, dt: float):
        if index == 0:
            self.muscles.__getitem__(index).stiffness += 100
            self.muscles.__getitem__(index + 1).stiffness -= 100
        elif index == 1:
            self.muscles.__getitem__(index).stiffness += 100
            self.muscles.__getitem__(index - 1).stiffness -= 100
        elif index == 2:
            self.muscles.__getitem__(index).stiffness += 100
            self.muscles.__getitem__(index + 1).stiffness -= 100
        elif index == 3:
            self.muscles.__getitem__(index).stiffness += 100
            self.muscles.__getitem__(index - 1).stiffness -= 100
        elif index == 4:
            self.muscles.__getitem__(index).stiffness += 100
            self.muscles.__getitem__(index + 1).stiffness -= 100
        elif index == 5:
            self.muscles.__getitem__(index).stiffness += 100
            self.muscles.__getitem__(index - 1).stiffness -= 100
        pass

    def move_running_gear(self):
        self.floor.velocity = (-20, 0)

    def movement_scenario(self, up: bool) -> bool:
        temp_up = up
        if not up:
            self.corps.body.velocity = (0, -5)
            self.move_muscles(0, 0.1)
            self.move_muscles(3, 0.1)
            self.move_muscles(5, 0.1)
            if self.corps.body.position.y <= (LEG_HEIGHT - 10):
                temp_up = not up
        elif up:
            self.corps.body.velocity = (0, 5)
            self.move_muscles(1, 0.1)
            if self.muscles.__getitem__(2).min >= THIGH_HEIGHT:
                self.move_muscles(2, 0.1)
            self.move_muscles(4, 0.1)
            if self.corps.body.position.y >= (LEG_HEIGHT + 10):
                temp_up = not up

        return temp_up

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

    def add_muscles_joints(self, space):
        # Muscles are added only to right leg
        cale_muscle_front_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.right_leg.cale.body, self.right_leg.foot.body,
                                                  (20, ((1 / 2) * CALE_HEIGHT)), (20, (0.5 * FOOT_HEIGHT)),
                                                  0.5 * CALE_HEIGHT, 20000, 200)
        cale_muscle_back_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.right_leg.cale.body, self.right_leg.foot.body,
                                                  (-20, ((1 / 2) * CALE_HEIGHT)), (-20, 0.5 * FOOT_HEIGHT),
                                                  0.5 * CALE_HEIGHT, 20000, 200)
        thigh_cale_muscle_front_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.right_leg.thigh.body, self.right_leg.cale.body,
                                                  (20, (0.5 * THIGH_HEIGHT)), (20, (0.5 * CALE_HEIGHT)),
                                                  0.5 * THIGH_HEIGHT, 30000, 100)
        thigh_cale_muscle_back_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.right_leg.thigh.body, self.right_leg.cale.body,
                                                  (-20, (0.5 * THIGH_HEIGHT)), (-20, (0.5 * CALE_HEIGHT)),
                                                  0.5 * THIGH_HEIGHT, 30000, 100)

        patella_thigh_muscle_joint = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.right_leg.patella_thigh_part.body,
                                                      self.right_leg.thigh.body,
                                                      (0.5 * PATELLA_WIDTH, 0),
                                                      (0.5 * THIGH_WIDTH, -(0.25 * THIGH_HEIGHT)),
                                                      MIN_PTJ, MIN_PTJ)
        patella_cale_muscle_joint = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.right_leg.patella_cale_part.body,
                                                      self.right_leg.cale.body,
                                                      (0.5 * PATELLA_WIDTH, 0),
                                                      (0.5 * CALE_WIDTH, (0.25 * CALE_HEIGHT)),
                                                      MIN_PCJ, MIN_PCJ)
        patellas_muscle_joint_1 = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.right_leg.patella_thigh_part.body,
                                                      self.right_leg.patella_cale_part.body,
                                                      (0.5 * PATELLA_WIDTH, 0), (0.5 * PATELLA_WIDTH, 0),
                                                      (self.right_leg.patella_thigh_part.body.position.y -
                                                       self.right_leg.patella_cale_part.body.position.y),
                                                      70)
        patellas_muscle_joint_2 = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.right_leg.patella_thigh_part.body,
                                                      self.right_leg.patella_cale_part.body,
                                                      (-0.5 * PATELLA_WIDTH, 0), (-0.5 * PATELLA_WIDTH, 0),
                                                      (self.right_leg.patella_thigh_part.body.position.y -
                                                       self.right_leg.patella_cale_part.body.position.y),
                                                      70)

        thigh_corps_muscle_front_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.corps.body, self.right_leg.thigh.body,
                                                  (0.5 * CORPS_WIDTH, (-0.5 * CORPS_HEIGHT)),
                                                  (0, (0.25 * THIGH_HEIGHT)),
                                                  0.5 * MIN_CMFJ, 10000, 100)
        thigh_cops_muscle_back_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.corps.body, self.right_leg.thigh.body,
                                                  (-0.5 * CORPS_WIDTH, (-0.5 * CORPS_HEIGHT)),
                                                  (0, (0.25 * THIGH_HEIGHT)),
                                                  0.5 * MIN_CMBJ, 10000, 100)

        slides_joints = [cale_muscle_front_joint, cale_muscle_back_joint,
                         thigh_cale_muscle_front_joint, thigh_cale_muscle_back_joint,
                         patellas_muscle_joint_1, patellas_muscle_joint_2,
                         patella_thigh_muscle_joint,
                         patella_cale_muscle_joint,
                         thigh_corps_muscle_front_joint, thigh_cops_muscle_back_joint
                         ]
        return slides_joints

    def add_pin_joints_parts(self, space):
        corps_rotation_center = LegPartsHelper.add_body_rotation_center(space, self.corps.body.position)
        # corps_temp_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.corps.body, corps_rotation_center, (0, 0),
        #                                                          (0, 0))

        right_hip_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.corps.body, self.right_leg.thigh.body,
                                                                (0, (-(1 / 2) * CORPS_HEIGHT)),
                                                                (0, (1 / 2) * THIGH_HEIGHT))
        left_hip_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.corps.body, self.left_leg.thigh.body,
                                                               (0, (-(1 / 2) * CORPS_HEIGHT)),
                                                               (0, (1 / 2) * THIGH_HEIGHT))
        r_hip_pin_joint = LegPartsHelper.add_body_pin_joint(space, self.corps.body, self.pivots.__getitem__(0),
                                                            (0, (-(1 / 2) * CORPS_HEIGHT)),
                                                            (0, 0))

        pin_joints = [corps_rotation_center, right_hip_pin_joint]

        return pin_joints
