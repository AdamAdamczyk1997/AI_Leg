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
from pymunk import Vec2d
import LegPartBone
import self as self
from LegSimulation_v2.simulation import constants
from math import sin, cos, pi

from LegSimulation_v2.simulation.LegPartBone import LegPartBone
from LegSimulation_v2.simulation.LegPartJoint import LegPartJoint
from LegSimulation_v2.simulation.constants import JOINT_RADIUS, BONE_WIDTH, BONE_HEIGHT

random.seed(1)  # make the simulation the same each time, easier to debug
global_corps: LegPartBone


def add_floor(space):
    floor = pymunk.Segment(space.static_body, (-100, 0), (2000, 0), 5)
    floor.friction = 1.0
    space.add(floor)

    return space


def add_leg_parts(space, corps, hip, thigh, knee, cale, ankle, foot):
    patella = knee.add_patella()
    space.add(patella)

    hip_pivot_body = corps.add_body_pivot_joint(space, corps.body, thigh.body, hip.body.position)
    knee_pivot_body = thigh.add_body_pivot_joint(space, thigh.body, cale.body, knee.body.position)
    ankle_pivot_body = cale.add_body_pivot_joint(space, cale.body, foot.body, ankle.body.position)

    corps_rotation_center = corps.add_body_rotation_center(space, corps.body.position)
    corps_temp_pin_joint = corps.add_body_pin_joint(space, corps.body, corps_rotation_center, (0, 0), (0, 0))
    corps_hip_pin_joint = corps.add_body_pin_joint(space, corps.body, hip.body, (0, -70), (0, 0))
    hip_thigh_pin_joint = hip.add_body_pin_joint(space, hip.body, thigh.body, (0, 0), (0, 120))
    thigh_knee_pin_joint = thigh.add_body_pin_joint(space, thigh.body, knee.body, (0, -120), (0, 0))
    knee_cale_pin_joint = knee.add_body_pin_joint(space, knee.body, cale.body, (0, 0), (0, 120))
    cale_ankle_pin_joint = cale.add_body_pin_joint(space, cale.body, ankle.body, (0, -120), (0, 0))
    ankle_foot_pin_joint = ankle.add_body_pin_joint(space, ankle.body, foot.body, (0, 0), (-35, 25))

    thigh_muscle_front_joint = corps.add_body_limit_slide_joint(space, corps.body, cale.body, (100, -50), (5, 50),
                                                                330, 410)
    thigh_muscle_back_joint = corps.add_body_limit_slide_joint(space, corps.body, cale.body, (-100, -50), (-5, 50),
                                                               330, 410)
    cale_muscle_front_joint = cale.add_body_limit_slide_joint(space, cale.body, foot.body, (5, 100), (-20, 5), 230,
                                                              240)
    cale_muscle_back_joint = cale.add_body_limit_slide_joint(space, cale.body, foot.body, (-5, 100), (-50, 5), 230,
                                                             260)

    return space


class Model:
    corps: LegPartBone
    hip: LegPartJoint
    thigh: LegPartBone
    knee: LegPartJoint
    cale: LegPartBone
    ankle: LegPartJoint
    foot: LegPartBone
    time: int = 0

    def __init__(self, space):
        self.corps = LegPartBone(space, "korpus", 100, (200, 100), Vec2d(1000, 700))
        self.hip = LegPartJoint(space, "hip", 10, JOINT_RADIUS, (self.corps.body.position - (0, 70)))
        self.thigh = LegPartBone(space, "thigh", 50, (BONE_WIDTH, BONE_HEIGHT),
                                 (self.hip.body.position - (0, 120)))
        self.knee = LegPartJoint(space, "knee", 10, JOINT_RADIUS, (self.thigh.body.position - (0, 120)))
        self.cale = LegPartBone(space, "cale", 50, (BONE_WIDTH, BONE_HEIGHT),
                                (self.knee.body.position - (0, 120)))
        self.ankle = LegPartJoint(space, "ankle", 10, JOINT_RADIUS, (self.cale.body.position - (0, 120)))
        self.foot = LegPartBone(space, "foot", 30, (100, 10), (self.ankle.body.position + (40, -25)))
        add_leg_parts(space, self.corps, self.hip, self.thigh, self.knee, self.cale, self.ankle, self.foot)
        add_floor(space)


def add_ball(space):
    """Add a ball to the given space at a random position"""
    mass = 3
    radius = 25
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
    body = pymunk.Body(mass, inertia)
    x = random.randint(400, 1500)
    body.position = x, 900
    shape = pymunk.Circle(body, radius, (0, 0))
    shape.friction = 1
    space.add(body, shape)
    return shape
