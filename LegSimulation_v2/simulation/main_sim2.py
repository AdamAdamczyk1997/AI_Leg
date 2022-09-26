import math
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

from LegSimulation_v2.simulation import LegPartsHelper
from LegSimulation_v2.simulation.Location import Location
from tabulate import tabulate
from pygame.color import THECOLORS
import numpy as np
import pymunk.matplotlib_util
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def table(model_object: Model.Model) -> None:
    table_content = [['Id', 'Parts Name', 'Moment', 'Position_x', 'Position_y', 'Velocity_x', 'Velocity_y', ''],
                     [model_object.corps.id, model_object.corps.name, model_object.corps.moment,
                      model_object.corps.body.position.x,
                      model_object.corps.body.position.y,
                      model_object.corps.body.velocity.x, model_object.corps.body.velocity.y],
                     [model_object.thigh.id, model_object.thigh.name, model_object.thigh.moment,
                      model_object.thigh.body.position.x,
                      model_object.thigh.body.position.y,
                      model_object.thigh.body.velocity.x, model_object.thigh.body.velocity.y],
                     [model_object.cale.id, model_object.cale.name, model_object.cale.moment,
                      model_object.cale.body.position.x,
                      model_object.cale.body.position.y,
                      model_object.cale.body.velocity.x, model_object.cale.body.velocity.y],
                     [model_object.foot.id, model_object.foot.name, model_object.foot.moment,
                      model_object.foot.body.position.x,
                      model_object.foot.body.position.y,
                      model_object.foot.body.velocity.x, model_object.foot.body.velocity.y]]

    print(tabulate(table_content, headers='firstrow', tablefmt='fancy_grid'))
    print('Amount of bodies =', model_object.num_bodies)


def calculate_distance(p1, p2):
    return math.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)


def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def limit_velocity(bodies: list[pymunk.Body], gravity, damping, dt):
    for x in range(len(bodies)):
        max_velocity = 100
        pymunk.Body.update_velocity(bodies[x], gravity, damping, dt)
        if bodies[x].velocity.length > max_velocity:
            bodies[x].velocity = bodies[x].velocity * 0.99


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
        self.filter()

    def reset_bodies(self, dt: float):
        for body in self.space.bodies:
            body.force = 0, 0
            body.torque = 0
            body.velocity = 0, 0
            body.angular_velocity = 0
            body.angle = body.start_angle

    def draw(self, line):
        self.screen.fill(THECOLORS["white"])  ### Clear the screen
        if line:
            pygame.draw.line(self.screen, "black", line[0], line[1], 3)
        self.space.debug_draw(self.draw_options)  ### Draw space
        pygame.display.flip()  ### All done, lets flip the display

    def filter(self):
        # ---prevent collisions with ShapeFilter
        shape_filter = pymunk.ShapeFilter(group=1)
        self.model_entity.corps.shape.filter = shape_filter
        self.model_entity.thigh.shape.filter = shape_filter
        self.model_entity.patella_thigh_part.shape.filter = shape_filter
        self.model_entity.cale.shape.filter = shape_filter
        self.model_entity.patella_cale_part.shape.filter = shape_filter
        self.model_entity.foot.shape.filter = shape_filter

    def main(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.display_size, self.display_flags)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        # ax = plt.axes(xlim=(0, 700), ylim=(0, 1000))
        # self.draw_options = pymunk.matplotlib_util.DrawOptions(ax)
        self.space._set_iterations(10)  ### Try another value to better experience

        clock = pygame.time.Clock()
        running = True

        print(self.space.bodies)

        simulate = False
        print_time = 0
        pressed_k_left = False
        pressed_k_right = False
        pressed_k_a = False
        force = 0.0
        collision_handler = False
        stop = False
        up = False

        while running:
            line = None

            fps = 60
            clock.tick(fps)
            dt = 1.0 / float(fps)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.QUIT or (
                            event.key in (pygame.K_q, pygame.K_ESCAPE)):
                        # running = False
                        sys.exit(0)

                    elif event.key == pygame.K_RIGHT:
                        pressed_k_right = not pressed_k_right

                    elif event.key == pygame.K_DOWN:
                        x = self.model_entity.corps.body.position.x + (0.5 * constants.CORPS_HEIGHT)
                        y = self.model_entity.corps.body.position.y
                        self.model_entity.corps.body.apply_force_at_local_point((0, -50000), (x, y))

                    # Start/stop simulation!!!!!!!!!!!!!!!!!!!!!!!!!.
                    elif event.key == pygame.K_s:
                        simulate = not simulate
                    elif event.key == pygame.K_a:
                        pressed_k_a = not pressed_k_a

                    # hold the simulation
                    elif event.key == pygame.K_r:
                        # Reset.
                        simulate = False
                    # Moving muscles
                    elif event.key == pygame.K_4:
                        self.model_entity.move_muscles(0, dt)
                    elif event.key == pygame.K_3:
                        self.model_entity.move_muscles(1, dt)
                    elif event.key == pygame.K_5:
                        self.model_entity.move_muscles(2, dt)
                    elif event.key == pygame.K_2:
                        self.model_entity.move_muscles(3, dt)
                    elif event.key == pygame.K_6:
                        self.model_entity.move_muscles(4, dt)
                    elif event.key == pygame.K_1:
                        self.model_entity.move_muscles(5, dt)
                    # Start new simulation
                    elif event.key == pygame.K_n:
                        sim1 = Simulator()
                        sim1.main()

                    if pygame.key.get_pressed()[pygame.K_LEFT]:
                        pressed_k_left = not pressed_k_left

            if pressed_k_left:
                x = self.model_entity.corps.body.position.x + (0.5 * constants.CORPS_WIDTH)
                y = self.model_entity.corps.body.position.y
                self.model_entity.corps.body.apply_force_at_local_point((force, 0), (x, y))
                force = force - 5

            temp_up = False
            if pressed_k_right:
                temp_up = self.model_entity.movement_scenario(up)

            up = temp_up

            if pressed_k_a:
                self.model_entity.move_running_gear()

            # ticks_to_next_ball = Model.ball_controller(self.space, balls, ticks_to_next_ball)
            self.draw(line)

            pygame.display.set_caption(f"fps: {clock.get_fps()}")
            # Update physics
            if simulate:
                # for x in range(10 * iterations):  # 10 iterations to get a more stable simulation
                self.space.step(dt)
                damping = 0.99

                limit_velocity(self.model_entity.bodies, self.space.gravity, damping, dt)
                self.model_entity.tick()

                if print_time == 0:
                    # table(self.model_entity)
                    # print(" self.space._get_iterations() = ", self.space._get_iterations(), " dt = ", dt)
                    print_time = print_time + 1
                elif print_time % 10 == 0:
                    # table(self.model_entity)
                    print("floor position x = ", self.model_entity.floor.position.x)
                    print(" self.space._get_iterations() = ", self.space._get_iterations(), " print_time = ",
                          print_time)
                    print(" stiffness 0 = ", self.model_entity.muscles.__getitem__(0).stiffness,
                          " stiffness 1 = ", self.model_entity.muscles.__getitem__(1).stiffness,
                          " damping 0 = ", self.model_entity.muscles.__getitem__(0).damping,
                          " damping 0 = ", self.model_entity.muscles.__getitem__(1).damping)
                    print(" stiffness 2 = ", self.model_entity.muscles.__getitem__(2).stiffness,
                          " stiffness 3 = ", self.model_entity.muscles.__getitem__(3).stiffness,
                          " damping 2 = ", self.model_entity.muscles.__getitem__(2).damping,
                          " damping 3 = ", self.model_entity.muscles.__getitem__(3).damping)
                    print(" stiffness 4 = ", self.model_entity.muscles.__getitem__(4).stiffness,
                          " stiffness 5 = ", self.model_entity.muscles.__getitem__(5).stiffness,
                          " damping 4 = ", self.model_entity.muscles.__getitem__(4).damping,
                          " damping 5 = ", self.model_entity.muscles.__getitem__(5).damping)
                    print_time = print_time + 1
                else:
                    print_time = print_time + 1


if __name__ == "__main__":
    sim = Simulator()
    sim.main()
