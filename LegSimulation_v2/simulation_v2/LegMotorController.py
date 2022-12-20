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
    current_phase: int
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
        self.current_phase = 0
        self.loop_counter = 0
        self.mode = mode
        self.right_foot_stabilize = True
        self.left_foot_stabilize = True

    def foot_stabilize(self, model_entity: Model, motors: list[SimpleMotor], right_switch: bool, left_switch: bool):
        if right_switch:
            if model_entity.right_leg.pivots.__getitem__(2).position.y >= \
                    model_entity.right_leg.pivots.__getitem__(3).position.y + 2:
                move_right_leg(motors, "foot", "backward")
            elif model_entity.right_leg.pivots.__getitem__(2).position.y < \
                    model_entity.right_leg.pivots.__getitem__(3).position.y - 2:
                move_right_leg(motors, "foot", "forward")
            else:
                stop_moving_right_leg(motors, "foot")

        if left_switch:
            if model_entity.left_leg.pivots.__getitem__(2).position.y > \
                    model_entity.left_leg.pivots.__getitem__(3).position.y + 2:
                move_left_leg(motors, "foot", "backward")
            elif model_entity.left_leg.pivots.__getitem__(2).position.y < \
                    model_entity.left_leg.pivots.__getitem__(3).position.y - 2:
                move_left_leg(motors, "foot", "forward")
            else:
                stop_moving_left_leg(motors, "foot")

        pass

    def movement_scenario_controller(self, model_entity: Model, motors: list[SimpleMotor], simulate, time):
        # self.right_leg_status.update(model_entity, model_entity.right_leg)
        # self.left_leg_status.update(model_entity, model_entity.left_leg)

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

        if simulate & (time % 5 == 0):
            if self.loop_counter == 0:
                self.loop_counter += 1
                print("loop_counter =", self.loop_counter)
                self.change_current_phase()

            self.choose_function_due_to_phase(model_entity, motors)
            # self.foot_stabilize(model_entity, motors, self.right_foot_stabilize, self.left_foot_stabilize)

        pass

    def choose_function_due_to_phase(self, model_entity: Model, motors: list[SimpleMotor]):
        if self.loop_counter == 1:
            if -0.1 < model_entity.right_leg.relative_values.angle_cale:
                move_right_leg(motors, "thigh", "backward")
            else:
                stop_moving_right_leg(motors, "thigh")
            end = lift_leg(model_entity.left_leg, motors)
            if end:
                stop_moving_right_leg(motors, "cale")
                self.change_current_phase()
        else:
            if self.current_phase == 1:
                end_second = lift_leg(model_entity.left_leg, motors)
                if self.mode == "Non-AI mode":
                    end_first = align_thigh(model_entity.right_leg, motors)
                    straight_leg(model_entity.right_leg, motors, True)
                else:
                    end_first = True
                if end_first & end_second:
                    self.change_current_phase()

        if self.current_phase == 2:
            end = straight_leg(model_entity.left_leg, motors, False)
            if end:
                self.change_current_phase()

        elif self.current_phase == 3:
            end_first = put_leg_down(model_entity.left_leg, motors)
            if self.mode == "Non-AI mode":
                self.right_foot_stabilize = False
                end_second = move_thigh_backward(model_entity.right_leg, motors)
            else:
                end_second = True
            if end_first & end_second:
                self.right_foot_stabilize = True
                self.change_current_phase()

        elif self.current_phase == 4:
            if self.mode == "Non-AI mode":
                end_second = lift_leg(model_entity.right_leg, motors)
            else:
                end_second = True
            end_first = align_thigh(model_entity.left_leg, motors)
            straight_leg(model_entity.left_leg, motors, True)
            if end_first & end_second:
                self.change_current_phase()

        elif self.current_phase == 5:
            if self.mode == "Non-AI mode":
                end_first = straight_leg(model_entity.right_leg, motors, False)
            else:
                end_first = True
            if end_first:
                self.change_current_phase()

        elif self.current_phase == 6:
            # self.left_foot_stabilize = False
            end_second = move_thigh_backward(model_entity.left_leg, motors)
            if self.mode == "Non-AI mode":
                end_first = put_leg_down(model_entity.right_leg, motors)
            else:
                end_first = True
            if end_first & end_second:
                # self.left_foot_stabilize = True
                self.loop_counter += 1
                print("loop_counter =", self.loop_counter)
                self.change_current_phase()

    def change_current_phase(self):
        if self.current_phase < 6:
            self.current_phase += 1
        elif self.current_phase == 6:
            self.current_phase = 1
        print("Phase left:", self.current_phase)


def move_heel_up(leg: Leg, motors: list[SimpleMotor]):
    if leg.name == "right":
        if -0.1 < leg.relative_values.angle_foot:
            move_right_leg(motors, "foot", "backward")
        else:
            stop_moving_right_leg(motors, "foot")
            return True

    elif leg.name == "left":
        if -0.1 < leg.relative_values.angle_foot:
            move_left_leg(motors, "foot", "backward")
        else:
            stop_moving_left_leg(motors, "foot")
            return True

    return False


def move_heel_down(leg: Leg, motors: list[SimpleMotor]):
    if leg.name == "right":
        if leg.relative_values.angle_foot < 0.0:
            move_right_leg(motors, "foot", "forward")
        else:
            stop_moving_right_leg(motors, "foot")
            return True

    elif leg.name == "left":
        if leg.relative_values.angle_foot < 0.0:
            move_left_leg(motors, "foot", "forward")
        else:
            stop_moving_left_leg(motors, "foot")
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


def align_thigh(leg: Leg, motors: list[SimpleMotor]):
    if leg.name == "right":
        if leg.relative_values.angle_thigh > 0.1:
            move_right_leg(motors, "thigh", "backward")
        else:
            stop_moving_right_leg(motors, "thigh")
            return True

    elif leg.name == "left":
        if leg.relative_values.angle_thigh > 0.1:
            move_left_leg(motors, "thigh", "backward")
        else:
            stop_moving_left_leg(motors, "thigh")
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
        if leg.pivots.__getitem__(3).position.y == 6:
            move_right_leg(motors, "thigh", "backward")
        else:
            stop_moving_right_leg(motors, "thigh")
            return True

    elif leg.name == "left":
        if leg.pivots.__getitem__(3).position.y == 6:
            move_left_leg(motors, "thigh", "backward")
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


def move_right_leg(motors: list[SimpleMotor], leg_part: str, direction: str):
    if direction == "forward":  # for foot toe up
        match leg_part:
            case "thigh":
                motors.__getitem__(0).rate = constants.ROTATION_RATE
            case "cale":
                motors.__getitem__(1).rate = constants.ROTATION_RATE
            case "foot":
                motors.__getitem__(2).rate = constants.ROTATION_RATE
    elif direction == "backward":  # for foot toe down
        match leg_part:
            case "thigh":
                motors.__getitem__(0).rate = -constants.ROTATION_RATE
            case "cale":
                motors.__getitem__(1).rate = -constants.ROTATION_RATE
            case "foot":
                motors.__getitem__(2).rate = -constants.ROTATION_RATE
    pass


def move_left_leg(motors: list[SimpleMotor], leg_part: str, direction: str):
    if direction == "forward":
        match leg_part:
            case "thigh":
                motors.__getitem__(3).rate = constants.ROTATION_RATE
            case "cale":
                motors.__getitem__(4).rate = constants.ROTATION_RATE
            case "foot":
                motors.__getitem__(5).rate = constants.ROTATION_RATE
    elif direction == "backward":
        match leg_part:
            case "thigh":
                motors.__getitem__(3).rate = -constants.ROTATION_RATE
            case "cale":
                motors.__getitem__(4).rate = -constants.ROTATION_RATE
            case "foot":
                motors.__getitem__(5).rate = -constants.ROTATION_RATE
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
