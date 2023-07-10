import time
import pygame
import pymunk.matplotlib_util
import pymunk.pygame_util

import Model
import constants
from Bipedipulator_simulation import ModelHelper
from Bipedipulator_simulation.ExportDataToFiles import export_data_to_files, save_gravity_results_to_excel
from Bipedipulator_simulation.LegMotorController import Controller, stop_moving_right_leg, stop_moving_left_leg


def event_method(model_entity: Model, simulate: bool):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.type == pygame.QUIT or (
                    event.key in (pygame.K_q, pygame.K_ESCAPE)):
                running = False
                # save_gravity_results_to_excel(data)
            # Start/stop simulation
            elif event.key == pygame.K_s:
                return [running, not simulate]
            elif event.key == pygame.K_a:
                model_entity.move_running_gear()
            elif event.key == pygame.K_z:
                model_entity.stop_running_gear()
            # Start new simulation
            elif event.key == pygame.K_n:
                sim1 = Simulator()
                sim1.main()

    return [running, simulate]


def validate_gravity(initial_position, real_values: pymunk.Body, current_time):
    real_position = real_values.position.y
    real_ball_velocity = -real_values.velocity.y
    initial_velocity = 0.0

    expected_position = initial_position - 0.5 * (-constants.GRAVITY) * current_time ** 2
    expected_velocity = initial_velocity + (-constants.GRAVITY) * current_time

    return {
        "current_time": current_time,
        "real_position": round(real_position, 1),
        "expected_position": round(expected_position, 1),
        "real_velocity": round(real_ball_velocity, 1),
        "expected_velocity": round(expected_velocity, 1)
    }


class Simulator:
    model_entity: Model
    controller: Controller
    space: pymunk.Space
    motors: list[pymunk.SimpleMotor]
    screen: pygame.Surface

    def __init__(self):
        self.add_space_with_gravity()

        self.model_entity = Model.Model(self.space)
        self.motors = ModelHelper.motor_leg(self.model_entity, self.space)
        self.controller = Controller()

    def add_space_with_gravity(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, constants.GRAVITY)
        pymunk.pygame_util.positive_y_is_up = True

    def main(self):
        pygame.init()
        clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            (constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT), constants.DISPLAY_FLAGS)

        simulate = False
        running = True
        simulation_step = 0

        # test_ball_body = ModelHelper.add_test_ball(self.space)
        # validate_gravity_flag = True
        # start_time = time.time()
        # initial_position = test_ball_body[0].position.y
        # data = []
        # counter = 0

        self.space.iterations = 300
        while running:
            clock.tick(constants.FPS)
            dt = 1.0 / float(constants.FPS)
            self.draw(clock)
            self.space.step(dt)

            # running, simulate = event_method(self.model_entity, simulate, data)
            running, simulate = event_method(self.model_entity, simulate)

            # if validate_gravity_flag:
            #     current_time = time.time()
            #     elapsed_time = current_time - start_time
            #     if test_ball_body[0].position.y > 100:
            #         result = validate_gravity(initial_position, test_ball_body[0], elapsed_time)
            # data.append(result)
            # else:
            #     validate_gravity_flag = False

            if simulate:
                temp_end = self.controller.movement_scenario_controller(self.model_entity, self.motors, simulation_step)
                if temp_end:
                    # simulate = False  # remove
                    # counter += 1
                    # if counter == 1:
                    #     simulation_step += 1
                    # elif counter == constants.AMOUNT_PHASES:
                    #     # running = False
                    simulation_step += 1
                    if simulation_step == constants.NUMBER_SIMULATION_STEPS:
                        simulate = False
                        running = False

                # self.limit_bodies_velocity(test_ball_body, dt)
                self.limit_bodies_velocity(dt)
            else:
                self.stop_moving()

        ModelHelper.show_counters(self.model_entity)
        export_data_to_files(self.model_entity)
        pygame.quit()

    def draw(self, clock: pygame.time.Clock()):
        self.screen.fill(pygame.color.THECOLORS['white'])  # Clear the screen
        draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.debug_draw(draw_options)  # Draw space
        pygame.display.flip()  # All done, lets flip the display
        pygame.display.set_caption(f"fps: {clock.get_fps()}")

    def limit_bodies_velocity(self, dt):
        # ModelHelper.limit_velocity(test_ball_body, self.space.gravity, dt)
        ModelHelper.limit_velocity(self.model_entity.right_leg.bodies, self.space.gravity, dt)
        ModelHelper.limit_velocity(self.model_entity.left_leg.bodies, self.space.gravity, dt)

    def stop_moving(self):
        stop_moving_right_leg(self.motors, "thigh")
        stop_moving_right_leg(self.motors, "calf")
        stop_moving_left_leg(self.motors, "thigh")
        stop_moving_left_leg(self.motors, "calf")


if __name__ == "__main__":
    sim = Simulator()
    sim.main()
