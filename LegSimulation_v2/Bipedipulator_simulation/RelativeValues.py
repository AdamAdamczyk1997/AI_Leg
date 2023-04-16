from math import sin, sqrt

from numpy import pi
from pymunk import Vec2d, Body

from LegSimulation_v2.Bipedipulator_simulation.constants import THIGH_HEIGHT, CALF_HEIGHT, CORPS_POSITION, CORPS_HEIGHT, \
    FOOT_WIDTH


class Counters:
    phase_part_usage_counters: list
    phase_usage_counters: list
    phase_0_usage: int
    phase_1_usage: int
    phase_2_usage: int
    phase_3_usage: int
    phase_4_usage: int
    phase_5_usage: int
    phase_6_usage: int
    phase_7_usage: int
    phase_8_usage: int
    phase_9_usage: int
    phase_10_usage: int
    phase_11_usage: int
    phase_12_usage: int

    def __init__(self):
        self.phase_part_usage_counters = []
        self.phase_0_usage = 0
        self.phase_1_usage = 0
        self.phase_2_usage = 0
        self.phase_3_usage = 0
        self.phase_4_usage = 0
        self.phase_5_usage = 0
        self.phase_6_usage = 0
        self.phase_7_usage = 0
        self.phase_8_usage = 0
        self.phase_9_usage = 0
        self.phase_10_usage = 0
        self.phase_11_usage = 0
        self.phase_12_usage = 0
        self.phase_usage_counters = []

    def append_phase_part_usage_counters(self, phase_part_usage: int):
        self.phase_part_usage_counters.append(phase_part_usage)

    def append_phase_usage_counter(self):
        self.phase_usage_counters.append([self.phase_1_usage, self.phase_2_usage, self.phase_3_usage,
                                          self.phase_4_usage, self.phase_5_usage, self.phase_6_usage,
                                          self.phase_7_usage, self.phase_8_usage, self.phase_9_usage,
                                          self.phase_10_usage, self.phase_11_usage, self.phase_12_usage])

    def get_counter(self, phase):
        match phase:
            case 0:
                return self.phase_0_usage
            case 1:
                return self.phase_1_usage
            case 2:
                return self.phase_2_usage
            case 3:
                return self.phase_3_usage
            case 4:
                return self.phase_4_usage
            case 5:
                return self.phase_5_usage
            case 6:
                return self.phase_6_usage
            case 7:
                return self.phase_7_usage
            case 8:
                return self.phase_8_usage
            case 9:
                return self.phase_9_usage
            case 10:
                return self.phase_10_usage
            case 11:
                return self.phase_11_usage
            case 12:
                return self.phase_12_usage

    def phase_part_usage_increment(self, phase: int, not_count: bool):
        if not not_count:
            match phase:
                case 0:
                    self.phase_0_usage += 1
                case 1:
                    self.phase_1_usage += 1
                case 2:
                    self.phase_2_usage += 1
                case 3:
                    self.phase_3_usage += 1
                case 4:
                    self.phase_4_usage += 1
                case 5:
                    self.phase_5_usage += 1
                case 6:
                    self.phase_6_usage += 1
                case 7:
                    self.phase_7_usage += 1
                case 8:
                    self.phase_8_usage += 1
                case 9:
                    self.phase_9_usage += 1
                case 10:
                    self.phase_10_usage += 1
                case 11:
                    self.phase_11_usage += 1
                case 12:
                    self.phase_12_usage += 1

    def show_counters(self):
        print("phase_part_usage_counters=", self.phase_part_usage_counters,
              "\nphase_0_usage=", self.phase_0_usage,
              "\nphase_1_usage=", self.phase_1_usage,
              "\nphase_2_usage=", self.phase_2_usage,
              "\nphase_3_usage=", self.phase_3_usage,
              "\nphase_4_usage=", self.phase_4_usage,
              "\nphase_5_usage=", self.phase_5_usage,
              "\nphase_6_usage=", self.phase_6_usage,
              "\nphase_7_usage=", self.phase_7_usage,
              "\nphase_8_usage=", self.phase_8_usage,
              "\nphase_9_usage=", self.phase_9_usage,
              "\nphase_10_usage=", self.phase_10_usage,
              "\nphase_11_usage=", self.phase_11_usage,
              "\nphase_12_usage=", self.phase_12_usage,
              "\nphase_usage_counters=", self.phase_usage_counters)


class RelativeValues:
    # TODO: if not precise enough change to double
    counters: list[Counters]

    x_hip: float
    y_hip: float

    x_knee: float
    y_knee: float
    angle_thigh: float

    x_ankle: float
    y_ankle: float
    angle_calf: float

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

    knee_velocity: float
    hip_velocity: float
    ankle_velocity: float

    def __init__(self):
        self.counters = [Counters()]
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
        self.x_foot = 0.0
        self.y_foot = 0.0
        self.angle_foot = 0.0

        self.knee_velocity = 0.0
        self.hip_velocity = 0.0
        self.ankle_velocity = 0.0

        self.usage_counter = 1
        self.history_record = [self.usage_counter, self.x_hip, self.y_hip, self.angle_thigh,
                               self.x_knee, self.y_knee, self.angle_calf, self.x_ankle, self.y_ankle, self.x_foot,
                               self.y_foot, self.angle_foot, self.oscillation, self.hip_velocity, self.knee_velocity,
                               self.ankle_velocity]
        self.histories = [self.history_record]

    def calculate_angles(self, real_hips_position: Vec2d, real_knee_position: Vec2d, real_ankle_position: Vec2d):
        # calculate angles for right leg
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

        self.x_foot = 2 # TODO: do zmiany!
        self.y_foot = 2
        sin_angle_foot = self.y_foot / (0.75 * FOOT_WIDTH)
        self.angle_foot = sin(sin_angle_foot)

        self.history_record = [self.usage_counter, int(self.x_hip), int(self.y_hip), round(self.angle_thigh, 2),
                               int(self.x_knee), int(self.y_knee), round(self.angle_calf, 2), int(self.x_ankle),
                               int(self.y_ankle), int(self.x_foot),
                               int(self.y_foot), round(self.angle_foot, 2), self.oscillation, self.hip_velocity,
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

    def show(self, leg_number: int):
        leg = ""
        if leg_number == 1:
            leg = "right_leg"
        elif leg_number == 2:
            leg = "left_leg"
        print("leg:", leg, ", usage_counter:", self.usage_counter, ": hip=(", int(self.x_hip), ",", int(self.y_hip),
              ",", "{:.2f}".format(round(self.angle_thigh, 2)), "), knee=(", int(self.x_knee), ",", int(self.y_knee),
              ",", "{:.2f}".format(round(self.angle_calf, 2)), "), ankle=(", int(self.x_ankle), ",", int(self.y_ankle),
              ", angle_foot", ")")

    def change_oscillation(self, phase_nr: int):
        pi_value = pi
        value = phase_nr * (2 * pi_value / 6)
        self.oscillation = value
        pass

