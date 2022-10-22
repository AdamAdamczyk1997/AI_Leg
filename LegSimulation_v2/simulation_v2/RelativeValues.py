from math import sin, cos

from numpy import double

from LegSimulation_v2.simulation_v2.constants import THIGH_HEIGHT, CALE_HEIGHT


class RelativeValues:
    # TODO: if not precise enough change to double
    x_knee: float
    y_knee: float
    angle_thigh: float

    x_ankle: float
    y_ankle: float
    angle_cale: float

    ankle_foot: float

    def __init__(self):
        self.x_knee = 0.0
        self.y_knee = 0.0
        self.angle_thigh = 0.0
        self.x_ankle = 0.0
        self.y_ankle = 0.0
        self.angle_cale = 0.0

    def calculate_angles(self, real_corps_position_x: float, real_knee_position_x: float, real_ankle_position_x: float):
        # calculate angles for right leg
        print(real_corps_position_x, real_knee_position_x, real_ankle_position_x)
        # knee position relative to the hip
        self.x_knee = real_knee_position_x - real_corps_position_x
        # ankle between corps and thigh
        sin_ankle_thigh = self.x_knee / THIGH_HEIGHT
        self.angle_thigh = sin(sin_ankle_thigh)
        self.y_knee = -THIGH_HEIGHT * cos(self.angle_thigh)

        # ankle position relative to the hip
        self.x_ankle = real_ankle_position_x - real_corps_position_x

        # ankle between corps and cale
        sin_ankle_cale = (self.x_ankle - self.x_knee) / CALE_HEIGHT
        self.angle_cale = sin(sin_ankle_cale)
        self.y_ankle = self.y_knee - (CALE_HEIGHT * cos(self.angle_cale))

        pass

    def show(self):
        print(" x_knee = ", self.x_knee, " y_knee = ", self.y_knee, "angle_thigh = ", self.angle_thigh)
        print(" x_ankle = ", self.x_ankle, " y_ankle = ", self.y_ankle, "angle_cale = ", self.angle_cale)


