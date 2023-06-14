from __future__ import annotations

from Bipedipulator_simulation.constants import THIGH_ANGLES_LIST, CALF_ANGLES_LIST, \
    START_VELOCITY_VALUE, AMOUNT_SCENARIOS, AMOUNT_PHASES, SCENARIO
import numpy as np


# TODO: need to reconsider this
def generate_hip_equation(q_1: float, q_2: float):
    start_angle = round(q_1, 3)
    angular_thigh_velocity = round((q_2 - q_1), 3)
    str_equation_for_second_angle = str(angular_thigh_velocity) + " * t + " + str(start_angle)

    return [str_equation_for_second_angle, angular_thigh_velocity, start_angle]


def generate_knee_equation(q_1: float, q_2: float, angular_thigh_velocity: float):
    start_angle = round(q_1, 3)
    angular_knee_velocity = round((q_2 - q_1), 3)
    real_angular_velocity = round(angular_knee_velocity + angular_thigh_velocity, 3)
    str_equation_for_second_angle = str(real_angular_velocity) + " * t + " + str(start_angle)

    return [str_equation_for_second_angle, real_angular_velocity, start_angle]


def calculate_speeds(thigh_angle, calf_angle, other_thigh_ang, other_calf_ang):
    angles = [thigh_angle, calf_angle, other_thigh_ang, other_calf_ang]
    # TODO: need to be changed or angles values are sometimes bad
    # thigh_angular_velocity = round(START_VELOCITY_VALUE * (thigh_angle / max_angle), 2)
    # calf_angular_velocity = round(START_VELOCITY_VALUE * (calf_angle / max_angle), 2)

    min_velocity = 0.1
    max_velocity = 0.3
    min_angle = min(angles)
    max_angle = max(angles)

    velocities = []
    for angle in angles:
        if angle == min_angle:
            velocities.append(min_velocity)
        elif angle == max_angle:
            velocities.append(max_velocity)
        else:
            scale = (angle - min_angle) / (max_angle - min_angle)
            velocities.append(min_velocity + scale * (max_velocity - min_velocity))

    return [velocities[0], velocities[1]]


def fill_angles_list(leg_name: str):
    thigh_angles_list = THIGH_ANGLES_LIST[SCENARIO][leg_name]
    calf_angles_list = CALF_ANGLES_LIST[SCENARIO][leg_name]
    return [thigh_angles_list, calf_angles_list]


def get_other_leg_angles(leg_name: str):
    other_leg = switch_direction(leg_name)
    other_thigh_angles_list = THIGH_ANGLES_LIST[SCENARIO][other_leg]
    other_calf_angles_list = CALF_ANGLES_LIST[SCENARIO][other_leg]

    return [other_thigh_angles_list, other_calf_angles_list]


def switch_direction(direction):
    return 'right' if direction == 'left' else 'left'


class Velocity:
    thigh_velocity: list
    calf_velocity: list

    thigh_time: list
    calf_time: list

    current_thigh_velocity_value: float
    current_calf_velocity_value: float

    histories: list

    def __init__(self, thigh_velocity: list, calf_velocity: list):
        self.thigh_velocity = []
        self.calf_velocity = []
        self.current_thigh_velocity_value = 0.0
        self.current_calf_velocity_value = 0.0
        self.thigh_time = []
        self.calf_time = []

        self.thigh_velocity = thigh_velocity
        self.calf_velocity = calf_velocity
        self.fill_time_list()
        self.histories = [[self.current_thigh_velocity_value, self.current_calf_velocity_value]]
        self.show_velocity_lists()

    def update_current_velocity(self, thigh_velocity: float, calf_velocity: float, phase: int):
        history_record = [self.current_thigh_velocity_value, self.current_calf_velocity_value]
        self.histories.append(history_record)

        self.current_thigh_velocity_value = thigh_velocity
        if not thigh_velocity == 0.0:
            self.increment_leg_part_time_usage("thigh", phase)
        self.current_calf_velocity_value = calf_velocity
        if not calf_velocity == 0.0:
            self.increment_leg_part_time_usage("calf", phase)

    def fill_velocity(self, thigh_velocity: list, calf_velocity: list):
        self.thigh_velocity = thigh_velocity
        self.calf_velocity = calf_velocity

    def fill_time_list(self):
        for i in range(0, AMOUNT_PHASES + 1):
            self.thigh_time.append(0)
            self.calf_time.append(0)

    def increment_leg_part_time_usage(self, body_part: str, phase: int):
        match body_part:
            case "thigh":
                self.thigh_time[phase] += 1
            case "calf":
                self.calf_time[phase] += 1

    def show_velocity_lists(self):
        print("thigh velocity list= ", self.thigh_velocity)
        print("calf velocity list= ", self.calf_velocity)


def fill_velocity_lists(thigh_velocities: float, calf_velocities: float, range_phase: int):
    thigh_velocity = []
    calf_velocity = []
    for i in range(0, range_phase):
        thigh_velocity.append(thigh_velocities)
        calf_velocity.append(calf_velocities)

    return [thigh_velocity, calf_velocity]


class Equations(str):
    # TODO remember że ruch 1_1 ma dziwne wyprostowanie łydki w którymś momencie jest to spowodowane że nie mamy stopy ruchomej
    leg_name: str

    thigh_angles_list: list[float]
    calf_angles_list: list[float]

    list_of_equations_dictionaries: list[dict]
    velocities: list[Velocity]

    def __init__(self, leg_name: str):
        self.leg_name = leg_name
        self.list_of_equations_dictionaries = []

        angles = fill_angles_list(leg_name)
        self.thigh_angles_list = angles[0]
        self.calf_angles_list = angles[1]

        constant_velocities = fill_velocity_lists(START_VELOCITY_VALUE, START_VELOCITY_VALUE, AMOUNT_PHASES + 1)
        different_velocities = self.fill_dictionaries()
        self.velocities = [Velocity([START_VELOCITY_VALUE], [START_VELOCITY_VALUE])]

        velocities = [constant_velocities, different_velocities]

        for i in range(0, AMOUNT_SCENARIOS):
            self.velocities.append(Velocity(velocities[i][0], velocities[i][1]))
            print(f"velocities: {velocities[i]}")

    def get_angle(self, leg_part: str, phase: int):
        match leg_part:
            case "thigh":
                return self.thigh_angles_list[phase]
            case "calf":
                return self.calf_angles_list[phase]

    def show_angles_lists(self):
        print("thigh angles list= ", self.thigh_angles_list)
        print("calf angles list= ", self.calf_angles_list)

    def fill_equation_dictionary(self, dict_name: str, phase: int, other_leg_angles: list):
        q_for_thigh = [self.thigh_angles_list[phase - 1],
                       self.thigh_angles_list[phase]]
        q_for_calf = [self.calf_angles_list[phase - 1],
                      self.calf_angles_list[phase]]

        q_for_other_thigh = abs(other_leg_angles[0][phase - 1] -
                                other_leg_angles[0][phase])
        q_for_other_calf = abs(other_leg_angles[1][phase - 1] -
                               other_leg_angles[1][phase])

        thigh_equation = generate_hip_equation(q_for_thigh[0], q_for_thigh[1])
        calf_equation = generate_knee_equation(q_for_calf[0], q_for_calf[1], thigh_equation[1])

        initial_velocity = calculate_speeds(abs(q_for_thigh[0] - q_for_thigh[1]), abs(q_for_calf[0] - q_for_calf[1]),
                                            q_for_other_thigh, q_for_other_calf)

        assumed_thigh_angle_stop = round(thigh_equation[1] + thigh_equation[2], 3)
        assumed_calf_angle_stop = round(calf_equation[1] + calf_equation[2], 3)

        dictionary = dict(name=dict_name, thigh_equation=thigh_equation[0], calf_equation=calf_equation[0],
                          assumed_thigh_angle_stop=assumed_thigh_angle_stop,
                          assumed_calf_angle_stop=assumed_calf_angle_stop,
                          thigh_initial_velocity=abs(round(initial_velocity[0], 2)),
                          calf_initial_velocity=abs(round(initial_velocity[1], 2)))

        return dictionary

    def fill_dictionaries(self):
        other_leg_angles = get_other_leg_angles(self.leg_name)
        thigh_velocity = [START_VELOCITY_VALUE]
        calf_velocity = [START_VELOCITY_VALUE]
        for i in range(1, AMOUNT_PHASES + 1):
            dictionary_per_phase = self.fill_equation_dictionary("phase_equation_" + str(i), i, other_leg_angles)
            self.list_of_equations_dictionaries.append(dictionary_per_phase)
            thigh_velocity.append(dictionary_per_phase['thigh_initial_velocity'])
            calf_velocity.append(dictionary_per_phase['calf_initial_velocity'])

        return [thigh_velocity, calf_velocity]
