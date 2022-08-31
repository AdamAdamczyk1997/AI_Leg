import sys

import pygame
import pymunk
from numpy import equal

import constants
import LegPartBone
import Model
from pymunk import Vec2d

import constants
import model
import random
import sys
import pygame
import pymunk
import pymunk.pygame_util
import numpy as np
import matplotlib.pyplot as plt

from LegSimulation_v2.simulation import LegPartJoint
from LegSimulation_v2.simulation.Location import Location

pygame.init()
SCREEN = pygame.display.set_mode((constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT))
CLOCK = pygame.time.Clock()

space = pymunk.Space()
model_entity = Model.Model(space)

pymunk.pygame_util.positive_y_is_up = True
space.gravity = Vec2d(0, constants.GRAVITY)


def main() -> None:
    pygame.display.set_caption("Pysics simulation of leg model")

    bodies = space.bodies
    print(bodies)

    balls = []
    draw_options = pymunk.pygame_util.DrawOptions(SCREEN)
    ticks_to_next_ball = 100

    mouse_joint = None
    mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_joint is not None:
                    space.remove(mouse_joint)
                    mouse_joint = None

                p = Vec2d(*event.pos)
                hit = space.point_query_nearest(p, 5, pymunk.ShapeFilter())
                if hit is not None and hit.shape.body.body_type == pymunk.Body.DYNAMIC:
                    shape = hit.shape
                    # Use the closest point on the surface if the click is outside
                    # of the shape.
                    if hit.distance > 0:
                        nearest = hit.point
                    else:
                        nearest = p
                    mouse_joint = pymunk.PivotJoint(
                        mouse_body, shape.body, (0, 0), shape.body.world_to_local(nearest)
                    )
                    mouse_joint.max_force = 50000
                    mouse_joint.error_bias = (1 - 0.15) ** 60
                    space.add(mouse_joint)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                model_entity.move_muscles(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                model_entity.move_muscles(1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                model_entity.move_muscles(2)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                model_entity.move_muscles(3)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                model_entity.move_muscles(4)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                model_entity.move_muscles(5)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                model_entity.release()

            # and event.key == pygame.K_LEFT:
            #     if Model.Model.corps.body.velocity = (-600, 0)
            # elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
            #     player_body.velocity = 0, 0
            #
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            #     player_body.velocity = (600, 0)
            # elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
            #     player_body.velocity = 0, 0

        #model_entity.tick()
        ticks_to_next_ball = Model.ball_controller(space, balls, ticks_to_next_ball)

        space.step(1.0 / 60)
        space.debug_draw(draw_options)
        pygame.display.flip()
        CLOCK.tick(60)
        model_entity.time = CLOCK.get_time()

        pygame.display.set_caption("fps: {CLOCK.get_fps()}")
        SCREEN.fill(pygame.Color("white"))

        # model_object.thigh_muscle_front_joint.shorten(Vec2d(0, 10))
        # model_object.foot.get_location()


if __name__ == "__main__":
    main()
