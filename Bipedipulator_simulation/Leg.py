from __future__ import annotations

import pymunk.pygame_util
from pymunk import Vec2d

from Bipedipulator_simulation import LegMethodsHelper
from Bipedipulator_simulation.RelativeValues import RelativeValues
from Bipedipulator_simulation.ValuesPerPhase import Equations
from Bipedipulator_simulation.constants import CORPS_HEIGHT, THIGH_WIDTH, THIGH_HEIGHT, \
    CALF_HEIGHT, FOOT_HEIGHT, FOOT_WIDTH, THIGH_WEIGHT, FOOT_WEIGHT, CALF_WIDTH, \
    CORPS_POSITION, NUMBER_SIMULATION_STEPS, CALF_WEIGHT


class Leg:
    leg_name: str

    thigh: LegPartBone
    knee_body: pymunk.Body
    calf: LegPartBone
    ankle_body: pymunk.Body
    foot: LegPartBone

    bodies: list[pymunk.Body]

    relative_values: list[RelativeValues]
    equations: Equations

    def __init__(self, space: pymunk.Space(), leg_name: str):
        self.relative_values = []
        for i in range(0, NUMBER_SIMULATION_STEPS):
            self.relative_values.append(RelativeValues())
        print("Created relative_values =", len(self.relative_values))

        self.leg_name = leg_name
        self.equations = Equations(self.leg_name)

        self.thigh = LegPartBone(space, "thigh", THIGH_WEIGHT, (THIGH_WIDTH, THIGH_HEIGHT),
                                 (CORPS_POSITION - (0, ((CORPS_HEIGHT / 2) + (THIGH_HEIGHT / 2)))))
        self.calf = LegPartBone(space, "calf", CALF_WEIGHT, (CALF_WIDTH, CALF_HEIGHT),
                                (self.thigh.body.position - (0, ((THIGH_HEIGHT / 2) + (CALF_HEIGHT / 2)))))
        self.foot = LegPartBone(space, "foot", FOOT_WEIGHT, (FOOT_WIDTH, FOOT_HEIGHT),
                                self.calf.body.position - (-FOOT_WIDTH / 4, CALF_HEIGHT / 2 + FOOT_HEIGHT / 2))

        self.knee_body = LegMethodsHelper.add_joint_body(space, (self.thigh.body.position.x,
                                                                 self.thigh.body.position.y - (THIGH_HEIGHT / 2)))
        self.ankle_body = LegMethodsHelper.add_joint_body(space, (self.calf.body.position.x,
                                                                  self.calf.body.position.y - (CALF_HEIGHT / 2)))
        self.bodies = [self.thigh.body, self.calf.body, self.foot.body, self.knee_body, self.ankle_body]

        self.add_pivot_joints(space)
        self.add_pin_joints_parts(space)

    def add_pivot_joints(self, space: pymunk.Space()):
        LegMethodsHelper.add_body_pivot_joint(space, self.thigh.body, self.calf.body, self.knee_body.position)
        LegMethodsHelper.add_body_pivot_joint(space, self.calf.body, self.foot.body, self.ankle_body.position)

    def add_pin_joints_parts(self, space: pymunk.Space()):
        LegMethodsHelper.add_body_pin_joint(space, self.thigh.body, self.calf.body,
                                            (0, (-THIGH_HEIGHT / 2)), (0, CALF_HEIGHT / 2))
        LegMethodsHelper.add_body_pin_joint(space, self.thigh.body, self.knee_body,
                                            (0, (-THIGH_HEIGHT / 2)), (0, 0))
        LegMethodsHelper.add_body_pin_joint(space, self.calf.body, self.foot.body,
                                            (0, (-CALF_HEIGHT / 2)), (-FOOT_WIDTH / 4, FOOT_HEIGHT / 2))
        LegMethodsHelper.add_body_pin_joint(space, self.calf.body, self.ankle_body,
                                            (0, (-CALF_HEIGHT / 2)), (0, 0))


class LegPartBone:
    leg_part_name: str
    shape: pymunk.Poly
    body: pymunk.Body

    def __init__(self, space: pymunk.Space(), name, mass, size, position_vector: Vec2d):
        self.leg_part_name = name
        moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, moment)
        self.body.body_type = pymunk.Body.DYNAMIC
        self.body.position = position_vector
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.friction = 0.61
        self.shape.collision_type = 0
        # ---prevent collisions with ShapeFilter
        self.shape.filter = pymunk.ShapeFilter(group=1)

        space.add(self.body, self.shape)
