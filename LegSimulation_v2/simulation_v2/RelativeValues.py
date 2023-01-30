from math import sin, cos

from numpy import double
from pymunk import Vec2d
import numpy as np
from numpy import pi

from LegSimulation_v2.simulation_v2.constants import THIGH_HEIGHT, CALE_HEIGHT, CORPS_POSITION, CORPS_HEIGHT, FOOT_WIDTH


class RelativeValues:
    # TODO: if not precise enough change to double
    x_hip: float
    y_hip: float

    x_knee: float
    y_knee: float
    angle_thigh: float

    x_ankle: float
    y_ankle: float
    angle_cale: float

    x_toe: float
    y_toe: float
    x_heel: float
    y_heel: float
    x_foot: float
    y_foot: float
    angle_foot: float

    usage_counter: int
    histories: list
    oscillation: float

    def __init__(self):
        self.oscillation = 0.0
        self.x_hip = 0.0
        self.y_hip = 0.0
        self.angle_thigh = 0.0
        self.x_knee = 0.0
        self.y_knee = 0.0
        self.angle_cale = 0.0
        self.x_ankle = 0.0
        self.y_ankle = 0.0
        self.x_toe = 0.0
        self.y_toe = 0.0
        self.x_heel = 0.0
        self.y_heel = 0.0
        self.x_foot = 0.0
        self.y_foot = 0.0
        self.angle_foot = 0.0
        self.usage_counter = 1
        self.history_record = [self.usage_counter, self.x_hip, self.y_hip, self.angle_thigh,
                               self.x_knee, self.y_knee, self.angle_cale, self.x_ankle, self.y_ankle,
                               self.x_toe, self.y_toe, self.x_heel, self.y_heel, self.x_foot, self.y_foot,
                               self.angle_foot, self.oscillation]
        self.histories = [self.history_record]

    def calculate_angles(self, real_hips_position: Vec2d, real_knee_position: Vec2d, real_ankle_position: Vec2d,
                         real_toe_position: Vec2d, real_heel_position: Vec2d, real_center_foot_position: Vec2d):
        # calculate angles for right leg
        self.x_hip = 0.0
        self.y_hip = real_hips_position.y - (CORPS_POSITION.y - ((1 / 2) * CORPS_HEIGHT))

        # knee position relative to the hip
        self.x_knee = real_knee_position.x - real_hips_position.x
        # angle between corps and thigh
        sin_ankle_thigh = self.x_knee / THIGH_HEIGHT
        self.angle_thigh = sin(sin_ankle_thigh)
        self.y_knee = real_knee_position.y - real_hips_position.y

        # ankle position relative to the hip
        self.x_ankle = real_ankle_position.x - real_hips_position.x
        # angle between corps and cale
        sin_angle_cale = (self.x_ankle - self.x_knee) / CALE_HEIGHT
        self.angle_cale = sin(sin_angle_cale)
        self.y_ankle = real_ankle_position.y - real_hips_position.y

        self.x_toe = real_toe_position.x - real_hips_position.x
        self.y_toe = real_toe_position.y - real_hips_position.y
        self.x_heel = real_heel_position.x - real_hips_position.x
        self.y_heel = real_heel_position.y - real_hips_position.y

        self.x_foot = real_center_foot_position.x - real_hips_position.x
        self.y_foot = real_center_foot_position.y - real_hips_position.y
        sin_angle_foot = (self.y_foot - self.y_toe) / (0.75 * FOOT_WIDTH)
        self.angle_foot = sin(sin_angle_foot)

        self.history_record = [self.usage_counter, int(self.x_hip), int(self.y_hip), round(self.angle_thigh, 2),
                               int(self.x_knee), int(self.y_knee), round(self.angle_cale, 2), int(self.x_ankle),
                               int(self.y_ankle),
                               int(self.x_toe), int(self.y_toe), int(self.x_heel), int(self.y_heel), int(self.x_foot),
                               int(self.y_foot), round(self.angle_foot, 2), self.oscillation]

        self.histories.append(self.history_record)

        self.usage_counter += 1

        pass

    def show(self, leg_number: int):
        leg = ""
        if leg_number == 1:
            leg = "right_leg"
        elif leg_number == 2:
            leg = "left_leg"
        print("leg:", leg, ", usage_counter:", self.usage_counter, ": hip=(", int(self.x_hip), ",", int(self.y_hip),
              ",",
              "{:.2f}".format(round(self.angle_thigh, 2)),
              "), knee=(", int(self.x_knee), ",", int(self.y_knee), ",", "{:.2f}".format(round(self.angle_cale, 2)),
              "), ankle=(", int(self.x_ankle), ",", int(self.y_ankle), ", angle_foot",
              "), toe=(", int(self.x_toe), ",", int(self.y_toe), "), heel=(", int(self.x_heel), ",", int(self.y_heel),
              ")")

    def change_oscillation(self, phase_nr: int):
        pi_value = pi
        value = phase_nr * (2 * pi_value/6)
        self.oscillation = value
        pass
