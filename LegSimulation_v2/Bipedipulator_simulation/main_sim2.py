import sys

import pygame
import pymunk
import pymunk.matplotlib_util
import pymunk.pygame_util
from pygame.color import THECOLORS

import Model
import constants
from LegSimulation_v2.Bipedipulator_simulation.FillDataAnd import VisualizeDataMatplotlib, write_data_to_excel
from LegSimulation_v2.Bipedipulator_simulation.LegMotorController import Controller


def limit_velocity(bodies: list[pymunk.Body], gravity, damping, dt):
    for x in range(len(bodies)):
        max_velocity = 100
        pymunk.Body.update_velocity(bodies[x], gravity, damping, dt)
        if bodies[x].velocity.length > max_velocity:
            bodies[x].velocity = bodies[x].velocity * 0.99


class Simulator(object):
    mode: str

    model_entity: Model
    controller: Controller
    space: pymunk.Space
    motors: list[pymunk.SimpleMotor]

    def __init__(self):
        self.mode = "Non-AI mode"
        # self.mode = "AI mode"
        self.display_flags = 0
        self.display_size = (constants.BOUNDS_WIDTH, constants.BOUNDS_HEIGHT)
        self.screen = None
        self.draw_options = None
        self.space = pymunk.Space()
        self.space.gravity = (0, constants.GRAVITY)
        pymunk.pygame_util.positive_y_is_up = True
        self.model_entity = Model.Model(self.space, self.mode)
        self.motors = self.motor_leg(0, 0)
        self.controller = Controller(self.model_entity, self.mode)
        self.matplotlib = VisualizeDataMatplotlib()
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
        self.model_entity.right_leg.thigh.shape.filter = shape_filter
        self.model_entity.right_leg.cale.shape.filter = shape_filter
        self.model_entity.right_leg.foot.shape.filter = shape_filter
        self.model_entity.right_leg.foot.shape.collision_type = 1

        self.model_entity.corps.shape.filter = shape_filter
        self.model_entity.left_leg.thigh.shape.filter = shape_filter
        self.model_entity.left_leg.cale.shape.filter = shape_filter
        self.model_entity.left_leg.foot.shape.filter = shape_filter
        self.model_entity.left_leg.foot.shape.collision_type = 1

        if self.mode == "AI mode":
            self.model_entity.right_leg.patella_thigh_part.shape.filter = shape_filter
            self.model_entity.right_leg.patella_cale_part.shape.filter = shape_filter

    def motor_leg(self, relative_angu_vel_right_leg, relative_angu_vel_left_leg):
        corps_motor = pymunk.SimpleMotor(self.model_entity.corps.body, self.model_entity.floor, 0)
        left_thigh_motor = pymunk.SimpleMotor(self.model_entity.left_leg.thigh.body, self.model_entity.corps.body,
                                              relative_angu_vel_left_leg)
        left_cale_motor = pymunk.SimpleMotor(self.model_entity.left_leg.cale.body,
                                             self.model_entity.left_leg.thigh.body, relative_angu_vel_left_leg)

        left_foot_motor = pymunk.SimpleMotor(self.model_entity.left_leg.foot.body, self.model_entity.floor, 0)

        right_thigh_motor = pymunk.SimpleMotor(self.model_entity.right_leg.thigh.body, self.model_entity.corps.body,
                                               relative_angu_vel_right_leg)
        right_cale_motor = pymunk.SimpleMotor(self.model_entity.right_leg.cale.body,
                                              self.model_entity.right_leg.thigh.body, relative_angu_vel_right_leg)
        right_foot_motor = pymunk.SimpleMotor(self.model_entity.right_leg.foot.body, self.model_entity.floor, 0)

        self.space.add(right_thigh_motor, right_cale_motor,
                       right_foot_motor, left_thigh_motor, left_cale_motor, left_foot_motor, corps_motor)

        # self.space.add(right_thigh_motor, right_cale_motor, right_foot_motor)

        self.filter()
        # motors = [left_thigh_motor, left_cale_motor, left_foot_motor]
        motors = [right_thigh_motor, right_cale_motor,
                  right_foot_motor, left_thigh_motor, left_cale_motor, left_foot_motor, corps_motor]

        return motors

    def main(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.display_size, self.display_flags)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        # ax = plt.axes(xlim=(0, 700), ylim=(0, 1000))
        # self.draw_options = pymunk.matplotlib_util.DrawOptions(ax)
        self.space._set_iterations(20)  ### Try another value to better experience

        clock = pygame.time.Clock()
        running = True

        simulate = False
        print_time = 0
        pressed_k_left = False
        pressed_k_right = False
        pressed_k_a = False
        force = 0.0
        collision_handler = False
        stop = False
        up = False

        relative_angu_vel_right_leg = 0
        relative_angu_vel_left_leg = 0
        counter = 0

        while running:

            line = None
            fps = 60
            clock.tick(fps)
            dt = 1.0 / float(fps)
            counter += 1

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.QUIT or (
                            event.key in (pygame.K_q, pygame.K_ESCAPE)):

                        self.model_entity.right_leg.relative_values.counters[0].show_counters()
                        self.model_entity.left_leg.relative_values.counters[0].show_counters()
                        if self.controller.loop_counter > 0:
                            self.model_entity.right_leg.relative_values.counters[1].show_counters()
                            self.model_entity.left_leg.relative_values.counters[1].show_counters()
                        self.model_entity.right_leg.relative_values.velocities.show_velocity_lists()
                        self.model_entity.left_leg.relative_values.velocities.show_velocity_lists()
                        # running = False
                        # print("initial_array : ", str(self.model_entity.left_leg.relative_values.data))

                        write_data_to_excel(self.model_entity)
                        # self.matplotlib.run("right_leg_data.xlsx")

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
                        self.model_entity.right_leg.relative_values.velocities.show_velocity_lists()
                        self.model_entity.left_leg.relative_values.velocities.show_velocity_lists()

                    elif event.key == pygame.K_a:
                        pressed_k_a = not pressed_k_a

                    # hold the simulation
                    elif event.key == pygame.K_r:
                        # Reset.
                        simulate = False
                    # Start new simulation
                    elif event.key == pygame.K_n:
                        sim1 = Simulator()
                        sim1.main()

            if pressed_k_left:
                x = self.model_entity.corps.body.position.x + (0.5 * constants.CORPS_WIDTH)
                y = self.model_entity.corps.body.position.y
                self.model_entity.corps.body.apply_force_at_local_point((force, 0), (x, y))
                force = force - 5

            temp_up = False

            up = temp_up

            if pressed_k_a:
                self.model_entity.move_running_gear()

            self.draw(line)
            pygame.display.set_caption(f"fps: {clock.get_fps()}")
            if simulate:
                self.space.step(dt)
                damping = 0.99
                temp_end = self.controller.movement_scenario_controller(self.model_entity, self.motors, simulate, counter)
                if temp_end:
                    simulate = False
                limit_velocity(self.model_entity.right_leg.bodies, self.space.gravity, damping, dt)
                limit_velocity(self.model_entity.left_leg.bodies, self.space.gravity, damping, dt)


if __name__ == "__main__":
    sim = Simulator()
    sim.main()
