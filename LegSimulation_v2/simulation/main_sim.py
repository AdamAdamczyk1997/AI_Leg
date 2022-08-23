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


def ball_controller(space, balls: [], ticks_to_next_ball):
    ticks_to_next_ball -= 1
    if ticks_to_next_ball <= 0:
        ticks_to_next_ball = 1000
        ball_shape = Model.add_ball(space)
        balls.append(ball_shape)

    balls_to_remove = []
    for ball in balls:
        if ball.body.position.y == constants.MIN_Y:
            balls_to_remove.append(ball)

    for ball in balls_to_remove:
        space.remove(ball, ball.body)
        balls.remove(ball)

    return ticks_to_next_ball


def main(model_object, space_object) -> None:
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT))
    pygame.display.set_caption("Pysics simulation of leg model")
    CLOCK = pygame.time.Clock()
    pymunk.pygame_util.positive_y_is_up = True

    space_object.gravity = Vec2d(0, constants.GRAVITY)

    balls = []
    draw_options = pymunk.pygame_util.DrawOptions(SCREEN)
    ticks_to_next_ball = 100

    mouse_joint = None
    mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit(0)
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            #     if Model.Model.corps.body.velocity = (-600, 0)
            # elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
            #     player_body.velocity = 0, 0
            #
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            #     player_body.velocity = (600, 0)
            # elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
            #     player_body.velocity = 0, 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_joint is not None:
                    space_object.remove(mouse_joint)
                    mouse_joint = None

                p = Vec2d(*event.pos)
                hit = space_object.point_query_nearest(p, 5, pymunk.ShapeFilter())
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
                    space_object.add(mouse_joint)

            elif event.type == pygame.MOUSEBUTTONUP:
                if mouse_joint is not None:
                    space_object.remove(mouse_joint)
                    mouse_joint = None

        model_object.thigh_muscle_front_joint.shorten(space_object, Vec2d(0, -20))

        pygame.display.update()

        SCREEN.fill(pygame.Color("white"))

        ticks_to_next_ball = ball_controller(space_object, balls, ticks_to_next_ball)
        space_object.debug_draw(draw_options)

        space_object.step(1 / 60.0)

        pygame.display.flip()
        CLOCK.tick(50)
        model_object.time = CLOCK.get_time()
        pygame.display.set_caption(f"fps: {CLOCK.get_fps()}")
        # model_entity.corps.Location.change_location()
        model_object.foot.position.get_current_location()


if __name__ == "__main__":
    world = pymunk.Space()
    model_entity = Model.Model(world)
    main(model_entity, world)
