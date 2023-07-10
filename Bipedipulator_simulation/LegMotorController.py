from pymunk import SimpleMotor

from Bipedipulator_simulation import constants
from Bipedipulator_simulation.Leg import Leg
from Bipedipulator_simulation.Model import Model
from Bipedipulator_simulation.constants import AMOUNT_PHASES, NUMBER_SIMULATION_STEPS


class Controller:
    loop_counter: int
    current_phase: int

    right_leg_angular_velocities: dict[str, float]
    left_leg_angular_velocities: dict[str, float]

    def __init__(self):
        self.current_phase = 0
        self.loop_counter = 0

        self.right_leg_angular_velocities = dict(thigh_velocity=0.0, calf_velocity=0.0)
        self.left_leg_angular_velocities = dict(thigh_velocity=0.0, calf_velocity=0.0)

    def movement_scenario_controller(self, model_entity: Model, motors: list[SimpleMotor], simulation_step: int):
        calculate_data(model_entity, simulation_step)

        right_leg_angular_velocities = model_entity.right_leg.equations.angular_velocities[simulation_step]
        left_leg_angular_velocities = model_entity.left_leg.equations.angular_velocities[simulation_step]
        right_leg_angular_velocities.update_current_velocity(motors[0].rate, motors[1].rate, self.current_phase)
        left_leg_angular_velocities.update_current_velocity(motors[3].rate, motors[4].rate, self.current_phase)

        self.set_multiplication_of_motor_velocity(model_entity, simulation_step)
        temp_end = self.run_phase_async(model_entity, motors, simulation_step)

        return temp_end

    def set_multiplication_of_motor_velocity(self, model_entity: Model, simulation_step: int):
        right_leg_angular_velocity = model_entity.right_leg.equations.angular_velocities[simulation_step]
        left_leg_angular_velocity = model_entity.left_leg.equations.angular_velocities[simulation_step]

        self.right_leg_angular_velocities['thigh_velocity'] = \
            right_leg_angular_velocity.thigh_angular_velocity_list[self.current_phase]
        self.right_leg_angular_velocities['calf_velocity'] = \
            right_leg_angular_velocity.calf_angular_velocity_list[self.current_phase]
        self.left_leg_angular_velocities['thigh_velocity'] = \
            left_leg_angular_velocity.thigh_angular_velocity_list[self.current_phase]
        self.left_leg_angular_velocities['calf_velocity'] = \
            left_leg_angular_velocity.calf_angular_velocity_list[self.current_phase]

    def run_phase_async(self, model_entity: Model, motors, simulation_step: int):
        temp_end = False
        end_right = self.handle_leg_movement(model_entity.right_leg, motors,
                                             self.right_leg_angular_velocities['thigh_velocity'],
                                             self.right_leg_angular_velocities['calf_velocity'], simulation_step)
        end_left = self.handle_leg_movement(model_entity.left_leg, motors,
                                            self.left_leg_angular_velocities['thigh_velocity'],
                                            self.left_leg_angular_velocities['calf_velocity'], simulation_step)

        if end_right and end_left:
            print("End current phase ", self.current_phase)
            temp_end = self.change_current_phase(simulation_step)

        return temp_end

    def change_current_phase(self, simulation_step: int):
        if self.current_phase == 0 and simulation_step == 0:
            self.current_phase += 1
            return True

        if 0 < self.current_phase < AMOUNT_PHASES:
            self.current_phase += 1
            return False
            # return True  # change this

        if self.current_phase == AMOUNT_PHASES:
            self.loop_counter += 1
            if self.loop_counter == NUMBER_SIMULATION_STEPS:
                self.loop_counter = 0
                self.current_phase = 1
                return True

        return False

    def handle_leg_movement(self, leg: Leg, motors: list[SimpleMotor], thigh_angular_change_rate: float,
                            calf_angular_change_rate: float, simulation_step: int):
        stop_leg_function = choose_leg_functions(leg, False)
        end_phase = move_leg_phase(leg, motors, thigh_angular_change_rate, calf_angular_change_rate, self.current_phase,
                                   simulation_step)
        leg.relative_values[simulation_step].counters.phases_usage_increment(self.current_phase, end_phase)
        if end_phase:
            stop_leg_function(motors, "thigh")
            stop_leg_function(motors, "calf")
        return end_phase


def move_leg_phase(leg: Leg, motors: list[SimpleMotor], thigh_angular_change_rate: float,
                   calf_angular_change_rate: float,
                   phase: int, simulation_step: int):
    if phase == 0:
        end_thigh = set_thigh_start_position(leg, motors, thigh_angular_change_rate, simulation_step)
        end_calf = set_calf_start_position(leg, motors, calf_angular_change_rate, simulation_step)
        if end_thigh and end_calf:
            return True

        return False
    else:
        end_thigh = False
        end_calf = False
        previous_phase = phase - 1
        move_leg_function = choose_leg_functions(leg, True)
        stop_leg_function = choose_leg_functions(leg, False)

        thigh_value = leg.equations.get_angle("thigh", phase)
        calf_value = leg.equations.get_angle("calf", phase)
        previous_thigh_value = leg.equations.get_angle("thigh", previous_phase)
        previous_calf_value = leg.equations.get_angle("calf", previous_phase)

        if previous_thigh_value > thigh_value:
            if leg.relative_values[simulation_step].hip['angle_thigh'] >= thigh_value:
                move_leg_function(motors, "thigh", "backward", thigh_angular_change_rate)
            else:
                stop_leg_function(motors, "thigh")
                end_thigh = True
        elif previous_thigh_value < thigh_value:
            if leg.relative_values[simulation_step].hip['angle_thigh'] <= thigh_value:
                move_leg_function(motors, "thigh", "forward", thigh_angular_change_rate)
            else:
                stop_leg_function(motors, "thigh")
                end_thigh = True
        else:
            stop_leg_function(motors, "thigh")
            end_thigh = True

        if calf_value < previous_calf_value:
            if leg.relative_values[simulation_step].knee['angle_calf'] >= calf_value:
                move_leg_function(motors, "calf", "backward", calf_angular_change_rate)
            else:
                stop_leg_function(motors, "calf")
                end_calf = True
        elif calf_value > previous_calf_value:
            if leg.relative_values[simulation_step].knee['angle_calf'] <= calf_value:
                move_leg_function(motors, "calf", "forward", calf_angular_change_rate)
            else:
                stop_leg_function(motors, "calf")
                end_calf = True
        else:
            stop_leg_function(motors, "calf")
            end_calf = True

        if end_thigh and end_calf:
            return True

        return False


def choose_leg_functions(leg: Leg, move: bool):
    functions = {
        "right": (move_right_leg, stop_moving_right_leg),
        "left": (move_left_leg, stop_moving_left_leg),
    }

    move_func, stop_func = functions.get(leg.leg_name, (None, None))

    return move_func if move else stop_func


def move_right_leg(motors: list[SimpleMotor], leg_part: str, direction: str, angular_change_rate: float):
    part_dict = {"thigh": 0, "calf": 1, "foot": 2}
    velocity = constants.ROTATION_RATE * angular_change_rate
    velocity = velocity if direction == "forward" else -velocity

    if leg_part in part_dict and motors[part_dict[leg_part]].rate != velocity:
        motors[part_dict[leg_part]].rate = velocity


def move_left_leg(motors: list[SimpleMotor], leg_part: str, direction: str, angular_change_rate: float):
    part_dict = {"thigh": 3, "calf": 4, "foot": 5}
    velocity = constants.ROTATION_RATE * angular_change_rate
    velocity = velocity if direction == "forward" else -velocity

    if leg_part in part_dict and motors[part_dict[leg_part]].rate != velocity:
        motors[part_dict[leg_part]].rate = velocity


def stop_moving_right_leg(motors: list[SimpleMotor], leg_part: str):
    part_dict = {"thigh": 0, "calf": 1, "foot": 2}
    if leg_part in part_dict:
        motors[part_dict[leg_part]].rate = 0


def stop_moving_left_leg(motors: list[SimpleMotor], leg_part: str):
    part_dict = {"thigh": 3, "calf": 4, "foot": 5}
    if leg_part in part_dict:
        motors[part_dict[leg_part]].rate = 0


def calculate_data(model_entity: Model, simulation_step: int):
    save_bodies_velocities(model_entity, simulation_step)

    for leg in (model_entity.right_leg, model_entity.left_leg):
        relative_values = leg.relative_values[simulation_step]
        relative_values.calculate_angles(
            model_entity.hip_body.position,
            leg.knee_body.position,
            leg.ankle_body.position
        )


def save_bodies_velocities(model_entity: Model, simulation_step: int):
    for leg in (model_entity.right_leg, model_entity.left_leg):
        relative_values = leg.relative_values[simulation_step]
        for joint_name, joint_body in zip(('hip', 'knee', 'ankle'),
                                          (model_entity.hip_body, leg.knee_body, leg.ankle_body)):
            relative_values.body_velocity(joint_body, joint_name)


def set_thigh_start_position(leg: Leg, motors: list[SimpleMotor], thigh_angular_change_rate: float,
                             simulation_step: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = leg.equations.get_angle("thigh", 0)
    if leg.relative_values[simulation_step].hip['angle_thigh'] <= thigh_value:
        move_leg_function(motors, "thigh", "forward", thigh_angular_change_rate)
    else:
        stop_leg_function(motors, "thigh")
        return True

    return False


def set_calf_start_position(leg: Leg, motors: list[SimpleMotor], calf_angular_change_rate: float, simulation_step: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    calf_value = leg.equations.get_angle("calf", 0)
    if leg.relative_values[simulation_step].knee['angle_calf'] >= calf_value:
        move_leg_function(motors, "calf", "backward", calf_angular_change_rate)
    else:
        stop_leg_function(motors, "calf")
        return True

    return False
