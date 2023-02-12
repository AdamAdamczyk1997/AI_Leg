from math import sin, sqrt
from enum import Enum
from numpy import pi, matrix
from pymunk import Vec2d, Body

from LegSimulation_v2.simulation_v2.constants import THIGH_HEIGHT, CALE_HEIGHT, CORPS_POSITION, CORPS_HEIGHT, FOOT_WIDTH

start_velocity_value = 0.5

class ChangeVelocitySignal(Enum):
    INCREASE_MAX = 0.1
    INCREASE = 0.05
    REDUCE = -0.05
    REDUCE_MAX = -0.1

class Velocity(float):
    thigh_velocity: list
    cale_velocity: list

    current_thigh_velocity_value: float
    current_cale_velocity_value: float

    def __init__(self, start_velocity: float):
        self.thigh_velocity = []
        self.cale_velocity = []
        self.current_thigh_velocity_value = 0.0
        self.current_cale_velocity_value = 0.0

        if start_velocity:
            self.fill_velocity(start_velocity)

    def update_current_velocity(self, thigh_velocity: float, cale_velocity: float):
        self.current_thigh_velocity_value = thigh_velocity
        self.current_cale_velocity_value = cale_velocity

    def append_thigh_velocity_record_to_the_list(self, phase: int, part: int, value: float):
        record = [phase, [part, value]]
        self.thigh_velocity.append(record)

    def change_velocity(self, which_phase: int, which_part_phase: int, leg_part: str, value: float):
        match leg_part:
            case "thigh":
                self.thigh_velocity[which_phase][which_part_phase] += value
            case "cale":
                self.cale_velocity[which_phase][which_part_phase] += value


    def fill_velocity(self, velocity: float):
        for i in range(0, 7):
            record_part = []
            for j in range(2):
                record_part.append(velocity)
            self.thigh_velocity.append(record_part)
            self.cale_velocity.append(record_part)

    def show_velocity_lists(self):
        print("thigh velocity list= ", self.thigh_velocity)
        print("cale velocity list= ", self.cale_velocity)


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

    def __init__(self):
        self.phase_part_usage_counters = []
        self.phase_0_usage = 0
        self.phase_1_usage = 0
        self.phase_2_usage = 0
        self.phase_3_usage = 0
        self.phase_4_usage = 0
        self.phase_5_usage = 0
        self.phase_6_usage = 0
        self.phase_usage_counters = []

    def append_phase_part_usage_counters(self, phase_part_usage: [int, int]):
        self.phase_part_usage_counters.append(phase_part_usage)

    def append_phase_usage_counter(self):
        self.phase_usage_counters.append([self.phase_1_usage, self.phase_2_usage, self.phase_3_usage,
                                          self.phase_4_usage, self.phase_5_usage, self.phase_6_usage])

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

    def show_counters(self):
        print("phase_part_usage_counters=", self.phase_part_usage_counters,
              "\nphase_0_usage=", self.phase_0_usage,
              "\nphase_1_usage=", self.phase_1_usage,
              "\nphase_2_usage=", self.phase_2_usage,
              "\nphase_3_usage=", self.phase_3_usage,
              "\nphase_4_usage=", self.phase_4_usage,
              "\nphase_5_usage=", self.phase_5_usage,
              "\nphase_6_usage=", self.phase_6_usage,
              "\nphase_usage_counters=", self.phase_usage_counters)


class RelativeValues:
    # TODO: if not precise enough change to double
    velocities: Velocity
    new_velocities: Velocity
    counters: list[Counters]

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

    knee_velocity: float
    hip_velocity: float
    ankle_velocity: float

    def __init__(self):
        self.velocities = Velocity(start_velocity_value)
        self.counters = [Counters()]
        self.phase_part_usage_counter = 0
        self.phase_part_usage_counter = 0
        self.phase_usage_counter = 0
        self.oscillation = 0.0
        self.x_hip = 0.0
        self.y_hip = 0.0
        self.angle_thigh = 0.0
        self.x_knee = 0.0
        self.y_knee = 0.0
        self.angle_cale = 0.0
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
                               self.x_knee, self.y_knee, self.angle_cale, self.x_ankle, self.y_ankle, self.x_foot,
                               self.y_foot, self.angle_foot, self.oscillation, self.hip_velocity, self.knee_velocity,
                               self.ankle_velocity, self.velocities.current_thigh_velocity_value,
                               self.velocities.current_cale_velocity_value]
        self.histories = [self.history_record]

    def calculate_angles(self, real_hips_position: Vec2d, real_knee_position: Vec2d, real_ankle_position: Vec2d,
                         real_center_foot_position: Vec2d):
        # calculate angles for right leg
        self.x_hip = 0.0
        self.y_hip = 0.0
        self.angle_thigh = 0.0
        self.x_knee = 0.0
        self.y_knee = 0.0
        self.angle_cale = 0.0
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

        self.x_foot = real_center_foot_position.x - real_hips_position.x
        self.y_foot = real_center_foot_position.y - real_hips_position.y
        sin_angle_foot = self.y_foot / (0.75 * FOOT_WIDTH)
        self.angle_foot = sin(sin_angle_foot)

        self.history_record = [self.usage_counter, int(self.x_hip), int(self.y_hip), round(self.angle_thigh, 2),
                               int(self.x_knee), int(self.y_knee), round(self.angle_cale, 2), int(self.x_ankle),
                               int(self.y_ankle), int(self.x_foot),
                               int(self.y_foot), round(self.angle_foot, 2), self.oscillation, self.hip_velocity,
                               self.knee_velocity, self.ankle_velocity,
                               self.velocities.current_thigh_velocity_value,
                               self.velocities.current_cale_velocity_value]

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
              ",", "{:.2f}".format(round(self.angle_cale, 2)), "), ankle=(", int(self.x_ankle), ",", int(self.y_ankle),
              ", angle_foot", ")")

    def change_oscillation(self, phase_nr: int):
        pi_value = pi
        value = phase_nr * (2 * pi_value / 6)
        self.oscillation = value
        pass

    # TODO: move method to controller and separate to thigh and cale values
    # def compare_phase_time(self, loop: int, which_phase: int,  leg_part: str):
    #     thigh_usage = self.counters[loop].phase_part_usage_counters[which_phase][0]
    #     cale_usage = self.counters[loop].phase_part_usage_counters[which_phase][1]
    #     total = thigh_usage + cale_usage
    #     average = total / 2
    #     value_to_be_increased = []
    #     value_to_be_reduce = []
    #     if thigh_usage - 2 > cale_usage:
    #         value_to_be_increased = cale_usage
    #         value_to_be_reduce = thigh_usage
    #     elif cale_usage - 2 > thigh_usage:
    #         value_to_be_increased = thigh_usage
    #         value_to_be_reduce = cale_usage
    #
    #     if value_to_be_reduce - value_to_be_increased > 40:
    #         return self.velocities.change_velocity(which_phase, )ChangeVelocitySignal.INCREASE_MAX
    #     elif average > 40:
    #         return ChangeVelocitySignal.INCREASE

