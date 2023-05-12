from math import sin, sqrt

from numpy import pi
from pymunk import Vec2d, Body

from LegSimulation_v2.Bipedipulator_simulation.constants import THIGH_HEIGHT, CALF_HEIGHT, CORPS_POSITION, CORPS_HEIGHT, \
    FOOT_WIDTH


class Counters:
    phase_usage_list: list[int]

    def __init__(self):
        self.phase_usage_list = []
        for i in range(0, 13):
            self.phase_usage_list.append(0)

    def phase_part_usage_increment(self, phase: int, not_count: bool):
        if not not_count:
            self.phase_usage_list[phase] += 1

    def show_counters(self):
        print("phase_usage_list=", self.phase_usage_list)


class RelativeValues:
    counters: Counters

    x_hip: float
    y_hip: float
    x_knee: float
    y_knee: float
    angle_thigh: float
    x_ankle: float
    y_ankle: float
    angle_calf: float

    usage_counter: int
    histories: list
    oscillation: float

    hip_velocity: float
    knee_velocity: float
    ankle_velocity: float

    def __init__(self):
        self.counters = Counters()
        self.phase_part_usage_counter = 0
        self.phase_usage_counter = 0
        self.oscillation = 0.0
        self.x_hip = 0.0
        self.y_hip = 0.0
        self.angle_thigh = 0.0
        self.x_knee = 0.0
        self.y_knee = 0.0
        self.angle_calf = 0.0
        self.x_ankle = 0.0
        self.y_ankle = 0.0

        self.knee_velocity = 0.0
        self.hip_velocity = 0.0
        self.ankle_velocity = 0.0

        self.usage_counter = 1
        self.history_record = []
        self.histories = []

    def calculate_angles(self, real_hips_position: Vec2d, real_knee_position: Vec2d, real_ankle_position: Vec2d):
        # calculate angles for leg
        self.x_hip = 0.0
        self.y_hip = 0.0
        self.angle_thigh = 0.0
        self.x_knee = 0.0
        self.y_knee = 0.0
        self.angle_calf = 0.0
        self.y_hip = real_hips_position.y - (CORPS_POSITION.y - ((1 / 2) * CORPS_HEIGHT))

        # knee position relative to the hip
        self.x_knee = real_knee_position.x - real_hips_position.x
        # angle between corps and thigh
        sin_angle_thigh = self.x_knee / THIGH_HEIGHT
        self.angle_thigh = sin(sin_angle_thigh)
        self.y_knee = real_knee_position.y - real_hips_position.y

        # ankle position relative to the hip
        self.x_ankle = real_ankle_position.x - real_hips_position.x
        # angle between corps and calf
        sin_angle_calf = (self.x_ankle - self.x_knee) / CALF_HEIGHT
        self.angle_calf = sin(sin_angle_calf)
        self.y_ankle = real_ankle_position.y - real_hips_position.y

        self.history_record = [self.usage_counter, int(self.x_hip), int(self.y_hip), round(self.angle_thigh, 2),
                               int(self.x_knee), int(self.y_knee), round(self.angle_calf, 2), int(self.x_ankle),
                               int(self.y_ankle), self.oscillation, self.hip_velocity,
                               self.knee_velocity, self.ankle_velocity]

        self.histories.append(self.history_record)

        self.usage_counter += 1

        pass

    def body_velocity(self, body: Body, body_part: str):
        velocity = round(sqrt(pow(body.velocity.x, 2) + pow(body.velocity.y, 2)), 2)
        match body_part:
            case "knee":
                self.knee_velocity = velocity
            case "hip":
                self.hip_velocity = velocity
            case "ankle":
                self.ankle_velocity = velocity
            case other:
                print("Unknown leg part", body_part)

    def change_oscillation(self, phase_nr: int):
        pi_value = pi
        value = phase_nr * (2 * pi_value / 6)
        self.oscillation = value
        pass

