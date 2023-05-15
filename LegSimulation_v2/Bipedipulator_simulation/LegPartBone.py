from __future__ import annotations

import pymunk
from pymunk import Poly, Vec2d, Body


class LegPartBone:
    """An individual subject in the simulation."""
    name: str
    mass: float
    size: tuple[int, int]
    moment: float
    shape: Poly
    shape_friction: float
    body: Body

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

