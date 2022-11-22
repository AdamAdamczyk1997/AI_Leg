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
            self.check_is_lifting(leg)
            self.check_is_straightening(leg)
            self.check_is_standing_on_the_ground(leg)

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
    run_flag: bool
    right_leg_status: LegStatus
    left_leg_status: LegStatus
    walk_phases_leg_right: list[LegStatus]
    walk_phases_leg_left: list[LegStatus]
    current_phase_left: int
    current_phase_right: int

    def __init__(self, model_entity: Model):
        self.run_flag = True
        self.right_leg_status = LegStatus(model_entity, model_entity.right_leg)
        self.left_leg_status = LegStatus(model_entity, model_entity.left_leg)
        self.walk_phases_leg_left = fill_walk_phases_leg_left(model_entity, model_entity.left_leg)
        self.current_phase_left = 0
        self.change_current_phase("left")

    def feet_stabilize(self, model_entity: Model, motors: list[SimpleMotor]):
        if model_entity.right_leg.pivots.__getitem__(2).position.y >= \
                model_entity.right_leg.pivots.__getitem__(3).position.y + 2:
            move_right_leg(motors, "foot", "backward")
        elif model_entity.right_leg.pivots.__getitem__(2).position.y < \
                model_entity.right_leg.pivots.__getitem__(3).position.y - 2:
            move_right_leg(motors, "foot", "forward")
        else:
            stop_moving_right_leg(motors, "foot")

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
        if simulate & (time % 10 == 0):
            model_entity.right_leg.relative_values.calculate_angles(
                model_entity.pivots.__getitem__(0).position,
                model_entity.right_leg.pivots.__getitem__(0).position,
                model_entity.right_leg.pivots.__getitem__(1).position,
                model_entity.right_leg.pivots.__getitem__(2).position,
                model_entity.right_leg.pivots.__getitem__(3).position)
            model_entity.left_leg.relative_values.calculate_angles(
                model_entity.pivots.__getitem__(0).position,
                model_entity.left_leg.pivots.__getitem__(0).position,
                model_entity.left_leg.pivots.__getitem__(1).position,
                model_entity.left_leg.pivots.__getitem__(2).position,
                model_entity.left_leg.pivots.__getitem__(3).position)

            self.right_leg_status.update(model_entity, model_entity.right_leg)
            self.left_leg_status.update(model_entity, model_entity.left_leg)
            self.feet_stabilize(model_entity, motors)

            if self.current_phase_left == 1:
                self.lift_leg(model_entity.left_leg, motors, True)

            if self.current_phase_left == 2:
                self.straight_leg(model_entity.left_leg, motors, True, model_entity.right_leg)

            if self.current_phase_left == 3:
                self.align_legs(model_entity, motors, model_entity.right_leg, model_entity.left_leg)
            elif self.current_phase_left == 4:
                stop_moving_left_leg(motors, 'thigh')
                stop_moving_right_leg(motors, 'thigh')
                stop_moving_left_leg(motors, "cale")
                stop_moving_right_leg(motors, 'cale')



            model_entity.right_leg.relative_values.show(1)

            self.left_leg_status.show_leg_status()
            print("---------------------------------------------------------------------------------")
            model_entity.left_leg.relative_values.show(2)
            self.left_leg_status.show_leg_status()
            print("---------------------------------------------------------------------------------")

            # if self.model_entity.pivots.__getitem__(0).position.x < self.model_entity.right_leg.pivots.__getitem__(
            #         2).position.x:
            #     motors.__getitem__(2).rate = constants.ROTATION_RATE
            # else:
            #     motors.__getitem__(2).rate = 0

        pass

    # def straight_leg(self, model_entity: Model, leg_number):

    #         motors = [right_thigh_motor, right_cale_motor,
    #                   right_foot_motor, left_thigh_motor, left_cale_motor, left_foot_motor]
    def straight_leg(self, leg: Leg, motors: list[SimpleMotor], run: bool, other_leg: Leg):
        if leg.name == "right":
            if run:
                stop_moving_right_leg(motors, "thigh")
                if leg.relative_values.angle_cale < leg.relative_values.angle_thigh:
                    move_right_leg(motors, "cale", "forward")
                else:
                    stop_moving_right_leg(motors, "cale")
            else:
                stop_moving_right_leg(motors, "cale")
        elif leg.name == "left":
            if run:
                stop_moving_left_leg(motors, "thigh")
                if leg.relative_values.angle_cale < leg.relative_values.angle_thigh - 0.2:
                    move_left_leg(motors, "cale", "forward")
                    if run & (-0.2 < other_leg.relative_values.angle_thigh):
                        move_right_leg(motors, "thigh", "backward")
                    else:
                        stop_moving_right_leg(motors, "thigh")
                else:
                    self.change_current_phase("left")
                    stop_moving_left_leg(motors, "cale")
                    stop_moving_right_leg(motors, "thigh")
            else:
                stop_moving_left_leg(motors, "cale")
                stop_moving_right_leg(motors, "thigh")

    def lift_leg(self, leg: Leg, motors: list[SimpleMotor], run: bool):
        if leg.name == "right":
            if run & (leg.relative_values.angle_thigh < 0.2):
                move_right_leg(motors, "thigh", "forward")
            else:
                self.change_current_phase("left")
                stop_moving_right_leg(motors, "thigh")
            if run & (-0.3 < leg.relative_values.angle_cale):
                move_right_leg(motors, "cale", "backward")
            else:
                stop_moving_right_leg(motors, "cale")
        elif leg.name == "left":
            if run & (leg.relative_values.angle_thigh < 0.2):
                move_left_leg(motors, "thigh", "forward")
            else:
                self.change_current_phase("left")
                stop_moving_left_leg(motors, "thigh")
            if run & (-0.3 < leg.relative_values.angle_cale):
                move_left_leg(motors, "cale", "backward")
            else:
                stop_moving_left_leg(motors, "cale")

    def change_current_phase(self, leg: str):
        if leg == "left":
            if self.current_phase_left <= 6:
                self.current_phase_left += 1
            elif self.current_phase_left == 6:
                self.current_phase_left = 0
            index = self.current_phase_left
            self.left_leg_status = self.walk_phases_leg_left.__getitem__(index)
        elif leg == "right":
            if self.current_phase_right <= 6:
                self.current_phase_right += 1
            elif self.current_phase_right == 6:
                self.current_phase_left = 0
            index = self.current_phase_right
            self.right_leg_status = self.walk_phases_leg_right.__getitem__(index)

    def align_legs(self, model_entity: Model, motors: list[SimpleMotor], right_leg: Leg, left_leg: Leg):
        if self.current_phase_left:
            if -0.1 < left_leg.relative_values.angle_thigh:
                move_left_leg(motors, "thigh", "backward")
            else:
                stop_moving_left_leg(motors, "thigh")
            self.lift_leg(right_leg, motors, True)


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

    walk_phases = [one, two, three, four, five, six]

    return walk_phases
