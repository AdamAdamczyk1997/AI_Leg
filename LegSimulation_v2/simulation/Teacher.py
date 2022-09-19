import math
import sys

import pygame
import pymunk
from numpy import equal

import constants
import LegPartBone
import Model
from pymunk import Vec2d, Poly, Body

import constants
import model
import random
import sys
import pygame
import pymunk
import pymunk.pygame_util
import numpy as np
import matplotlib.pyplot as plt

from LegSimulation_v2.simulation.Location import Location


class Teacher:
    """An individual subject in the simulation."""
    id: int
    name: str
    mass: float
    size: tuple[int, int]
    moment: float
    shape: Poly
    part_vector_position: Location
    body: Body
    floor: Body

    # helper: LegPartsHelper

    def __init__(self, space: pymunk.Space(), body_id, name, size, vector: Vec2d):
        self.id = body_id
        self.name = name
        self.body = pymunk.Body()
        self.body.body_type = pymunk.Body.STATIC
        self.body.position = vector
        self.shape = pymunk.Poly.create_box(self.body, size)
        self.body_rotation_limit = None
        self.body_rotation_center = None
        self.part_vector_position = Location(vector)
        self.floor = self.running_gear(space)

        space.add(self.body, self.shape)

    def add_holder(self, space):
        slide = pymunk.Segment(space.static_body, (-100, self.body.position.y), (2000, self.body.position.y), 2)
        slide.friction = 0.30
        space.add(slide)

        return space

    def running_gear(self, space):
        floor = pymunk.Body()
        floor.body_type = pymunk.Body.KINEMATIC
        floor.shape = pymunk.Segment(floor, (0, 0), (100000, 0), 5)
        floor.shape.friction = 1.0
        space.add(floor, floor.shape)

        return floor
