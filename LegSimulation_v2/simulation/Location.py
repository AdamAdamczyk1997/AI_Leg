from __future__ import annotations
from typing import List
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
    x: int
    y: int
    location_history: List[int, int, int]
    records_amount: int = 0

    def __init__(self, first_x: int, first_y: int, tick: int):
        """Construct a point with x, y coordinates."""
        self.x = first_x
        self.y = first_y
        self.location_history = [first_x, first_y, tick]
        self.records_amount = 1

    def change_location(self, next_x: int, next_y: int, tick: int) -> Location:
        self.records_amount += 1
        self.location_history.append(next_x, next_y, tick)
        self.x = next_x
        self.y = next_y
        return self


