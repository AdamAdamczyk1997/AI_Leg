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
    real_angular_velocity = angular_knee_velocity + angular_thigh_velocity
    str_equation_for_second_angle = str(real_angular_velocity) + " * t + " + str(start_angle)

    return [str_equation_for_second_angle, real_angular_velocity, start_angle]

# def angular_velocity(t_q_1: float, t_q_2: float, c_q_1: float, c_q_2: float):
#     # Załóżmy, że x1 to numpy array reprezentujący szybkość kątową w różnych punktach czasowych
#     x1 = np.array([t_q_1, t_q_2])
#     # Obliczamy pochodną x1 po czasie za pomocą funkcji np.gradient, zakładając jednostkowy krok czasowy
#     dx1_dt = np.gradient(x1)
#     print("pochodna po czasie uda: dx1/dt:", dx1_dt)
#     # Teraz obliczamy dx2/dt używając danej zależności liniowej
#     # Załóżmy, że x1 to numpy array reprezentujący szybkość kątową w różnych punktach czasowych
#     x2 = np.array([c_q_1, c_q_2])
#     # Obliczamy pochodną x1 po czasie za pomocą funkcji np.gradient, zakładając jednostkowy krok czasowy
#     dx2_dt = np.gradient(x2)
#     print("pochodna po czasie kolana: dx2/dt:", dx2_dt)
#
#     #  dx2_dt = a * dx1_dt
#     a = dx2_dt / dx1_dt
#
#     print("a:", a)


def fill_angles_list(leg_name: str):
    thigh_angles_list = THIGH_ANGLES_LIST[SCENARIO][leg_name]
    calf_angles_list = CALF_ANGLES_LIST[SCENARIO][leg_name]
    return [thigh_angles_list, calf_angles_list]


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
        print("thigh time list= ", self.thigh_time)
        print("calf time list= ", self.calf_time)


def fill_velocity_lists(thigh_velocities: float, calf_velocities: float, range_phase: int):
    thigh_velocity = []
    calf_velocity = []
    for i in range(0, range_phase):
        thigh_velocity.append(thigh_velocities)
        calf_velocity.append(calf_velocities)

    return [thigh_velocity, calf_velocity]


class Equations(str):
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
            # TODO: fix the different_velocities because it doesn't work good with it and replace with const or add
            #  another option
            # self.velocities.append(Velocity(velocities[i][0], velocities[i][1]))
            self.velocities.append(Velocity(constant_velocities[0], constant_velocities[1]))

    def get_angle(self, leg_part: str, phase: int):
        match leg_part:
            case "thigh":
                return self.thigh_angles_list[phase]
            case "calf":
                return self.calf_angles_list[phase]

    def show_angles_lists(self):
        print("thigh angles list= ", self.thigh_angles_list)
        print("calf angles list= ", self.calf_angles_list)

    def fill_equation_dictionary(self, dict_name: str, phase: int):
        q_for_thigh = [self.thigh_angles_list[phase - 1],
                       self.thigh_angles_list[phase]]
        q_for_calf = [self.calf_angles_list[phase - 1],
                      self.calf_angles_list[phase]]

        thigh_equation = generate_hip_equation(q_for_thigh[0], q_for_thigh[1])
        calf_equation = generate_knee_equation(q_for_calf[0], q_for_calf[1], thigh_equation[1])

        # angular_velocity(q_for_thigh[0], q_for_thigh[1], q_for_calf[0], q_for_calf[1])

        assumed_thigh_angle_stop = round(thigh_equation[1] + thigh_equation[2], 3)
        assumed_calf_angle_stop = round(calf_equation[1] + calf_equation[2], 3)

        initial_velocity = [thigh_equation[1], calf_equation[1]]

        dictionary = dict(name=dict_name, thigh_equation=thigh_equation[0], calf_equation=calf_equation[0],
                          time=phase, assumed_thigh_angle_stop=assumed_thigh_angle_stop,
                          assumed_calf_angle_stop=assumed_calf_angle_stop,
                          thigh_initial_velocity=abs(round(initial_velocity[0], 2)),
                          calf_initial_velocity=abs(round(initial_velocity[1], 2)))

        return dictionary

    def fill_dictionaries(self):
        thigh_velocity = [START_VELOCITY_VALUE]
        calf_velocity = [START_VELOCITY_VALUE]
        for i in range(1, AMOUNT_PHASES + 1):
            dictionary_per_phase = self.fill_equation_dictionary("phase_equation_" + str(i), i)
            self.list_of_equations_dictionaries.append(dictionary_per_phase)
            different_velocities = fill_velocity_lists(dictionary_per_phase['thigh_initial_velocity'],
                                                       dictionary_per_phase['calf_initial_velocity'], 1)
            thigh_velocity.append(different_velocities[0][0])
            calf_velocity.append(different_velocities[1][0])
            i += 1

        return [thigh_velocity, calf_velocity]