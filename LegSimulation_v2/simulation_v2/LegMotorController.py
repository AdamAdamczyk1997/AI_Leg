import string
from ctypes import Union

import pymunk
from pymunk import SimpleMotor

from LegSimulation_v2.simulation_v2 import constants
from LegSimulation_v2.simulation_v2.Leg import Leg
from LegSimulation_v2.simulation_v2.Model import Model
from LegSimulation_v2.simulation_v2.constants import FOOT_HEIGHT, FLOOR_HEIGHT


def print_bool(status: bool):
    if status:
        return 'True'
    else:
        return 'False'


class LegStatus:
    phase_id: int
    is_moving: bool
    is_standing_on_the_ground: bool
    is_leading: bool
    is_lifting: bool
    is_up: bool
    is_straightening: bool
    is_straight: bool

    def __init__(self, model_entity: Model, leg: Leg):
        self.update(model_entity, leg)
        self.phase_id = 0
        self.is_moving = False
        self.is_standing_on_the_ground = True
        self.is_leading = False
        self.is_lifting = False
        self.is_up = False
        self.is_straightening = False
        self.is_straight = True

    def update(self, model_entity: Model, leg: Leg):
        self.is_straight = False if (leg.relative_values.angle_thigh - leg.relative_values.angle_cale) > 0.05 else True
        if len(leg.relative_values.histories) > 2:
            self.check_leader(model_entity, leg)
            # self.check_is_lifting(leg)
            # self.check_is_straightening(leg)
            # self.check_is_standing_on_the_ground(leg)

    def check_leader(self, model_entity: Model, leg: Leg):
        lead = model_entity.right_leg.name if \
            model_entity.right_leg.foot.body.position.x > model_entity.left_leg.foot.body.position.x else \
            model_entity.left_leg.name
        self.is_leading = True if leg.name == lead else False

    def check_is_lifting(self, leg: Leg):
        current_status = leg.relative_values.histories[-1][5]
        previous_status = leg.relative_values.histories[-2][5]
        self.is_lifting = True if current_status > previous_status else False

    def check_is_straightening(self, leg: Leg):
        if not self.is_straight:
            current_difference_angle = leg.relative_values.angle_thigh - leg.relative_values.angle_cale
            previous_difference_angle = leg.relative_values.histories[-2][3] - leg.relative_values.histories[-2][6]
            self.is_straightening = True if current_difference_angle < previous_difference_angle else False

    def check_is_standing_on_the_ground(self, leg: Leg):
        self.is_standing_on_the_ground = True if ((leg.pivots.__getitem__(2).position.y == FLOOR_HEIGHT)
                                                  | (leg.pivots.__getitem__(3).position.y == FLOOR_HEIGHT)) else \
            False

    def show_leg_status(self):
        print("================================")
        print("phase_id:", self.phase_id)
        print("is_moving:", print_bool(self.is_moving))
        print("is_standing_on_the_ground:", print_bool(self.is_standing_on_the_ground))
        print("is_leading:", print_bool(self.is_leading))
        print("is_lifting:", print_bool(self.is_lifting))
        print("is_up:", print_bool(self.is_up))
        print("is_straightening:", print_bool(self.is_straightening))
        print("is_straight:", print_bool(self.is_straight))


class Controller:
    loop_counter: int
    run_flag: bool
    right_leg_status: LegStatus
    left_leg_status: LegStatus
    walk_phases_leg_right: list[LegStatus]
    walk_phases_leg_left: list[LegStatus]
    current_phase_for_right: int
    current_phase_for_left: int
    before_start: bool
    mode: str
    right_foot_stabilize: bool
    left_foot_stabilize: bool

    def __init__(self, model_entity: Model, mode: str):
        self.run_flag = True
        self.right_leg_status = LegStatus(model_entity, model_entity.right_leg)
        self.left_leg_status = LegStatus(model_entity, model_entity.left_leg)
        self.walk_phases_leg_left = fill_walk_phases_leg_left(model_entity, model_entity.left_leg)
        self.walk_phases_leg_right = fill_walk_phases_leg_right(model_entity, model_entity.right_leg)
        self.current_phase_for_right = 0
        self.current_phase_for_left = 0
        self.loop_counter = 0
        self.mode = mode
        self.right_foot_stabilize = True
        self.left_foot_stabilize = True

    def movement_scenario_controller(self, model_entity: Model, motors: list[SimpleMotor], simulate, time):
        if simulate:
            model_entity.right_leg.relative_values.calculate_angles(
                model_entity.pivots.__getitem__(0).position,
                model_entity.right_leg.knee_body.position,
                model_entity.right_leg.ankle_body.position,
                model_entity.right_leg.pivots.__getitem__(2).position,
                model_entity.right_leg.pivots.__getitem__(3).position,
                model_entity.right_leg.pivots.__getitem__(4).position)

            model_entity.left_leg.relative_values.calculate_angles(
                model_entity.pivots.__getitem__(0).position,
                model_entity.left_leg.knee_body.position,
                model_entity.left_leg.ankle_body.position,
                model_entity.left_leg.pivots.__getitem__(2).position,
                model_entity.left_leg.pivots.__getitem__(3).position,
                model_entity.right_leg.pivots.__getitem__(4).position)

            self.choose_function_due_to_phase_v2(model_entity, motors)

        pass

    def choose_function_due_to_phase_v2(self, model_entity, motors):
        self.run_phase_async(model_entity, motors, 0)
        self.run_phase_async(model_entity, motors, 1)
        self.run_phase_async(model_entity, motors, 2)
        self.run_phase_async(model_entity, motors, 3)
        self.run_phase_async(model_entity, motors, 4)
        self.run_phase_async(model_entity, motors, 5)
        self.run_phase_async(model_entity, motors, 6)

        pass

    def change_current_phase(self, leg: str):
        match leg:
            case "right":
                if self.current_phase_for_right < 6:
                    self.current_phase_for_right += 1
                elif self.current_phase_for_right == 6:
                    self.current_phase_for_right = 1
            case "left":
                if self.current_phase_for_left < 6:
                    self.current_phase_for_left += 1
                elif self.current_phase_for_left == 6:
                    self.current_phase_for_left = 1

    def run_phase_async(self, model_entity, motors, phase_nr: int):
        first_part = 0
        second_part = 1
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
        if self.run_flag:
            if self.current_phase_for_right == phase_nr:
                end_right = phase_function(model_entity.right_leg, motors, first_part)
                if end_right:
                    stop_moving_right_leg(motors, "thigh")
                    stop_moving_right_leg(motors, "cale")
                    print("End ", first_part, " R:", self.current_phase_for_right)
            if self.current_phase_for_left == phase_nr:
                end_left = phase_function(model_entity.left_leg, motors, first_part)
                if end_left:
                    stop_moving_left_leg(motors, "thigh")
                    stop_moving_left_leg(motors, "cale")
                    print("End ", first_part, " L:", self.current_phase_for_left)
            if end_right and end_left:
                self.run_flag = False
                print("End first_part current phases")

        if not self.run_flag:
            if self.current_phase_for_right == phase_nr:
                end_right = phase_function(model_entity.right_leg, motors, second_part)
                if end_right:
                    stop_moving_right_leg(motors, "thigh")
                    stop_moving_right_leg(motors, "cale")
                    print("End R:", self.current_phase_for_right)
            if self.current_phase_for_left == phase_nr:
                end_left = phase_function(model_entity.left_leg, motors, second_part)
                if end_left:
                    stop_moving_left_leg(motors, "thigh")
                    stop_moving_left_leg(motors, "cale")
                    print("End L:", self.current_phase_for_left)
            if end_right and end_left:
                print("End second_part current phases")
                self.change_current_phase("right")
                self.change_current_phase("left")
                self.run_flag = True


def phase_zero(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        end_thigh = align_thigh(leg, motors, 0.5)
        end_cale = align_cale(leg, motors, 0.5)
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            if leg.relative_values.angle_cale >= -0.25:
                move_right_leg(motors, "cale", "backward", 1)
            # elif -0.2 > leg.relative_values.angle_cale >= -0.25:
            #     move_right_leg(motors, "cale", "backward", 0.5)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
            if leg.relative_values.angle_thigh <= 0.25:
                move_right_leg(motors, "thigh", "forward", 1)
            # elif 0.2 < leg.relative_values.angle_thigh <= 0.25:
            #     move_right_leg(motors, "thigh", "forward", 0.5)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True

        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_cale >= -0.25:
                move_left_leg(motors, "cale", "backward", 1)
            # elif -0.2 > leg.relative_values.angle_cale >= -0.25:
            #     move_left_leg(motors, "cale", "backward", 0.5)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
            if leg.relative_values.angle_thigh <= 0.25:
                move_left_leg(motors, "thigh", "forward", 1)
            # elif 0.2 < leg.relative_values.angle_thigh <= 0.25:
            #     move_left_leg(motors, "thigh", "forward", 0.5)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True

        if end_thigh and end_cale:
            return True

    return False


def phase_one(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        if leg.name == "right":
            stop_moving_right_leg(motors, "thigh")
            end_thigh = True
            stop_moving_right_leg(motors, "cale")
            end_cale = True
            if end_thigh and end_cale:
                return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh <= 0.3:
                move_left_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.3:
                move_left_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            if leg.relative_values.angle_thigh >= 0.12:
                move_right_leg(motors, "thigh", "backward", 1)
            elif 0.12 > leg.relative_values.angle_thigh >= 0.1:
                move_right_leg(motors, "thigh", "backward", 0.5)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.28:
                move_right_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh <= 0.45:
                move_left_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale <= -0.25:
                move_left_leg(motors, "cale", "forward", 0.5)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    return False


def phase_two(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        if leg.name == "right":
            stop_moving_right_leg(motors, "thigh")
            end_thigh = True
            if leg.relative_values.angle_cale >= -0.3:
                move_right_leg(motors, "cale", "backward", 0.5)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            stop_moving_left_leg(motors, "thigh")
            end_thigh = True
            if leg.relative_values.angle_cale <= -0.1:
                move_left_leg(motors, "cale", "forward", 1)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            if leg.relative_values.angle_thigh >= 0.0:
                move_right_leg(motors, "thigh", "backward", 0.5)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            end_thigh = put_leg_down(leg, motors)
            stop_moving_left_leg(motors, "cale")
            end_cale = True
        if end_thigh and end_cale:
            return True

    return False


def phase_three(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        if leg.name == "right":
            if leg.relative_values.angle_thigh <= 0.0:
                move_right_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.6:
                move_right_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh <= 0.25:
                move_left_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.3:
                move_left_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            if leg.relative_values.angle_thigh <= 0.3:
                move_right_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.7:
                move_right_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh >= 0.25:
                move_left_leg(motors, "thigh", "backward", 1)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale <= -0.3:
                move_left_leg(motors, "cale", "forward", 1)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    return False


def phase_four(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        if leg.name == "right":
            if leg.relative_values.angle_thigh <= 0.3:
                move_right_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale <= -0.3:
                move_right_leg(motors, "cale", "forward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            stop_moving_left_leg(motors, "thigh")
            end_thigh = True
            stop_moving_left_leg(motors, "cale")
            end_cale = True
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            if leg.relative_values.angle_thigh <= 0.45:
                move_right_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale <= -0.25:
                move_right_leg(motors, "cale", "forward", 0.5)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh >= 0.12:
                move_left_leg(motors, "thigh", "backward", 1)
            elif 0.12 > leg.relative_values.angle_thigh >= 0.1:
                move_left_leg(motors, "thigh", "backward", 0.5)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.28:
                move_left_leg(motors, "cale", "backward", 1)
            elif -0.28 > leg.relative_values.angle_cale >= -0.3:
                move_left_leg(motors, "cale", "backward", 0.5)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    return False


def phase_five(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        if leg.name == "right":
            stop_moving_right_leg(motors, "thigh")
            end_thigh = True
            if leg.relative_values.angle_cale <= -0.1:
                move_right_leg(motors, "cale", "forward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            stop_moving_left_leg(motors, "thigh")
            end_thigh = True
            if leg.relative_values.angle_cale >= -0.35:
                move_left_leg(motors, "cale", "backward", 0.5)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            end_thigh = put_leg_down(leg, motors)
            stop_moving_right_leg(motors, "cale")
            end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh >= 0.0:
                move_left_leg(motors, "thigh", "backward", 0.5)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    return False


def phase_six(leg: Leg, motors: list[SimpleMotor], flag: int):
    end_thigh = False
    end_cale = False
    if flag == 0:
        if leg.name == "right":
            if leg.relative_values.angle_thigh <= 0.25:
                move_right_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.3:
                move_right_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh <= 0.0:
                move_left_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.6:
                move_left_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    if flag == 1:
        if leg.name == "right":
            if leg.relative_values.angle_thigh >= 0.25:
                move_right_leg(motors, "thigh", "backward", 1)
            else:
                stop_moving_right_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale <= -0.3:
                move_right_leg(motors, "cale", "forward", 1)
            else:
                stop_moving_right_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

        if leg.name == "left":
            if leg.relative_values.angle_thigh <= 0.3:
                move_left_leg(motors, "thigh", "forward", 1)
            else:
                stop_moving_left_leg(motors, "thigh")
                end_thigh = True
            if leg.relative_values.angle_cale >= -0.7:
                move_left_leg(motors, "cale", "backward", 1)
            else:
                stop_moving_left_leg(motors, "cale")
                end_cale = True
        if end_thigh and end_cale:
            return True

    return False


def move_thigh_backward(leg: Leg, motors: list[SimpleMotor]):
    if leg.name == "right":
        if -0.15 < leg.relative_values.angle_thigh:
            # move_heel_up(leg, motors)
            move_right_leg(motors, "thigh", "backward")
            if -0.2 < leg.relative_values.angle_cale:
                move_right_leg(motors, "cale", "backward")
            else:
                stop_moving_right_leg(motors, "cale")
        else:
            # move_heel_down(leg, motors)
            stop_moving_right_leg(motors, "cale")
            stop_moving_right_leg(motors, "thigh")
            return True

    elif leg.name == "left":
        if -0.15 < leg.relative_values.angle_thigh:
            # move_heel_up(leg, motors)
            move_left_leg(motors, "thigh", "backward")
            if -0.2 < leg.relative_values.angle_cale:
                move_left_leg(motors, "cale", "backward")
            else:
                stop_moving_left_leg(motors, "cale")
        else:
            # move_heel_down(leg, motors)
            stop_moving_left_leg(motors, "cale")
            stop_moving_left_leg(motors, "thigh")
            return True

    return False


def align_thigh(leg: Leg, motors: list[SimpleMotor], multiplication: float):
    if leg.name == "right":
        if leg.relative_values.angle_thigh > 0.05:
            move_right_leg(motors, "thigh", "backward", multiplication)
        elif leg.relative_values.angle_thigh < -0.05:
            move_right_leg(motors, "thigh", "forward", multiplication)
        else:
            stop_moving_right_leg(motors, "thigh")
            return True

    elif leg.name == "left":
        if leg.relative_values.angle_thigh > 0.05:
            move_left_leg(motors, "thigh", "backward", multiplication)
        elif leg.relative_values.angle_thigh < -0.05:
            move_left_leg(motors, "thigh", "backward", multiplication)
        else:
            stop_moving_left_leg(motors, "thigh")
            return True

    return False


def align_cale(leg: Leg, motors: list[SimpleMotor], multiplication: float):
    if leg.name == "right":
        if leg.relative_values.angle_cale < -0.05:
            move_right_leg(motors, "cale", "forward", multiplication)
        else:
            stop_moving_right_leg(motors, "cale")
            return True

    elif leg.name == "left":
        if leg.relative_values.angle_cale < -0.05:
            move_left_leg(motors, "cale", "forward", multiplication)
        else:
            stop_moving_left_leg(motors, "cale")
            return True

    return False


def lift_leg(leg: Leg, motors: list[SimpleMotor]):
    complete_one = False
    complete_second = False
    if leg.name == "right":
        if -0.2 < leg.relative_values.angle_cale:
            move_right_leg(motors, "cale", "backward")
        else:
            stop_moving_right_leg(motors, "cale")
            complete_second = True
        if leg.relative_values.angle_thigh < 0.2:
            move_right_leg(motors, "thigh", "forward")
        else:
            stop_moving_right_leg(motors, "thigh")
            complete_one = True

    elif leg.name == "left":
        if -0.2 < leg.relative_values.angle_cale:
            move_left_leg(motors, "cale", "backward")
        else:
            stop_moving_left_leg(motors, "cale")
            complete_second = True
        if leg.relative_values.angle_thigh < 0.2:
            move_left_leg(motors, "thigh", "forward")
        else:
            stop_moving_left_leg(motors, "thigh")
            complete_one = True

    if complete_one & complete_second:
        return True
    else:
        return False


def put_leg_down(leg: Leg, motors: list[SimpleMotor]):
    if leg.name == "right":
        if leg.relative_values.angle_thigh >= 0.4:
            move_right_leg(motors, "thigh", "backward", 1)
        else:
            stop_moving_right_leg(motors, "thigh")
            return True

    elif leg.name == "left":
        if leg.relative_values.angle_thigh >= 0.4:
            move_left_leg(motors, "thigh", "backward", 1)
        else:
            stop_moving_left_leg(motors, "thigh")
            return True

    return False


def straight_leg(leg: Leg, motors: list[SimpleMotor], entirely: bool):
    if entirely:
        difference = 0.2
    else:
        difference = 0.3
    if leg.name == "right":
        if leg.relative_values.angle_cale < leg.relative_values.angle_thigh - difference:
            move_right_leg(motors, "cale", "forward")
        else:
            stop_moving_right_leg(motors, "cale")
            return True

    if leg.name == "left":
        if leg.relative_values.angle_cale < leg.relative_values.angle_thigh - difference:
            move_left_leg(motors, "cale", "forward")
        else:
            stop_moving_left_leg(motors, "cale")
            return True

    return False


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


def fill_walk_phases_leg_left(model_entity: Model, leg: Leg):
    zero = LegStatus(model_entity, leg)
    zero.phase_id = 0
    zero.is_moving = False
    zero.is_standing_on_the_ground = True
    zero.is_leading = False
    zero.is_lifting = True
    zero.is_up = False
    zero.is_straightening = False
    zero.is_straight = True

    one = LegStatus(model_entity, leg)
    one.phase_id = 1
    one.is_moving = True
    one.is_standing_on_the_ground = False
    one.is_leading = True
    one.is_lifting = True
    one.is_up = False
    one.is_straightening = False
    one.is_straight = False

    two = LegStatus(model_entity, leg)
    two.phase_id = 2
    two.is_moving = False
    two.is_standing_on_the_ground = False
    two.is_leading = True
    two.is_lifting = False
    two.is_up = True
    two.is_straightening = False
    two.is_straight = False

    three = LegStatus(model_entity, leg)
    three.phase_id = 3
    three.is_moving = True
    three.is_standing_on_the_ground = False
    three.is_leading = True
    three.is_lifting = False
    three.is_up = True
    three.is_straightening = True
    three.is_straight = False

    four = LegStatus(model_entity, leg)
    four.phase_id = 4
    four.is_moving = False
    four.is_standing_on_the_ground = True
    four.is_leading = True
    four.is_lifting = False
    four.is_up = False
    four.is_straightening = False
    four.is_straight = True

    five = LegStatus(model_entity, leg)
    five.phase_id = 5
    five.is_moving = True
    five.is_standing_on_the_ground = True
    five.is_leading = True
    five.is_lifting = False
    five.is_up = False
    five.is_straightening = False
    five.is_straight = True

    six = LegStatus(model_entity, leg)
    six.phase_id = 6
    six.is_moving = True
    six.is_standing_on_the_ground = True
    six.is_leading = False
    six.is_lifting = False
    six.is_up = False
    six.is_straightening = False
    six.is_straight = True

    walk_phases = [zero, one, two, three, four, five, six]

    return walk_phases


def fill_walk_phases_leg_right(model_entity: Model, leg: Leg):
    zero = LegStatus(model_entity, leg)
    zero.phase_id = 0
    zero.is_moving = False
    zero.is_standing_on_the_ground = True
    zero.is_leading = False
    zero.is_lifting = True
    zero.is_up = False
    zero.is_straightening = False
    zero.is_straight = True

    one = LegStatus(model_entity, leg)
    one.phase_id = 1
    one.is_moving = True
    one.is_standing_on_the_ground = True
    one.is_leading = False
    one.is_lifting = False
    one.is_up = False
    one.is_straightening = False
    one.is_straight = True

    two = LegStatus(model_entity, leg)
    two.phase_id = 2
    two.is_moving = False
    two.is_standing_on_the_ground = False
    two.is_leading = True
    two.is_lifting = False
    two.is_up = True
    two.is_straightening = False
    two.is_straight = False

    three = LegStatus(model_entity, leg)
    three.phase_id = 3
    three.is_moving = True
    three.is_standing_on_the_ground = False
    three.is_leading = True
    three.is_lifting = False
    three.is_up = True
    three.is_straightening = True
    three.is_straight = False

    four = LegStatus(model_entity, leg)
    four.phase_id = 4
    four.is_moving = False
    four.is_standing_on_the_ground = True
    four.is_leading = True
    four.is_lifting = False
    four.is_up = False
    four.is_straightening = False
    four.is_straight = True

    five = LegStatus(model_entity, leg)
    five.phase_id = 5
    five.is_moving = True
    five.is_standing_on_the_ground = True
    five.is_leading = True
    five.is_lifting = False
    five.is_up = False
    five.is_straightening = False
    five.is_straight = True

    six = LegStatus(model_entity, leg)
    six.phase_id = 6
    six.is_moving = True
    six.is_standing_on_the_ground = True
    six.is_leading = False
    six.is_lifting = False
    six.is_up = False
    six.is_straightening = False
    six.is_straight = True

    walk_phases = [zero, one, two, three, four, five, six]

    return walk_phases
