from __future__ import annotations

import random

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

from Bipedipulator_simulation import LegMethodsHelper
from Bipedipulator_simulation.RelativeValues import RelativeValues
from Bipedipulator_simulation.ValuesPerPhase import Equations
from Bipedipulator_simulation.constants import CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALF_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, THIGH_WEIGHT, FOOT_WEIGHT, CALF_WIDTH, \
    CORPS_POSITION, AMOUNT_SCENARIOS

random.seed(1)  # make the simulation the same each time, easier to debug


class Leg:
    name: str

    thigh: LegPartBone
    knee_body: pymunk.Body
    calf: LegPartBone
    ankle_body: pymunk.Body
    foot: LegPartBone

    bodies: list[pymunk.Body]

    relative_values: list[RelativeValues]
    equations: Equations

    def __init__(self, space: pymunk.Space(), name: str):
        self.relative_values = []
        for i in range(0, AMOUNT_SCENARIOS + 1):
            self.relative_values.append(RelativeValues())
        print("Created relative_values =", len(self.relative_values))
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

        self.knee_body = LegMethodsHelper.add_joint_body((self.thigh.body.position.x,
                                                          self.thigh.body.position.y -
                                                          ((1 / 2) * THIGH_HEIGHT)))
        self.ankle_body = LegMethodsHelper.add_joint_body((self.calf.body.position.x,
                                                           self.calf.body.position.y -
                                                           ((1 / 2) * CALF_HEIGHT)))
        self.bodies = [self.thigh.body, self.calf.body, self.foot.body, self.knee_body, self.ankle_body]

        self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)

    def add_pivot_joints(self, space):
        LegMethodsHelper.add_body_pivot_joint(space, self.thigh.body, self.calf.body,
                                              self.knee_body.position)
        LegMethodsHelper.add_body_pivot_joint(space, self.calf.body, self.foot.body,
                                              self.ankle_body.position)

        space.add(self.knee_body, self.ankle_body)

    def add_pin_joints_parts(self, space):
        LegMethodsHelper.add_body_pin_joint(space, self.thigh.body, self.calf.body,
                                            (0, (-(1 / 2) * THIGH_HEIGHT)), (0, (1 / 2) * CALF_HEIGHT))
        LegMethodsHelper.add_body_pin_joint(space, self.thigh.body, self.knee_body,
                                            (0, (-(1 / 2) * THIGH_HEIGHT)), (0, 0))
        LegMethodsHelper.add_body_pin_joint(space, self.calf.body, self.foot.body,
                                            (0, (-(1 / 2) * CALF_HEIGHT)),
                                            ((-1 / 4) * FOOT_WIDTH, (1 / 2) * FOOT_HEIGHT))
        LegMethodsHelper.add_body_pin_joint(space, self.calf.body, self.ankle_body,
                                            (0, (-(1 / 2) * CALF_HEIGHT)), (0, 0))


class LegPartBone:
    name: str
    mass: float
    size: tuple[int, int]
    moment: float
    shape: pymunk.Poly
    shape_friction: float
    body: pymunk.Body

    def __init__(self, space: pymunk.Space(), name, mass, size, vector: Vec2d):
        self.name = name
        self.mass = mass
        self.size = size
        self.moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, self.moment)
        self.body.body_type = pymunk.Body.DYNAMIC
        self.body.position = vector
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 0.61
        self.shape.collision_type = 0
        # ---prevent collisions with ShapeFilter
        self.shape.filter = pymunk.ShapeFilter(group=1)

        space.add(self.body, self.shape)
