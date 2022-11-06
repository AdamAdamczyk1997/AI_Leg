from ctypes import Union

import pymunk
from pymunk import SimpleMotor

from LegSimulation_v2.simulation_v2 import constants
from LegSimulation_v2.simulation_v2.Leg import Leg
from LegSimulation_v2.simulation_v2.Model import Model


class LegStatus:
    is_standing_on_the_ground: bool
    is_leading: bool
    is_lifting: bool
    is_straightening: bool
    is_straight: bool
    phase: int

    def __init__(self, model_entity: Model, leg: Leg):
        self.update(model_entity, leg)
        self.is_leading = False
        self.is_lifting = False
        self.is_straight = True
        self.phase = 0

    def update(self, model_entity: Model, leg: Leg):
        self.is_straight = False if (leg.relative_values.angle_thigh - leg.relative_values.angle_cale) > 0.05 else True
        if len(leg.relative_values.histories) > 2:
            self.check_leader(model_entity, leg)
            self.check_is_lifting(leg)

    def check_leader(self, model_entity: Model, leg: Leg):
        lead = model_entity.right_leg.name if model_entity.right_leg.foot.body.position.x > model_entity.left_leg.foot.body.position.x else model_entity.left_leg.name
        self.is_leading = True if leg.name == lead else False

    def check_is_lifting(self, leg: Leg):
        current_status = leg.relative_values.histories[-1][5]
        previous_status = leg.relative_values.histories[-2][5]
        self.is_lifting = True if current_status > previous_status else False

    def check_is_straightening(self, leg: Leg):
        current_difference_angle = leg.relative_values.angle_thigh - leg.relative_values.angle_cale
        previous_difference_angle = leg.relative_values.histories[-2][3] - leg.relative_values.histories[-2][6]
        self.is_straightening = True if current_difference_angle > previous_difference_angle else False


class Controller:
    run_flag: bool
    right_leg_status: LegStatus
    left_leg_status: LegStatus
    walk_phases: list
    current_phase: int

    def __init__(self, model_entity: Model):
        self.run_flag = True
        self.right_leg_status = LegStatus(model_entity, model_entity.right_leg)
        self.left_leg_status = LegStatus(model_entity, model_entity.left_leg)

    def feet_stabilize(self, model_entity: Model, motors: list[SimpleMotor]):
        if model_entity.right_leg.pivots.__getitem__(
                2).position.y >= model_entity.right_leg.pivots.__getitem__(3).position.y + 2:
            motors.__getitem__(2).rate = -constants.ROTATION_RATE
        elif model_entity.right_leg.pivots.__getitem__(
                2).position.y < model_entity.right_leg.pivots.__getitem__(3).position.y - 2:
            motors.__getitem__(2).rate = constants.ROTATION_RATE

        if model_entity.left_leg.pivots.__getitem__(2).position.y > model_entity.left_leg.pivots.__getitem__(
                3).position.y + 2:
            motors.__getitem__(5).rate = -constants.ROTATION_RATE
        elif model_entity.left_leg.pivots.__getitem__(
                2).position.y < model_entity.left_leg.pivots.__getitem__(3).position.y - 2:
            motors.__getitem__(5).rate = constants.ROTATION_RATE

        pass

    def feet_lifter(self, model_entity: Model, motors: list[SimpleMotor], leg_number, run):
        if run:
            leg_right = 0
            if leg_number == 1:
                leg_right = self.get_leg(model_entity, leg_number)
                leg_left = self.get_leg(model_entity, leg_number + 1)
            elif leg_number == 2:
                leg_left = self.get_leg(model_entity, leg_number)
                leg_right = self.get_leg(model_entity, leg_number - 1)
            else:
                pass

            if leg_right == model_entity.right_leg:
                if leg_right.relative_values.y_ankle < \
                        (model_entity.left_leg.relative_values.y_ankle + ((1 / 3) * constants.CALE_HEIGHT)):
                    if -0.3 < model_entity.left_leg.relative_values.angle_thigh < 0.3:
                        motors.__getitem__(3).rate = constants.ROTATION_RATE
                    else:
                        motors.__getitem__(3).rate = 0

                    if (model_entity.left_leg.relative_values.angle_thigh > 0.0) & \
                            (
                                    -0.3 < model_entity.left_leg.relative_values.angle_cale < model_entity.left_leg.relative_values.angle_thigh):
                        motors.__getitem__(4).rate = -constants.ROTATION_RATE
                    else:
                        motors.__getitem__(4).rate = 0
        else:
            motors.__getitem__(3).rate = 0
            motors.__getitem__(4).rate = 0
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

            run = True
            self.feet_lifter(model_entity, motors, 1, run)

            # if self.model_entity.pivots.__getitem__(0).position.x < self.model_entity.right_leg.pivots.__getitem__(
            #         2).position.x:
            #     motors.__getitem__(2).rate = constants.ROTATION_RATE
            # else:
            #     motors.__getitem__(2).rate = 0

        pass

    def get_leg(self, model_entity: Model, leg_number):
        leg = model_entity.right_leg if leg_number == 1 else model_entity.left_leg

        return leg

    # def thigh_move(self, leg: Union[Leg, int], turn):
    #
    #     pass
    #
    # def cale_move(self, leg: Union[Leg, int], turn):
    #     pass
    #
    # def foot_move(self, leg: Union[Leg, int], turn):
    #     pass
