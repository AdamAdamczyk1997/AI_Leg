from pymunk import SimpleMotor, Vec2d

from LegSimulation_v2.Bipedipulator_simulation import constants
from LegSimulation_v2.Bipedipulator_simulation.Leg import Leg
from LegSimulation_v2.Bipedipulator_simulation.Model import Model
from LegSimulation_v2.Bipedipulator_simulation.RelativeValues import Counters


class Controller:
    loop_counter: int
    current_phase: int
    before_start: bool
    mode: str

    right_thigh_speed: float
    right_calf_speed: float
    left_thigh_speed: float
    left_calf_speed: float

    used_scenario: int

    def __init__(self, model_entity: Model):
        self.current_phase = 0
        self.loop_counter = 0
        self.right_thigh_speed = 0
        self.right_calf_speed = 0
        self.left_thigh_speed = 0
        self.left_calf_speed = 0
        self.used_scenario = 0

    def set_multiplication_of_motor_velocity(self, right_thigh_speed: float, right_calf_speed: float,
                                             left_thigh_speed: float, left_calf_speed: float):
        self.right_thigh_speed = right_thigh_speed
        self.right_calf_speed = right_calf_speed
        self.left_thigh_speed = left_thigh_speed
        self.left_calf_speed = left_calf_speed
        pass

    def movement_scenario_controller(self, model_entity: Model, motors: list[SimpleMotor], simulate,
                                     used_scenario: int):
        if simulate:
            self.used_scenario = used_scenario
            calculate_data(model_entity, used_scenario)

            right_thigh_speed = model_entity.right_leg.equations.velocities[used_scenario].thigh_velocity. \
                __getitem__(self.current_phase)
            right_calf_speed = model_entity.right_leg.equations.velocities[used_scenario].calf_velocity. \
                __getitem__(self.current_phase)
            left_thigh_speed = model_entity.left_leg.equations.velocities[used_scenario].thigh_velocity. \
                __getitem__(self.current_phase)
            left_calf_speed = model_entity.left_leg.equations.velocities[used_scenario].calf_velocity. \
                __getitem__(self.current_phase)

            model_entity.right_leg.equations.velocities[used_scenario].update_current_velocity(
                motors.__getitem__(0).rate,
                motors.__getitem__(1).rate,
                self.current_phase)
            model_entity.left_leg.equations.velocities[used_scenario].update_current_velocity(
                motors.__getitem__(3).rate,
                motors.__getitem__(4).rate,
                self.current_phase)

            self.set_multiplication_of_motor_velocity(right_thigh_speed, right_calf_speed, left_thigh_speed,
                                                      left_calf_speed)
            temp_end = self.run_phase_async(model_entity, motors, self.current_phase)

            return temp_end

    def change_current_phase(self, model_entity: Model):
        if self.current_phase == 0 and self.used_scenario == 0:
            self.current_phase += 1
            return True
        elif 0 < self.current_phase < 12:
            self.current_phase += 1
        elif self.current_phase == 12:
            self.loop_counter += 1
            if self.loop_counter == 2:
                self.loop_counter = 0
                return True
            self.current_phase = 1

        return False

    def run_phase_async(self, model_entity: Model, motors, phase_nr: int):
        temp_end = False
        end_right = move_leg_phase(model_entity.right_leg, motors, self.right_thigh_speed,
                                   self.right_calf_speed, self.current_phase, self.used_scenario)
        model_entity.right_leg.relative_values[self.used_scenario].counters. \
            phase_part_usage_increment(self.current_phase, end_right)
        if end_right:
            stop_moving_right_leg(motors, "thigh")
            stop_moving_right_leg(motors, "calf")
            print("End Right:", self.current_phase)

        end_left = move_leg_phase(model_entity.left_leg, motors, self.left_thigh_speed,
                                  self.left_calf_speed, self.current_phase, self.used_scenario)
        model_entity.left_leg.relative_values[self.used_scenario].counters. \
            phase_part_usage_increment(self.current_phase, end_left)
        if end_left:
            stop_moving_left_leg(motors, "thigh")
            stop_moving_left_leg(motors, "calf")
            print("End Left:", self.current_phase)

        if end_right and end_left:
            print("End current phase ", self.current_phase)

            model_entity.right_leg.relative_values[self.used_scenario].change_oscillation(self.current_phase)
            model_entity.left_leg.relative_values[self.used_scenario].change_oscillation(self.current_phase)
            temp_end = self.change_current_phase(model_entity)

        return temp_end


def choose_leg_functions(leg: Leg, move: bool):
    match leg.name:
        case "right":
            if move:
                return move_right_leg
            else:
                return stop_moving_right_leg
        case "left":
            if move:
                return move_left_leg
            else:
                return stop_moving_left_leg


def calculate_data(model_entity: Model, used_scenario: int):
    model_entity.right_leg.relative_values[used_scenario].body_velocity(model_entity.hip_body, "hip")
    model_entity.right_leg.relative_values[used_scenario].body_velocity(model_entity.right_leg.knee_body, "knee")
    model_entity.right_leg.relative_values[used_scenario].body_velocity(model_entity.right_leg.ankle_body, "ankle")
    model_entity.left_leg.relative_values[used_scenario].body_velocity(model_entity.hip_body, "hip")
    model_entity.left_leg.relative_values[used_scenario].body_velocity(model_entity.left_leg.knee_body, "knee")
    model_entity.left_leg.relative_values[used_scenario].body_velocity(model_entity.left_leg.ankle_body, "ankle")

    model_entity.right_leg.relative_values[used_scenario].calculate_angles(
        model_entity.hip_body.position,
        model_entity.right_leg.knee_body.position,
        model_entity.right_leg.ankle_body.position)
    model_entity.left_leg.relative_values[used_scenario].calculate_angles(
        model_entity.hip_body.position,
        model_entity.left_leg.knee_body.position,
        model_entity.left_leg.ankle_body.position)
    pass


def move_right_leg(motors: list[SimpleMotor], leg_part: str, direction: str, multiplication: float):
    velocity = constants.ROTATION_RATE * multiplication
    if direction == "forward":
        match leg_part:
            case "thigh":
                if motors.__getitem__(0).rate != velocity:
                    motors.__getitem__(0).rate = velocity
            case "calf":
                if motors.__getitem__(1).rate != velocity:
                    motors.__getitem__(1).rate = velocity
            case "foot":
                if motors.__getitem__(2).rate != velocity:
                    motors.__getitem__(2).rate = velocity
    elif direction == "backward":
        match leg_part:
            case "thigh":
                if motors.__getitem__(0).rate != -velocity:
                    motors.__getitem__(0).rate = -velocity
            case "calf":
                if motors.__getitem__(1).rate != -velocity:
                    motors.__getitem__(1).rate = -velocity
            case "foot":
                if motors.__getitem__(2).rate != -velocity:
                    motors.__getitem__(2).rate = -velocity
    pass


def move_left_leg(motors: list[SimpleMotor], leg_part: str, direction: str, multiplication: float):
    velocity = constants.ROTATION_RATE * multiplication
    if direction == "forward":
        match leg_part:
            case "thigh":
                if motors.__getitem__(3).rate != velocity:
                    motors.__getitem__(3).rate = velocity
            case "calf":
                if motors.__getitem__(4).rate != velocity:
                    motors.__getitem__(4).rate = velocity
            case "foot":
                if motors.__getitem__(5).rate != velocity:
                    motors.__getitem__(5).rate = velocity
    elif direction == "backward":
        match leg_part:
            case "thigh":
                if motors.__getitem__(3).rate != -velocity:
                    motors.__getitem__(3).rate = -velocity
            case "calf":
                if motors.__getitem__(4).rate != -velocity:
                    motors.__getitem__(4).rate = -velocity
            case "foot":
                if motors.__getitem__(5).rate != -velocity:
                    motors.__getitem__(5).rate = -velocity
    pass


def stop_moving_right_leg(motors: list[SimpleMotor], leg_part: str):
    match leg_part:
        case "thigh":
            motors.__getitem__(0).rate = 0
        case "calf":
            motors.__getitem__(1).rate = 0
        case "foot":
            motors.__getitem__(2).rate = 0
    pass


def stop_moving_left_leg(motors: list[SimpleMotor], leg_part: str):
    match leg_part:
        case "thigh":
            motors.__getitem__(3).rate = 0
        case "calf":
            motors.__getitem__(4).rate = 0
        case "foot":
            motors.__getitem__(5).rate = 0
    pass


def set_thigh_start_position(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, used_scenario: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = leg.equations.get_angle("thigh", 0)
    if leg.relative_values[used_scenario].angle_thigh <= thigh_value:
        move_leg_function(motors, "thigh", "forward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        return True

    return False


def set_calf_start_position(leg: Leg, motors: list[SimpleMotor], calf_speed: float, used_scenario: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    calf_value = leg.equations.get_angle("calf", 0)
    if leg.relative_values[used_scenario].angle_calf >= calf_value:
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
            if leg.relative_values[used_scenario].angle_thigh >= thigh_value:
                move_leg_function(motors, "thigh", "backward", thigh_speed)
            else:
                stop_leg_function(motors, "thigh")
                end_thigh = True
        elif previous_thigh_value < thigh_value:
            if leg.relative_values[used_scenario].angle_thigh <= thigh_value:
                move_leg_function(motors, "thigh", "forward", thigh_speed)
            else:
                stop_leg_function(motors, "thigh")
                end_thigh = True
        else:
            stop_leg_function(motors, "thigh")
            end_thigh = True

        if calf_value < previous_calf_value:
            if leg.relative_values[used_scenario].angle_calf >= calf_value:
                move_leg_function(motors, "calf", "backward", calf_speed)
            else:
                stop_leg_function(motors, "calf")
                end_calf = True
        elif calf_value > previous_calf_value:
            if leg.relative_values[used_scenario].angle_calf <= calf_value:
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
