from math import sin, cos

from numpy import double
from pymunk import Vec2d

from LegSimulation_v2.simulation_v2.constants import THIGH_HEIGHT, CALE_HEIGHT


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
    angle_foot: float

    usage_counter: int
    histories: list

    def __init__(self):
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
        self.angle_foot = 0.0
        self.usage_counter = 1
        self.histories = [[self.usage_counter, self.x_hip, self.y_hip, self.angle_thigh,
                           self.x_knee, self.y_knee, self.angle_cale,
                           self.x_toe, self.y_toe, self.x_heel, self.y_heel, self.angle_foot]]

    def calculate_angles(self, real_hips_position: Vec2d, real_knee_position: Vec2d, real_ankle_position: Vec2d,
                         real_toe_position: Vec2d, real_heel_position: Vec2d):
        # calculate angles for right leg
        self.x_hip = 0
        self.y_hip = real_hips_position.y - 375

        # knee position relative to the hip
        self.x_knee = real_knee_position.x - real_hips_position.x
        # angle between corps and thigh
        sin_ankle_thigh = self.x_knee / THIGH_HEIGHT
        self.angle_thigh = sin(sin_ankle_thigh)
        self.y_knee = real_knee_position.y - real_hips_position.y

        # ankle position relative to the hip
        self.x_ankle = real_ankle_position.x - real_hips_position.x
        # angle between corps and cale
        sin_ankle_cale = (self.x_ankle - self.x_knee) / CALE_HEIGHT
        self.angle_cale = sin(sin_ankle_cale)
        self.y_ankle = real_ankle_position.y - real_hips_position.y

        self.x_toe = real_toe_position.x - real_hips_position.x
        self.y_toe = real_toe_position.y - real_hips_position.y
        self.x_heel = real_heel_position.x - real_hips_position.x
        self.y_heel = real_heel_position.y - real_hips_position.y

        self.histories.append(
            [self.usage_counter, int(self.x_hip), int(self.y_hip), round(self.angle_thigh, 2),
             int(self.x_knee), int(self.y_knee), round(self.angle_cale, 2),
             int(self.x_toe), int(self.y_toe), int(self.x_heel), int(self.y_heel), self.angle_foot])
        self.usage_counter += 1

        pass

    def show(self, leg_number: int):
        print(leg_number, ": hip=(", int(self.x_hip), ",", int(self.y_hip), ",",
              "{:.2f}".format(round(self.angle_thigh, 2)),
              "), knee=(", int(self.x_knee), ",", int(self.y_knee), ",", "{:.2f}".format(round(self.angle_cale, 2)),
              "), ankle=(", int(self.x_ankle), ",", int(self.y_ankle), ", angle_foot",
              "), toe=(", int(self.x_toe), ",", int(self.y_toe), "), heel=(", int(self.x_heel), ",", int(self.y_heel),
              ")")

        print(self.histories[-1])
        print("---------------------------------------------------------------------------------")
