import math
from math import sqrt

from numpy import pi
from pymunk import Vec2d, Body

from Bipedipulator_simulation.constants import THIGH_HEIGHT, CALF_HEIGHT, CORPS_POSITION, CORPS_HEIGHT, \
    AMOUNT_PHASES


class Counters:
    phase_usage_list: list[int]

    def __init__(self):
        self.phase_usage_list = []
        for i in range(0, AMOUNT_PHASES + 1):
            self.phase_usage_list.append(0)

    def phases_usage_increment(self, phase: int, not_count: bool):
        if not not_count:
            self.phase_usage_list[phase] += 1

    def show_counters(self):
        print("phase_usage_list=", self.phase_usage_list)


class RelativeValues:
    counters: Counters
    hip: dict[str, float]
    knee: dict[str, float]
    ankle: dict[str, float]

    usage_counter: int
    histories: list
    oscillation: float

    hip_velocity: float
    knee_velocity: float
    ankle_velocity: float

    def __init__(self):
        self.counters = Counters()
        self.hip = dict(x_hip=0.0, y_hip=0.0, angle_thigh=0.0, hip_velocity=0.0)
        self.knee = dict(x_knee=0.0, y_knee=0.0, angle_calf=0.0, knee_velocity=0.0)
        self.ankle = dict(x_ankle=0.0, y_ankle=0.0, ankle_velocity=0.0)

        self.usage_counter = 1
        self.history_record = []
        self.histories = []

    def calculate_angles(self, real_hips_position: Vec2d, real_knee_position: Vec2d, real_ankle_position: Vec2d):
        # calculate angles for leg
        self.hip['x_hip'] = 0.0
        self.hip['y_hip'] = real_hips_position.y - (CORPS_POSITION.y - ((1 / 2) * CORPS_HEIGHT))

        self.knee['x_knee'] = real_knee_position.x - real_hips_position.x
        self.knee['y_knee'] = real_knee_position.y - real_hips_position.y

        sin_angle_thigh = self.knee['x_knee'] / THIGH_HEIGHT
        angle_thigh_rad = math.asin(sin_angle_thigh)
        angle_thigh_deg = math.degrees(angle_thigh_rad)
        self.hip['angle_thigh'] = angle_thigh_rad  # hip angle values are in radians at now

        self.ankle['x_ankle'] = real_ankle_position.x - real_hips_position.x
        self.ankle['y_ankle'] = real_ankle_position.y - real_hips_position.y

        sin_angle_calf = (self.ankle['x_ankle'] - self.knee['x_knee']) / CALF_HEIGHT
        angle_calf_rad = math.asin(sin_angle_calf)
        angle_calf_deg = math.degrees(angle_calf_rad)
        self.knee['angle_calf'] = angle_calf_rad

        self.history_record = [self.usage_counter, int(self.hip['x_hip']), int(self.hip['y_hip']),
                               round(self.hip['angle_thigh'], 2),
                               int(self.knee['x_knee']), int(self.knee['y_knee']), round(self.knee['angle_calf'], 2),
                               int(self.ankle['x_ankle']),
                               int(self.ankle['y_ankle']), self.hip_velocity,
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

