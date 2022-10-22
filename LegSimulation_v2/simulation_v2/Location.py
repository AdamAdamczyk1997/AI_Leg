from __future__ import annotations
from typing import List, Tuple
import random
import pymunk
import pymunk.pygame_util
# from kivy.graphics import Quad, Triangle
from pygame import Color
from pymunk import Vec2d
import numpy

import constants

random.seed(1)  # make the simulation the same each time, easier to debug


class Location:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float
    first_x: float
    first_y: float
    body_position: Vec2d
    location_history: List[Vec2d]
    records_amount: int = 0
    tick: List[int]

    def __init__(self, first_vec: pymunk.Vec2d):
        """Construct a point with x, y coordinates."""
        self.body_position = Vec2d(*first_vec)
        self.first_x = first_vec[0]
        self.first_y = first_vec[1]
        self.x = self.first_x
        self.y = self.first_y
        self.location_history = [self.body_position]
        self.records_amount = 1

    def change_location(self, body_location):
        self.location_history.append(Vec2d(*body_location))
        self.x = body_location[0]
        self.y = body_location[1]
        self.records_amount = self.records_amount + 1

    def get_current_location(self) -> Vec2d:
        return self.body_position

    def show_location(self) -> None:
        print(self.x, self.y)
