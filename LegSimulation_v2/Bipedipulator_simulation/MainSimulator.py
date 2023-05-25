import pygame
import pymunk
import pymunk.matplotlib_util
import pymunk.pygame_util
from pygame.color import THECOLORS

import Model
import constants
from LegSimulation_v2.Bipedipulator_simulation import LegMethodsHelper
from LegSimulation_v2.Bipedipulator_simulation.FillDataAnd import write_data_to_excel
from LegSimulation_v2.Bipedipulator_simulation.LegMotorController import Controller


class Simulator(object):
    model_entity: Model
    controller: Controller
    space: pymunk.Space
    motors: list[pymunk.SimpleMotor]

    def __init__(self):
        self.display_flags = 0  # TODO: move to constants
        self.screen = pygame.display.set_mode((constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT), self.display_flags)
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
            fps = 60
            clock.tick(fps)
            dt = 1.0 / float(fps)
            self.draw()
            pygame.display.set_caption(f"fps: {clock.get_fps()}")
            self.space.step(dt)

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
                    # Start new simulation
                    elif event.key == pygame.K_n:
                        sim1 = Simulator()
                        sim1.main()

            if simulate:
                temp_end = self.controller.movement_scenario_controller(self.model_entity, self.motors,
                                                                        used_scenario)

                # TODO: for validate gravity
                # print(self.ball_body_shape[0].position)
                # print(self.ball_body_shape[0].velocity)
                if temp_end:
                    match used_scenario:
                        case 0:
                            used_scenario += 1
                        # case 1:
                        #     used_scenario += 1
                        case 1:
                            simulate = False
                            running = False

                LegMethodsHelper.limit_velocity(self.model_entity.right_leg.bodies, self.space.gravity, dt)
                LegMethodsHelper.limit_velocity(self.model_entity.left_leg.bodies, self.space.gravity, dt)

        LegMethodsHelper.show_counters(self.model_entity)
        write_data_to_excel(self.model_entity)
        pygame.quit()


if __name__ == "__main__":
    sim = Simulator()
    sim.main()
