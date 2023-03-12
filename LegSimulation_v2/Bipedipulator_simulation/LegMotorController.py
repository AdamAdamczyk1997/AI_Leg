from pymunk import SimpleMotor

from LegSimulation_v2.Bipedipulator_simulation import constants
from LegSimulation_v2.Bipedipulator_simulation.Leg import Leg
from LegSimulation_v2.Bipedipulator_simulation.Model import Model
from LegSimulation_v2.Bipedipulator_simulation.RelativeValues import Counters
from LegSimulation_v2.Bipedipulator_simulation.constants import FLOOR_HEIGHT


def print_bool(status: bool):
    if status:
        return 'True'
    else:
        return 'False'


class Controller:
    loop_counter: int
    run_part_phase: bool
    current_phase: int
    before_start: bool
    mode: str
    right_foot_stabilize: bool
    left_foot_stabilize: bool

    right_thigh_speed: float
    right_cale_speed: float
    left_thigh_speed: float
    left_cale_speed: float

    temp_right_phase_first_part_usage_counter: int
    temp_right_phase_second_part_usage_counter: int
    temp_left_phase_first_part_usage_counter: int
    temp_left_phase_second_part_usage_counter: int
    temp_phase_usage_counter: int

    def __init__(self, model_entity: Model, mode: str):
        self.part_phase = 0
        self.current_phase = 0
        self.loop_counter = 0
        self.mode = mode
        self.right_foot_stabilize = True
        self.left_foot_stabilize = True
        self.right_thigh_speed = 0
        self.right_cale_speed = 0
        self.left_thigh_speed = 0
        self.left_cale_speed = 0
        self.reset_counters()

        self.temp_phase_usage_counter = 0

    def set_multiplication_of_motor_velocity(self, right_thigh_speed: float, right_cale_speed: float,
                                             left_thigh_speed: float, left_cale_speed: float):
        self.right_thigh_speed = right_thigh_speed
        self.right_cale_speed = right_cale_speed
        self.left_thigh_speed = left_thigh_speed
        self.left_cale_speed = left_cale_speed
        pass

    def reset_counters(self):
        self.temp_right_phase_first_part_usage_counter = 0
        self.temp_right_phase_second_part_usage_counter = 0
        self.temp_left_phase_first_part_usage_counter = 0
        self.temp_left_phase_second_part_usage_counter = 0

    def movement_scenario_controller(self, model_entity: Model, motors: list[SimpleMotor], simulate, time):
        if simulate:
            calculate_data(model_entity)

            right_thigh_speed = model_entity.right_leg.relative_values.velocities.thigh_velocity. \
                __getitem__(self.current_phase).__getitem__(self.part_phase)
            right_cale_speed = model_entity.right_leg.relative_values.velocities.cale_velocity. \
                __getitem__(self.current_phase).__getitem__(self.part_phase)
            left_thigh_speed = model_entity.left_leg.relative_values.velocities.thigh_velocity. \
                __getitem__(self.current_phase).__getitem__(self.part_phase)
            left_cale_speed = model_entity.left_leg.relative_values.velocities.cale_velocity. \
                __getitem__(self.current_phase).__getitem__(self.part_phase)

            model_entity.right_leg.relative_values.velocities.update_current_velocity(motors.__getitem__(0).rate,
                                                                                      motors.__getitem__(1).rate,
                                                                                      self.current_phase,
                                                                                      self.part_phase)
            model_entity.left_leg.relative_values.velocities.update_current_velocity(motors.__getitem__(3).rate,
                                                                                     motors.__getitem__(4).rate,
                                                                                     self.current_phase,
                                                                                     self.part_phase)
            self.set_multiplication_of_motor_velocity(right_thigh_speed, right_cale_speed, left_thigh_speed,
                                                      left_cale_speed)
            temp_end = self.run_phase_async(model_entity, motors, self.current_phase)

            return temp_end

    def change_current_phase(self, model_entity: Model):
        if self.current_phase < 6:
            self.current_phase += 1
        elif self.current_phase == 6:
            model_entity.right_leg.relative_values.counters[self.loop_counter].append_phase_usage_counter()
            model_entity.left_leg.relative_values.counters[self.loop_counter].append_phase_usage_counter()
            self.loop_counter += 1
            model_entity.right_leg.relative_values.counters.append(Counters())
            model_entity.left_leg.relative_values.counters.append(Counters())
            if self.loop_counter == 2:
                return True
            self.current_phase = 1

        return False

    def run_phase_async(self, model_entity: Model, motors, phase_nr: int):
        phase_function = ""
        match phase_nr:
            case 0:
                phase_function = phase_zero
            case 1:
                phase_function = phase_one
            case 2:
                phase_function = phase_two
            case 3:
                phase_function = phase_three
            case 4:
                phase_function = phase_four
            case 5:
                phase_function = phase_five
            case 6:
                phase_function = phase_six
        end_right = False
        end_left = False
        match self.part_phase:
            case 0:
                end_right = phase_function(model_entity.right_leg, motors, self.right_thigh_speed,
                                           self.right_cale_speed, self.current_phase, self.part_phase)
                model_entity.right_leg.relative_values.counters[self.loop_counter]. \
                    phase_part_usage_increment(self.current_phase, end_right)
                if end_right:
                    stop_moving_right_leg(motors, "thigh")
                    stop_moving_right_leg(motors, "cale")
                    print("End ", self.part_phase, " R:", self.current_phase)
                else:
                    self.temp_right_phase_first_part_usage_counter += 1

                end_left = phase_function(model_entity.left_leg, motors, self.left_thigh_speed,
                                          self.left_cale_speed, self.current_phase, self.part_phase)
                model_entity.left_leg.relative_values.counters[self.loop_counter]. \
                    phase_part_usage_increment(self.current_phase, end_left)
                if end_left:
                    stop_moving_left_leg(motors, "thigh")
                    stop_moving_left_leg(motors, "cale")
                    print("End ", self.part_phase, " L:", self.current_phase)
                else:
                    self.temp_left_phase_first_part_usage_counter += 1
                if end_right and end_left:
                    self.part_phase = 1
                    print("End first_part current phases")
            case 1:
                end_right = phase_function(model_entity.right_leg, motors, self.right_thigh_speed,
                                           self.right_cale_speed, self.current_phase, self.part_phase)
                model_entity.right_leg.relative_values.counters[self.loop_counter]. \
                    phase_part_usage_increment(self.current_phase, end_right)
                if end_right:
                    # self.fill_time(model_entity.right_leg, motors)
                    stop_moving_right_leg(motors, "thigh")
                    stop_moving_right_leg(motors, "cale")
                    print("End R:", self.current_phase)
                else:
                    self.temp_right_phase_second_part_usage_counter += 1

                end_left = phase_function(model_entity.left_leg, motors, self.left_thigh_speed,
                                          self.left_cale_speed, self.current_phase, self.part_phase)
                model_entity.left_leg.relative_values.counters[self.loop_counter]. \
                    phase_part_usage_increment(self.current_phase, end_left)
                if end_left:
                    stop_moving_left_leg(motors, "thigh")
                    stop_moving_left_leg(motors, "cale")
                    print("End L:", self.current_phase)
                else:
                    self.temp_left_phase_second_part_usage_counter += 1

                if end_right and end_left:
                    print("End second_part current phases")

                    self.part_phase = 0
                    model_entity.right_leg.relative_values.counters[self.loop_counter].append_phase_part_usage_counters(
                        [self.temp_right_phase_first_part_usage_counter,
                         self.temp_right_phase_second_part_usage_counter])
                    model_entity.left_leg.relative_values.counters[self.loop_counter].append_phase_part_usage_counters(
                        [self.temp_left_phase_first_part_usage_counter, self.temp_left_phase_second_part_usage_counter])
                    self.reset_counters()

                    model_entity.right_leg.relative_values.change_oscillation(self.current_phase)
                    model_entity.left_leg.relative_values.change_oscillation(self.current_phase)
                    temp_end = self.change_current_phase(model_entity)

                    return temp_end


def phase_zero(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int, part_phase: int):
    if part_phase == 0:
        end_thigh = align_thigh(leg, motors, thigh_speed)
        end_cale = align_cale(leg, motors, cale_speed)
        if end_thigh and end_cale:
            return True

    if part_phase == 1:
        end_thigh = set_thigh_start_position(leg, motors, thigh_speed)
        end_cale = set_cale_start_position(leg, motors, cale_speed)
        if end_thigh and end_cale:
            return True

    return False


def phase_one(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int, part_phase: int):
    if part_phase == 0:
        if leg.name == "right":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    if part_phase == 1:
        if leg.name == "right":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    return False


def phase_two(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int, part_phase: int):
    if part_phase == 0:
        if leg.name == "right":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    if part_phase == 1:
        if leg.name == "right":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = put_thigh_down(leg, motors, cale_speed, phase, part_phase)
            stop_moving_left_leg(motors, "cale")
            if end:
                return True

    return False


def phase_three(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int,
                part_phase: int):
    if part_phase == 0:
        if leg.name == "right":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = move_weight_to_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    if part_phase == 1:
        if leg.name == "right":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = move_weight_to_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    return False


def phase_four(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int, part_phase: int):
    if part_phase == 0:
        if leg.name == "right":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    if part_phase == 1:
        if leg.name == "right":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    return False


def phase_five(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int, part_phase: int):
    if part_phase == 0:
        if leg.name == "right":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    if part_phase == 1:
        if leg.name == "right":
            end = put_thigh_down(leg, motors, thigh_speed, phase, part_phase)
            stop_moving_right_leg(motors, "cale")
            if end:
                return True

        if leg.name == "left":
            end = move_leg_to_the_back(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    return False


def phase_six(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float, phase: int, part_phase: int):
    if part_phase == 0:
        if leg.name == "right":
            end = move_weight_to_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    if part_phase == 1:
        if leg.name == "right":
            end = move_weight_to_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

        if leg.name == "left":
            end = lifting_leg(leg, motors, thigh_speed, cale_speed, phase, part_phase)
            if end:
                return True

    return False


def lifting_leg(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float,
                phase: int, part_phase: int):
    end_thigh = False
    end_cale = False
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = leg.equations.get_angle("thigh", phase, part_phase)
    cale_value = leg.equations.get_angle("cale", phase, part_phase)

    if leg.relative_values.angle_thigh <= thigh_value:
        move_leg_function(motors, "thigh", "forward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        end_thigh = True
    if leg.relative_values.angle_cale <= cale_value:
        move_leg_function(motors, "cale", "forward", cale_speed)
    else:
        stop_leg_function(motors, "cale")
        end_cale = True
    if end_thigh and end_cale:
        return True

    return False


def move_leg_to_the_back(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float,
                         phase: int, part_phase: int):
    end_thigh = False
    end_cale = False
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = leg.equations.get_angle("thigh", phase, part_phase)
    cale_value = leg.equations.get_angle("cale", phase, part_phase)

    if leg.relative_values.angle_thigh >= thigh_value:
        move_leg_function(motors, "thigh", "backward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        end_thigh = True
    if leg.relative_values.angle_cale >= cale_value:
        move_leg_function(motors, "cale", "backward", cale_speed)
    else:
        stop_leg_function(motors, "cale")
        end_cale = True
    if end_thigh and end_cale:
        return True

    return False


def move_weight_to_leg(leg: Leg, motors: list[SimpleMotor], thigh_speed: float, cale_speed: float,
                       phase: int, part_phase: int):
    end_thigh = False
    end_cale = False
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = leg.equations.get_angle("thigh", phase, part_phase)
    cale_value = leg.equations.get_angle("cale", phase, part_phase)
    cale_direction = ""
    match part_phase:
        case 0:
            cale_direction = "backward"
        case 1:
            cale_direction = "forward"

    if leg.relative_values.angle_thigh >= thigh_value:
        move_leg_function(motors, "thigh", "backward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        end_thigh = True
    if leg.relative_values.angle_cale <= cale_value:
        move_leg_function(motors, "cale", cale_direction, cale_speed)
    else:
        stop_leg_function(motors, "cale")
        end_cale = True
    if end_thigh and end_cale:
        return True

    return False


def put_thigh_down(leg: Leg, motors: list[SimpleMotor], multiplication: float, phase: int, part_phase: int):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    angle_thigh = leg.equations.get_angle("thigh", phase, part_phase)
    if leg.relative_values.angle_thigh >= angle_thigh:
        move_leg_function(motors, "thigh", "backward", multiplication)
    else:
        stop_leg_function(motors, "thigh")
        return True

    return False


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


def calculate_data(model_entity: Model):
    model_entity.right_leg.relative_values.body_velocity(model_entity.right_leg.pivots.__getitem__(0), "hip")
    model_entity.right_leg.relative_values.body_velocity(model_entity.right_leg.knee_body, "knee")
    model_entity.right_leg.relative_values.body_velocity(model_entity.right_leg.ankle_body, "ankle")
    model_entity.left_leg.relative_values.body_velocity(model_entity.left_leg.pivots.__getitem__(0), "hip")
    model_entity.left_leg.relative_values.body_velocity(model_entity.left_leg.knee_body, "knee")
    model_entity.left_leg.relative_values.body_velocity(model_entity.left_leg.ankle_body, "ankle")
    model_entity.right_leg.relative_values.calculate_angles(
        model_entity.pivots.__getitem__(0).position,
        model_entity.right_leg.knee_body.position,
        model_entity.right_leg.ankle_body.position,
        model_entity.right_leg.pivots.__getitem__(2).position)

    model_entity.left_leg.relative_values.calculate_angles(
        model_entity.pivots.__getitem__(0).position,
        model_entity.left_leg.knee_body.position,
        model_entity.left_leg.ankle_body.position,
        model_entity.left_leg.pivots.__getitem__(2).position)
    pass


def move_right_leg(motors: list[SimpleMotor], leg_part: str, direction: str, multiplication: float):
    velocity = constants.ROTATION_RATE * multiplication
    if direction == "forward":  # for foot toe up
        match leg_part:
            case "thigh":
                if motors.__getitem__(0).rate != velocity:
                    motors.__getitem__(0).rate = velocity
            case "cale":
                if motors.__getitem__(1).rate != velocity:
                    motors.__getitem__(1).rate = velocity
            case "foot":
                if motors.__getitem__(2).rate != velocity:
                    motors.__getitem__(2).rate = velocity
    elif direction == "backward":  # for foot toe down
        match leg_part:
            case "thigh":
                if motors.__getitem__(0).rate != -velocity:
                    motors.__getitem__(0).rate = -velocity
            case "cale":
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
            case "cale":
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
            case "cale":
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
        case "cale":
            motors.__getitem__(1).rate = 0
        case "foot":
            motors.__getitem__(2).rate = 0
    pass


def stop_moving_left_leg(motors: list[SimpleMotor], leg_part: str):
    match leg_part:
        case "thigh":
            motors.__getitem__(3).rate = 0
        case "cale":
            motors.__getitem__(4).rate = 0
        case "foot":
            motors.__getitem__(5).rate = 0
    pass


def align_thigh(leg: Leg, motors: list[SimpleMotor], thigh_speed: float):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    if leg.relative_values.angle_thigh < 0.1:
        move_leg_function(motors, "thigh", "forward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        return True

    return False


def align_cale(leg: Leg, motors: list[SimpleMotor], cale_speed: float):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    if leg.relative_values.angle_cale > -0.1:
        move_leg_function(motors, "cale", "backward", cale_speed)
    else:
        stop_leg_function(motors, "cale")
        return True

    return False


def set_thigh_start_position(leg: Leg, motors: list[SimpleMotor], thigh_speed: float):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    thigh_value = 0.0
    match leg.name:
        case "right":
            thigh_value = 0.2
        case "left":
            thigh_value = 0.24
    if leg.relative_values.angle_thigh <= thigh_value:
        move_leg_function(motors, "thigh", "forward", thigh_speed)
    else:
        stop_leg_function(motors, "thigh")
        return True

    return False


def set_cale_start_position(leg: Leg, motors: list[SimpleMotor], cale_speed: float):
    move_leg_function = choose_leg_functions(leg, True)
    stop_leg_function = choose_leg_functions(leg, False)
    cale_value = 0.0
    match leg.name:
        case "right":
            cale_value = -0.2
        case "left":
            cale_value = -0.40
    if leg.relative_values.angle_cale >= cale_value:
        move_leg_function(motors, "cale", "backward", cale_speed)
    else:
        stop_leg_function(motors, "cale")
        return True

    return False
