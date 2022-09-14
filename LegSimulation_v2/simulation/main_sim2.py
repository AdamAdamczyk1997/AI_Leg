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
from tabulate import tabulate
from pygame.color import THECOLORS


def table(model_object: Model.Model) -> None:
    table_content = [['Parts Name', 'Moment', 'Position_x', 'Position_y', 'Velocity_x', 'Velocity_y', ''],
                     [model_object.corps.name, model_object.corps.moment, model_object.corps.body.position.x,
                      model_object.corps.body.position.y,
                      model_object.corps.body.velocity.x, model_object.corps.body.velocity.y],
                     [model_object.thigh.name, model_object.thigh.moment, model_object.thigh.body.position.x,
                      model_object.thigh.body.position.y,
                      model_object.thigh.body.velocity.x, model_object.thigh.body.velocity.y],
                     [model_object.cale.name, model_object.cale.moment, model_object.cale.body.position.x,
                      model_object.cale.body.position.y,
                      model_object.cale.body.velocity.x, model_object.cale.body.velocity.y],
                     [model_object.foot.name, model_object.foot.moment, model_object.foot.body.position.x,
                      model_object.foot.body.position.y,
                      model_object.foot.body.velocity.x, model_object.foot.body.velocity.y]]

    print(tabulate(table_content, headers='firstrow', tablefmt='fancy_grid'))


class Simulator(object):

    def __init__(self):
        self.display_flags = 0
        self.display_size = (constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT)
        self.space = pymunk.Space()
        self.space.gravity = (0, constants.GRAVITY)
        pymunk.pygame_util.positive_y_is_up = True
        self.model_entity = Model.Model(self.space)
        self.screen = None
        self.draw_options = None

    def reset_bodies(self):
        for body in self.space.bodies:
            if not hasattr(body, 'start_position'):
                continue
            body.position = Vec2d(body.start_position)
            body.force = 0, 0
            body.torque = 0
            body.velocity = 0, 0
            body.angular_velocity = 0
            body.angle = body.start_angle

    def draw(self):
        self.screen.fill(THECOLORS["white"])  ### Clear the screen
        self.space.debug_draw(self.draw_options)  ### Draw space
        pygame.display.flip()  ### All done, lets flip the display

    def main(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.display_size, self.display_flags)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space._set_iterations(20) ### Try another value to better experience

        clock = pygame.time.Clock()
        running = True

        bodies = self.space.bodies
        print(bodies)

        balls = []
        ticks_to_next_ball = 100

        # ---prevent collisions with ShapeFilter
        shape_filter = pymunk.ShapeFilter(group=1)
        self.model_entity.corps.shape.filter = shape_filter
        self.model_entity.thigh.shape.filter = shape_filter
        self.model_entity.cale.shape.filter = shape_filter
        self.model_entity.foot.shape.filter = shape_filter

        simulate = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE)):
                    # running = False
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    # Start/stop simulation.
                    simulate = not simulate
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    # Reset.
                    simulate = False
                    self.reset_bodies()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                    self.model_entity.move_muscles(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                    self.model_entity.move_muscles(1)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                    self.model_entity.move_muscles(2)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                    self.model_entity.move_muscles(3)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_6:
                    self.model_entity.move_muscles(4)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                    self.model_entity.move_muscles(5)

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    sim1 = Simulator()
                    sim1.main()

            ticks_to_next_ball = Model.ball_controller(self.space, balls, ticks_to_next_ball)
            self.draw()

            pygame.display.set_caption(f"fps: {clock.get_fps()}")
            # Update physics
            fps = 60
            clock.tick(fps)

            dt = 1.0 / float(fps)
            if simulate:
                # for x in range(10 * iterations):  # 10 iterations to get a more stable simulation
                self.space.step(dt)
                self.reset_bodies()

            table(self.model_entity)
            print(self.space._get_iterations())

if __name__ == "__main__":
    sim = Simulator()
    sim.main()
