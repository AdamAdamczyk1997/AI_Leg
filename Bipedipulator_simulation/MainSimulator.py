import pygame
import pymunk
import pymunk.matplotlib_util
import pymunk.pygame_util
from pygame.color import THECOLORS

import Model
import constants
from Bipedipulator_simulation import LegMethodsHelper
from Bipedipulator_simulation.FillDataAnd import write_data_to_excel
from Bipedipulator_simulation.LegMotorController import Controller, stop_moving_right_leg, stop_moving_left_leg


def event_method(model_entity: Model, simulate: bool):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.type == pygame.QUIT or (
                    event.key in (pygame.K_q, pygame.K_ESCAPE)):
                running = False
            # Start/stop simulation
            elif event.key == pygame.K_s:
                return [running, not simulate]
            elif event.key == pygame.K_a:
                model_entity.move_running_gear()
            # Start new simulation
            elif event.key == pygame.K_n:
                sim1 = Simulator()
                sim1.main()

    return [running, simulate]


class Simulator(object):
    model_entity: Model
    controller: Controller
    space: pymunk.Space
    motors: list[pymunk.SimpleMotor]

    def __init__(self):
        self.screen = pygame.display.set_mode((constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT),
                                              constants.DISPLAY_FLAGS)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space = pymunk.Space()
        self.space.gravity = (0, constants.GRAVITY)
        pymunk.pygame_util.positive_y_is_up = True

        self.model_entity = Model.Model(self.space)
        self.motors = LegMethodsHelper.motor_leg(self.model_entity, self.space)
        self.controller = Controller()

        # for validate gravity
        self.ball_body_shape = LegMethodsHelper.add_test_ball()
        self.space.add(self.ball_body_shape[0], self.ball_body_shape[1])

    def draw(self):
        self.screen.fill(THECOLORS["white"])  # Clear the screen
        self.space.debug_draw(self.draw_options)  # Draw space
        pygame.display.flip()  # All done, lets flip the display

    def main(self):
        pygame.init()
        self.space.iterations = 100  # Try another value to better experience
        clock = pygame.time.Clock()

        simulate = False
        running = True
        used_scenario = 0

        while running:
            clock.tick(constants.FPS)
            dt = 1.0 / float(constants.FPS)
            self.draw()
            pygame.display.set_caption(f"fps: {clock.get_fps()}")
            self.space.step(dt)

            event_return = event_method(self.model_entity, simulate)
            running = event_return[0]
            simulate = event_return[1]

            if simulate:
                temp_end = self.controller.movement_scenario_controller(self.model_entity, self.motors,
                                                                        used_scenario)

                # TODO: for validate gravity
                # print(self.ball_body_shape[0].position)
                # print(self.ball_body_shape[0].velocity)
                if temp_end:
                    used_scenario += 1
                    if used_scenario > constants.AMOUNT_SCENARIOS:
                        simulate = False
                        running = False

                LegMethodsHelper.limit_velocity(self.model_entity.right_leg.bodies, self.space.gravity, dt)
                LegMethodsHelper.limit_velocity(self.model_entity.left_leg.bodies, self.space.gravity, dt)
            else:
                stop_moving_right_leg(self.motors, "thigh")
                stop_moving_right_leg(self.motors, "calf")
                stop_moving_left_leg(self.motors, "thigh")
                stop_moving_left_leg(self.motors, "calf")

        LegMethodsHelper.show_counters(self.model_entity)
        write_data_to_excel(self.model_entity)
        pygame.quit()


if __name__ == "__main__":
    sim = Simulator()
    sim.main()
