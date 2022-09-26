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
from LegSimulation_v2.simulation import constants, LegPartsHelper
from math import sin, cos, pi, sqrt

from LegSimulation_v2.simulation.LegPartBone import LegPartBone
from LegSimulation_v2.simulation.constants import JOINT_RADIUS, CORPS_WIDTH, CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALE_WIDTH, CALE_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, MIN_CORPS_THIGH, MIN_CMFJ, MIN_CMBJ, PATELLA_HEIGHT, \
    PATELLA_WIDTH, MIN_PTJ, MIN_PCJ, CORPS_WEIGHT, THIGH_WEIGHT, FOOT_WEIGHT, PATELLA_WEIGHT, CALE_WEIGHT, \
    HANDLER_LENGTH, LEG_HEIGHT, FLOOR_HEIGHT

random.seed(1)  # make the simulation the same each time, easier to debug


def running_gear(space):
    floor = pymunk.Body()
    floor.body_type = pymunk.Body.KINEMATIC
    floor.shape = pymunk.Segment(floor, (0, 0), (100000, 0), FLOOR_HEIGHT)
    floor.shape.friction = 0.5
    # floor.shape.collision_type = 1
    space.add(floor, floor.shape)

    return floor


class Model:
    num_bodies: int = 0
    corps: LegPartBone
    thigh: LegPartBone
    cale: LegPartBone
    foot: LegPartBone
    patella_thigh_part: LegPartBone
    patella_cale_part: LegPartBone
    pivots: list[pymunk.Body]
    muscles: list[DampedSpring | SlideJoint]
    bodies: list[pymunk.Body]
    time: int = 0
    teacher_holder: list[SlideJoint]
    floor: pymunk.Body

    def __init__(self, space: pymunk.Space()):
        self.floor = running_gear(space)
        self.corps = LegPartBone(space, self.iterator(), "corps", CORPS_WEIGHT, (CORPS_WIDTH, CORPS_HEIGHT),
                                 Vec2d(1000, LEG_HEIGHT + 10))
        self.thigh = LegPartBone(space, self.iterator(), "thigh", THIGH_WEIGHT, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (self.corps.body.position - (
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

        add_pin_joints_parts(space, self.corps, self.thigh, self.patella_thigh_part, self.cale, self.patella_cale_part,
                             self.foot)

        self.muscles = self.add_muscles_joints(space)

        self.bodies = [self.corps.body, self.thigh.body, self.patella_thigh_part.body, self.patella_cale_part.body,
                       self.cale.body, self.foot.body]

        # space._remove_body(self.thigh.body)
        # shape = pymunk.Poly.create_box(self.thigh.body, (PATELLA_WIDTH, PATELLA_HEIGHT))
        #
        # self.thigh.body.shapes.add(shape)
        # space.reindex_shapes_for_body(self.thigh.body)
        #
        # space.add(self.thigh.body, shape)

        # self.teacher = Teacher.Teacher(space, 8, "teacher", (CORPS_WIDTH, 30), self.corps.body.position + (0, HANDLER_LENGTH))
        # self.teacher.add_holder(space)
        # self.teacher_holder = self.add_holder_joint(space)

    def tick(self):
        self.corps.part_vector_position = self.corps.body.position
        self.thigh.part_vector_position = self.thigh.body.position
        self.cale.part_vector_position = self.cale.body._get_position()
        self.foot.part_vector_position = self.foot.body._get_position()
        # self.corps.part_vector_position.show_location()
        # self.thigh.part_vector_position.show_location()
        # self.cale.part_vector_position.show_location()
        # self.foot.part_vector_position.show_location()
        pass

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
        self.floor.velocity = (-30, 0)
        self.corps.body.body_type = pymunk.Body.KINEMATIC

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
        hip_pivot_body = LegPartsHelper.add_body_pivot_joint(space, self.corps.body, self.thigh.body,
                                                             (self.corps.part_vector_position.x,
                                                              self.corps.part_vector_position.y -
                                                              ((1 / 2) * CORPS_HEIGHT)))
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
        pivots = [hip_pivot_body, knee_pivot_body, ankle_pivot_body,
                  patella_thigh_pivot_body, patella_cale_pivot_body]
        return pivots

    def add_muscles_joints(self, space):
        cale_muscle_front_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.cale.body, self.foot.body,
                                                  (20, ((1 / 2) * CALE_HEIGHT)), (20, (0.5 * FOOT_HEIGHT)),
                                                  0.5 * CALE_HEIGHT, 20000, 200)
        cale_muscle_back_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.cale.body, self.foot.body,
                                                  (-20, ((1 / 2) * CALE_HEIGHT)), (-20, 0.5 * FOOT_HEIGHT),
                                                  0.5 * CALE_HEIGHT, 20000, 200)
        thigh_cale_muscle_front_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.thigh.body, self.cale.body,
                                                  (20, (0.5 * THIGH_HEIGHT)), (20, (0.5 * CALE_HEIGHT)),
                                                  0.5 * THIGH_HEIGHT, 30000, 100)
        thigh_cale_muscle_back_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.thigh.body, self.cale.body,
                                                  (-20, (0.5 * THIGH_HEIGHT)), (-20, (0.5 * CALE_HEIGHT)),
                                                  0.5 * THIGH_HEIGHT, 30000, 100)
        thigh_corps_muscle_front_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.corps.body, self.thigh.body,
                                                  (0.5 * CORPS_WIDTH, (-0.5 * CORPS_HEIGHT)), (0, (0.25 * THIGH_HEIGHT)),
                                                  0.5 * MIN_CMFJ, 10000, 100)
        thigh_cops_muscle_back_joint = \
            LegPartsHelper.add_body_dumped_spring(space, self.corps.body, self.thigh.body,
                                                  (-0.5 * CORPS_WIDTH, (-0.5 * CORPS_HEIGHT)), (0, (0.25 * THIGH_HEIGHT)),
                                                  0.5 * MIN_CMBJ, 10000, 100)

        patella_thigh_muscle_joint = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.patella_thigh_part.body, self.thigh.body,
                                                      (0.5 * PATELLA_WIDTH, 0), (0.5 * THIGH_WIDTH,
                                                                                 -(0.25 * THIGH_HEIGHT)),
                                                      MIN_PTJ, MIN_PTJ)
        patella_cale_muscle_joint = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.patella_cale_part.body, self.cale.body,
                                                      (0.5 * PATELLA_WIDTH, 0),
                                                      (0.5 * CALE_WIDTH, (0.25 * CALE_HEIGHT)),
                                                      MIN_PCJ, MIN_PCJ)
        patellas_muscle_joint_1 = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.patella_thigh_part.body, self.patella_cale_part.body,
                                                      (0.5 * PATELLA_WIDTH, 0), (0.5 * PATELLA_WIDTH, 0),
                                                      (self.patella_thigh_part.part_vector_position.first_y -
                                                       self.patella_cale_part.part_vector_position.first_y), 70)
        patellas_muscle_joint_2 = \
            LegPartsHelper.add_body_limit_slide_joint(space, self.patella_thigh_part.body, self.patella_cale_part.body,
                                                      (-0.5 * PATELLA_WIDTH, 0), (-0.5 * PATELLA_WIDTH, 0),
                                                      (self.patella_thigh_part.part_vector_position.first_y -
                                                       self.patella_cale_part.part_vector_position.first_y), 70)

        slides_joints = [cale_muscle_front_joint, cale_muscle_back_joint,
                         thigh_cale_muscle_front_joint, thigh_cale_muscle_back_joint,
                         thigh_corps_muscle_front_joint, thigh_cops_muscle_back_joint,
                         patellas_muscle_joint_1, patellas_muscle_joint_2,
                         patella_thigh_muscle_joint,
                         patella_cale_muscle_joint
                         ]
        return slides_joints


def add_pin_joints_parts(space, corps, thigh, patella_thigh_part, cale, patella_cale_part, foot):
    corps_rotation_center = LegPartsHelper.add_body_rotation_center(space, corps.body.position)
    # corps_temp_pin_joint = LegPartsHelper.add_body_pin_joint(space, corps.body, corps_rotation_center, (0, 0), (0, 0))
    hip_pin_joint = LegPartsHelper.add_body_pin_joint(space, corps.body, thigh.body,
                                                      (0, (-(1 / 2) * CORPS_HEIGHT)), (0, (1 / 2) * THIGH_HEIGHT))
    # patella_thigh_part_pin_joint = LegPartsHelper.add_body_pin_joint(space, patella_thigh_part.body, thigh.body,
    #                                                                  (-(1 / 2) * PATELLA_WIDTH, 0),
    #                                                                  ((0.5 * THIGH_WIDTH), -((7 / 16) * THIGH_HEIGHT)))
    knee_pin_joint = LegPartsHelper.add_body_pin_joint(space, thigh.body, cale.body,
                                                       (0, (-(1 / 2) * THIGH_HEIGHT)), (0, (1 / 2) * CALE_HEIGHT))
    # patella_cale_part_pin_joint = LegPartsHelper.add_body_pin_joint(space, patella_cale_part.body, cale.body,
    #                                                                 (-(1 / 2) * PATELLA_WIDTH, 0),
    #                                                                 ((0.5 * CALE_WIDTH), ((7 / 16) * CALE_HEIGHT)))
    ankle_pin_joint = LegPartsHelper.add_body_pin_joint(space, cale.body, foot.body,
                                                        (0, (-(1 / 2) * CALE_HEIGHT)), (0, (1 / 2) * FOOT_HEIGHT))

    return space
