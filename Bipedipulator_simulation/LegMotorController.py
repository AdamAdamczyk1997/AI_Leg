import operator

from pymunk import SimpleMotor

from Bipedipulator_simulation import constants
from Bipedipulator_simulation.Leg import Leg
from Bipedipulator_simulation.Model import Model
from Bipedipulator_simulation.constants import AMOUNT_PHASES, AMOUNT_SCENARIOS


class Controller:
    loop_counter: int
    current_phase: int

    right_thigh_speed: float
    right_calf_speed: float
    left_thigh_speed: float
    left_calf_speed: float

    def __init__(self):
        self.current_phase = 0
        self.loop_counter = 0
        self.right_thigh_speed = 0
        self.right_calf_speed = 0
        self.left_thigh_speed = 0
        self.left_calf_speed = 0

    def set_multiplication_of_motor_velocity(self, model_entity: Model, used_scenario: int):
        right_leg_velocities = model_entity.right_leg.equations.velocities[used_scenario]
        left_leg_velocities = model_entity.left_leg.equations.velocities[used_scenario]

        self.right_thigh_speed = right_leg_velocities.thigh_velocity[self.current_phase]
        self.right_calf_speed = right_leg_velocities.calf_velocity[self.current_phase]
        self.left_thigh_speed = left_leg_velocities.thigh_velocity[self.current_phase]
        self.left_calf_speed = left_leg_velocities.calf_velocity[self.current_phase]

    def movement_scenario_controller(self, model_entity: Model, motors: list[SimpleMotor], used_scenario: int):
        calculate_data(model_entity, used_scenario)

        right_leg_velocities = model_entity.right_leg.equations.velocities[used_scenario]
        left_leg_velocities = model_entity.left_leg.equations.velocities[used_scenario]
        right_leg_velocities.update_current_velocity(motors[0].rate, motors[1].rate, self.current_phase)
        left_leg_velocities.update_current_velocity(motors[3].rate, motors[4].rate, self.current_phase)

        self.set_multiplication_of_motor_velocity(model_entity, used_scenario)
        temp_end = self.run_phase_async(model_entity, motors, used_scenario)

        return temp_end

    def change_current_phase(self, used_scenario: int):
        if self.current_phase == 0 and used_scenario == 0:
            self.current_phase += 1
            return True

        if 0 < self.current_phase < AMOUNT_PHASES:
            self.current_phase += 1
            return False

        if self.current_phase == AMOUNT_PHASES:
            self.loop_counter += 1
            if self.loop_counter == AMOUNT_SCENARIOS:
                self.loop_counter = 0
                self.current_phase = 1
                return True

        return False

    def handle_leg_movement(self, leg, motors, thigh_speed, calf_speed, used_scenario):
        stop_leg_function = choose_leg_functions(leg, False)
        end_phase = move_leg_phase(leg, motors, thigh_speed, calf_speed, self.current_phase, used_scenario)
        leg.relative_values[used_scenario].counters.phases_usage_increment(self.current_phase, end_phase)
        if end_phase:
            stop_leg_function(motors, "thigh")
            stop_leg_function(motors, "calf")
            print("End Phase: ", self.current_phase, " for Leg: ", leg.name)
        return end_phase

    def run_phase_async(self, model_entity: Model, motors, used_scenario: int):
        temp_end = False
        end_right = self.handle_leg_movement(model_entity.right_leg, motors, self.right_thigh_speed,
                                             self.right_calf_speed, used_scenario)
        end_left = self.handle_leg_movement(model_entity.left_leg, motors, self.left_thigh_speed,
                                            self.left_calf_speed, used_scenario)

        if end_right and end_left:
            print("End current phase ", self.current_phase)
            model_entity.right_leg.relative_values[used_scenario].change_oscillation(self.current_phase)
            model_entity.left_leg.relative_values[used_scenario].change_oscillation(self.current_phase)
            temp_end = self.change_current_phase(used_scenario)

        return temp_end


def set_thigh_start_position(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, used_scenario: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = leg.equations.get_angle("thigh", 0)
    if leg.relative_values[used_scenario].hip['angle_thigh'] <= thigh_value:
        move_leg_function(motors, "thigh", "forward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        return True

    return False


def set_calf_start_position(leg: Leg, motors: list[SimpleMotor], calf_speed: float, used_scenario: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    calf_value = leg.equations.get_angle("calf", 0)
    if leg.relative_values[used_scenario].knee['angle_calf'] >= calf_value:
        move_leg_function(motors, "calf", "backward", calf_speed)
    else:
        stop_leg_function(motors, "calf")
        return True

    return False


def move_leg_phase(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, calf_speed: float,
                   phase: int, used_scenario: int):
    if phase == 0:
        end_thigh = set_thigh_start_position(leg, motors, thigh_speed, used_scenario)
        end_calf = set_calf_start_position(leg, motors, calf_speed, used_scenario)
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
            if leg.relative_values[used_scenario].hip['angle_thigh'] >= thigh_value:
                move_leg_function(motors, "thigh", "backward", thigh_speed)
            else:
                stop_leg_function(motors, "thigh")
                end_thigh = True
        elif previous_thigh_value < thigh_value:
            if leg.relative_values[used_scenario].hip['angle_thigh'] <= thigh_value:
                move_leg_function(motors, "thigh", "forward", thigh_speed)
            else:
                stop_leg_function(motors, "thigh")
                end_thigh = True
        else:
            stop_leg_function(motors, "thigh")
            end_thigh = True

        if calf_value < previous_calf_value:
            if leg.relative_values[used_scenario].knee['angle_calf'] >= calf_value:
                move_leg_function(motors, "calf", "backward", calf_speed)
            else:
                stop_leg_function(motors, "calf")
                end_calf = True
        elif calf_value > previous_calf_value:
            if leg.relative_values[used_scenario].knee['angle_calf'] <= calf_value:
                move_leg_function(motors, "calf", "forward", calf_speed)
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

    move_func, stop_func = functions.get(leg.name, (None, None))

    return move_func if move else stop_func


def move_right_leg(motors: list[SimpleMotor], leg_part: str, direction: str, multiplication: float):
    part_dict = {"thigh": 0, "calf": 1, "foot": 2}
    velocity = constants.ROTATION_RATE * multiplication
    velocity = velocity if direction == "forward" else -velocity

    if leg_part in part_dict and motors[part_dict[leg_part]].rate != velocity:
        motors[part_dict[leg_part]].rate = velocity


def move_left_leg(motors: list[SimpleMotor], leg_part: str, direction: str, multiplication: float):
    part_dict = {"thigh": 3, "calf": 4, "foot": 5}
    velocity = constants.ROTATION_RATE * multiplication
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


def calculate_data(model_entity: Model, used_scenario: int):
    save_body_velocities(model_entity, used_scenario)

    for leg in (model_entity.right_leg, model_entity.left_leg):
        relative_values = leg.relative_values[used_scenario]
        relative_values.calculate_angles(
            model_entity.hip_body.position,
            leg.knee_body.position,
            leg.ankle_body.position
        )


def save_body_velocities(model_entity: Model, used_scenario: int):
    for leg in (model_entity.right_leg, model_entity.left_leg):
        relative_values = leg.relative_values[used_scenario]
        for joint_name, joint_body in zip(('hip', 'knee', 'ankle'),
                                          (model_entity.hip_body, leg.knee_body, leg.ankle_body)):
            relative_values.body_velocity(joint_body, joint_name)
