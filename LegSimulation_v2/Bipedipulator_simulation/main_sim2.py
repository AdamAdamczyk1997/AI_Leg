import sys

import pygame
import pymunk
import pymunk.matplotlib_util
import pymunk.pygame_util
from pygame.color import THECOLORS

import Model
import constants
from LegSimulation_v2.Bipedipulator_simulation.FillDataAnd import write_data_to_excel
from LegSimulation_v2.Bipedipulator_simulation.LegMotorController import Controller


def add_test_ball():
    """Add a ball to the given space at a random position"""
    mass = 1
    radius = 20
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
    body = pymunk.Body(mass, inertia)
    body.position = 200, 1000
    shape = pymunk.Circle(body, radius, (0, 0))
    shape.friction = 1
    return [body, shape]


def limit_velocity(bodies: list[pymunk.Body], gravity, damping, dt):
    for x in range(len(bodies)):
        max_velocity = 100
        pymunk.Body.update_velocity(bodies[x], gravity, damping, dt)
        if bodies[x].velocity.length > max_velocity:
            bodies[x].velocity = bodies[x].velocity * 0.99


class Simulator(object):
    used_scenario: int

    model_entity: Model
    controller: Controller
    space: pymunk.Space
    motors: list[pymunk.SimpleMotor]

    def __init__(self):
        self.display_flags = 0
        self.screen = pygame.display.set_mode((constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT), self.display_flags)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space = pymunk.Space()
        self.space.gravity = (0, constants.GRAVITY)
        pymunk.pygame_util.positive_y_is_up = True

        self.model_entity = Model.Model(self.space)
        self.motors = self.motor_leg()
        self.controller = Controller(self.model_entity)
        self.used_scenario = 0

        # for validate gravity
        self.ball_body_shape = add_test_ball()
        self.space.add(self.ball_body_shape[0], self.ball_body_shape[1])

    def draw(self):
        self.screen.fill(THECOLORS["white"])  ### Clear the screen
        self.space.debug_draw(self.draw_options)  ### Draw space
        pygame.display.flip()  ### All done, lets flip the display

    def motor_leg(self):
        corps_motor = pymunk.SimpleMotor(self.model_entity.corps.body, self.model_entity.floor, 0)

        left_thigh_motor = pymunk.SimpleMotor(self.model_entity.left_leg.thigh.body, self.model_entity.corps.body, 0)
        left_calf_motor = pymunk.SimpleMotor(self.model_entity.left_leg.calf.body,
                                             self.model_entity.left_leg.thigh.body, 0)
        left_foot_motor = pymunk.SimpleMotor(self.model_entity.left_leg.foot.body, self.model_entity.floor, 0)

        right_thigh_motor = pymunk.SimpleMotor(self.model_entity.right_leg.thigh.body, self.model_entity.corps.body, 0)
        right_calf_motor = pymunk.SimpleMotor(self.model_entity.right_leg.calf.body,
                                              self.model_entity.right_leg.thigh.body, 0)
        right_foot_motor = pymunk.SimpleMotor(self.model_entity.right_leg.foot.body, self.model_entity.floor, 0)

        self.space.add(right_thigh_motor, right_calf_motor,
                       right_foot_motor, left_thigh_motor, left_calf_motor, left_foot_motor, corps_motor)

        motors = [right_thigh_motor, right_calf_motor, right_foot_motor,
                  left_thigh_motor, left_calf_motor, left_foot_motor, corps_motor]

        return motors

    def main(self):
        pygame.init()
        self.space.iterations = 100  ### Try another value to better experience

        clock = pygame.time.Clock()
        counter = 0

        simulate = False
        running = True

        while running:
            fps = 60
            clock.tick(fps)
            dt = 1.0 / float(fps)
            counter += 1
            self.draw()
            pygame.display.set_caption(f"fps: {clock.get_fps()}")

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.QUIT or (
                            event.key in (pygame.K_q, pygame.K_ESCAPE)):
                        running = False
                    # Start/stop simulation
                    elif event.key == pygame.K_s:
                        simulate = not simulate
                    elif event.key == pygame.K_a:
                        self.model_entity.move_running_gear()
                    # hold the simulation
                    elif event.key == pygame.K_r:
                        # Reset.
                        simulate = False
                    # Start new simulation
                    elif event.key == pygame.K_n:
                        sim1 = Simulator()
                        sim1.main()

            if simulate:
                self.space.step(dt)
                damping = 0.99
                temp_end = self.controller.movement_scenario_controller(self.model_entity, self.motors, simulate,
                                                                        self.used_scenario)

                # TODO: for validate gravity
                # print(self.ball_body_shape[0].position)
                # print(self.ball_body_shape[0].velocity)

                if temp_end:
                    match self.used_scenario:
                        case 0:
                            self.model_entity.right_leg.relative_values[self.used_scenario].counters.show_counters()
                            self.model_entity.left_leg.relative_values[self.used_scenario].counters.show_counters()
                            self.used_scenario += 1
                            temp_end = False
                        case 1:
                            simulate = False
                            running = False

                limit_velocity(self.model_entity.right_leg.bodies, self.space.gravity, damping, dt)
                limit_velocity(self.model_entity.left_leg.bodies, self.space.gravity, damping, dt)

        self.model_entity.right_leg.relative_values[self.used_scenario].counters.show_counters()
        self.model_entity.left_leg.relative_values[self.used_scenario].counters.show_counters()
        self.model_entity.right_leg.equations.velocities[self.used_scenario].show_velocity_lists()
        self.model_entity.left_leg.equations.velocities[self.used_scenario].show_velocity_lists()

        write_data_to_excel(self.model_entity)
        pygame.quit()


if __name__ == "__main__":
    sim = Simulator()
    sim.main()
