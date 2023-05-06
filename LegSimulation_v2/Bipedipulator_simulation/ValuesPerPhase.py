from __future__ import annotations

from enum import Enum
from pymunk import vec2d, Vec2d

start_velocity_value = 0.25


class ChangeVelocitySignal(Enum):
    INCREASE_MAX = 0.1
    INCREASE = 0.05
    REDUCE = -0.05
    REDUCE_MAX = -0.1


def calculate_velocity_change_angle(time: float, velocity: float):
    # velocity is first derivative angle of time, example for Q=-0.6t + 1, velocity is -0.6
    velocity_change_angle = velocity / time
    return velocity_change_angle


def generate_equation(t_1: float, t_2: float, q_1: float, q_2: float):
    A = round(((q_2 - q_1) / (t_2 - t_1)), 3)
    B = round((q_1 - (A * t_1)), 3)
    equation = str(A) + " * t + " + str(B)

    return [equation, A, B]


def calculate_initial_velocity(q_for_first: list, q_for_second: list):
    distance_1 = abs(q_for_first[0] - q_for_first[1])
    distance_2 = abs(q_for_second[0] - q_for_second[1])
    if distance_1 < distance_2:
        velocity_2 = 0.25
        velocity_1 = round(distance_1 / (distance_2 / velocity_2), 2)
    elif distance_1 > distance_2:
        velocity_1 = 0.25
        velocity_2 = round(distance_2 / (distance_1 / velocity_1), 2)
    else:
        velocity_1 = 0.20
        velocity_2 = 0.20

    return [velocity_1, velocity_2]


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

        if thigh_velocity and calf_velocity:
            self.fill_velocity(thigh_velocity, calf_velocity)
            self.fill_time_list()
            self.histories = [[self.current_thigh_velocity_value, self.current_calf_velocity_value]]

    def update_current_velocity(self, thigh_velocity: float, calf_velocity: float, phase: int):
        history_record = [self.current_thigh_velocity_value, self.current_calf_velocity_value]
        self.histories.append(history_record)

        self.current_thigh_velocity_value = thigh_velocity
        if not thigh_velocity == 0.0:
            self.increment_leg_part_time_usage("thigh", phase)
        self.current_calf_velocity_value = calf_velocity
        if not calf_velocity == 0.0:
            self.increment_leg_part_time_usage("calf", phase)

    def change_velocity(self, which_phase: int, which_part_phase: int, leg_part: str, value: float):
        match leg_part:
            case "thigh":
                self.thigh_velocity[which_phase][which_part_phase] += value
            case "calf":
                self.calf_velocity[which_phase][which_part_phase] += value

    def fill_velocity(self, thigh_velocity: list, calf_velocity: list):
        # thigh velocity list=  [[0.25, 0.25], ... , [0.25, 0.25]]
        self.thigh_velocity = thigh_velocity
        self.calf_velocity = calf_velocity

    def fill_time_list(self):
        for i in range(0, 14):
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
        print("current_thigh_velocity_value = ", self.current_thigh_velocity_value)
        print("current_calf_velocity_value = ", self.current_calf_velocity_value)


class Equations(str):
    leg_name: str

    thigh_angles_list: list[float]
    calf_angles_list: list[float]

    current_angle_value_due_to_the_equation: float

    list_of_equations_dictionaries: list[dict]

    thigh_velocity: list[list]
    calf_velocity: list[list]

    velocities: list[Velocity]

    def __init__(self, leg_name: str):
        self.thigh_velocity = [[start_velocity_value], [], [], []]
        self.calf_velocity = [[start_velocity_value], [], [], []]
        self.leg_name = leg_name
        self.list_of_equations_dictionaries = []
        self.fill_velocity_list(start_velocity_value)
        # self.fill_angles_list_v1()
        self.fill_angles_list_v2()
        # self.fill_angles_list_v3()
        self.fill_dictionaries()
        self.velocities = [Velocity(self.thigh_velocity[0], self.calf_velocity[0]),
                           Velocity(self.thigh_velocity[1], self.calf_velocity[1]),
                           Velocity(self.thigh_velocity[2], self.calf_velocity[2]),
                           Velocity(self.thigh_velocity[3], self.calf_velocity[3])]
        # self.velocities.append(Velocity(self.thigh_velocity, self.calf_velocity))

    def fill_angles_list_v1(self):
        match self.leg_name:
            case "right":
                self.thigh_angles_list = [0.30, 0.25, 0.20, 0.15, 0.1,
                                          0.3, 0.38, 0.41, 0.48,
                                          0.55, 0.45, 0.375, 0.30]

                self.calf_angles_list = [-0.32, -0.35, -0.4, -0.45, -0.5,
                                         -0.55, -0.6, -0.55, -0.35,
                                         -0.25, -0.28, -0.3, -0.32]
            case "left":
                self.thigh_angles_list = [0.38, 0.41, 0.48, 0.55, 0.45,
                                          0.375, 0.30, 0.25, 0.20,
                                          0.15, 0.1, 0.3, 0.38]

                self.calf_angles_list = [-0.6, -0.55, -0.35, -0.25, -0.28,
                                         -0.3, -0.32, -0.35, -0.4,
                                         -0.45, -0.5, -0.55, -0.6]
            case other:
                print("Equation leg name not specified")

    def fill_angles_list_v2(self):
        match self.leg_name:
            case "right":
                self.thigh_angles_list = [0.452, 0.389, 0.276, 0.119, 0.049,
                                          0.361, 0.628, 0.696,
                                          0.605, 0.556, 0.488,
                                          0.470, 0.452]

                self.calf_angles_list = [-0.488, -0.531, -0.572, -0.589, -0.681,
                                         -0.724, -0.514, -0.159,
                                         -0.129, -0.285, -0.389,
                                         -0.443, -0.488]
            case "left":
                self.thigh_angles_list = [0.628, 0.696, 0.605, 0.556, 0.488,
                                          0.470, 0.452, 0.389,
                                          0.276, 0.119, 0.049,
                                          0.361, 0.628]

                self.calf_angles_list = [-0.514, -0.159, -0.129, -0.285, -0.389,
                                         -0.443, -0.488, -0.531,
                                         -0.572, -0.589, -0.681,
                                         -0.724, -0.514]
            case other:
                print("Equation leg name not specified")

    def fill_angles_list_v3(self):
        match self.leg_name:
            case "right":
                self.thigh_angles_list = [0.496880138, 0.333487092, 0.149438132, -0.079914694,
                                          0.019998667, 0.479425539, 0.767543502,
                                          0.717356091, 0.605186406, 0.581035161,
                                          0.522687229, 0.522687229, 0.496880138]

                self.calf_angles_list = [-0.841, -0.78332691, -0.703279419, -0.605186406,
                                         -0.78332691, -0.98544973, -0.948984619,
                                         -0.644217687, -0.496880138, -0.703279419,
                                         -0.78332691, -0.813415505, -0.841]
            case "left":
                self.thigh_angles_list = [0.767543502, 0.717356091, 0.605186406, 0.581035161,
                                          0.522687229, 0.522687229, 0.496880138,
                                          0.333487092, 0.149438132, -0.079914694,
                                          0.019998667, 0.479425539, 0.767543502]

                self.calf_angles_list = [-0.948984619, -0.644217687, -0.496880138, -0.703279419,
                                         -0.78332691, -0.813415505, -0.841,
                                         -0.78332691, -0.703279419, -0.605186406,
                                         -0.78332691, -0.98544973, -0.948984619]
            case other:
                print("Equation leg name not specified")

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
        t = [phase - 1, phase]

        q_for_thigh = [self.thigh_angles_list[phase - 1],
                       self.thigh_angles_list[phase]]
        q_for_calf = [self.calf_angles_list[phase - 1],
                      self.calf_angles_list[phase]]

        initial_velocity = calculate_initial_velocity(q_for_thigh, q_for_calf)
        self.fill_initial_velocity(phase, initial_velocity, 2)

        thigh_equation = generate_equation(t[0], t[1], q_for_thigh[0], q_for_thigh[1])
        calf_equation = generate_equation(t[0], t[1], q_for_calf[0], q_for_calf[1])
        t_q_for_phase_1 = round(thigh_equation[1] * ((phase - 1) - 1) + thigh_equation[2], 3)
        t_q_for_phase_2 = round(thigh_equation[1] * phase + thigh_equation[2], 3)
        c_q_for_phase_1 = round(calf_equation[1] * ((phase - 1) - 1) + calf_equation[2], 3)
        c_q_for_phase_2 = round(calf_equation[1] * phase + calf_equation[2], 3)

        velocity = [thigh_equation[1], calf_equation[1]]
        self.fill_initial_velocity(phase, velocity, 3)

        dictionary = dict(name=dict_name, thigh_equation=thigh_equation[0], calf_equation=calf_equation[0],
                          time=phase, thigh_q_start=t_q_for_phase_1, calf_q_start=c_q_for_phase_1,
                          thigh_q_stop=t_q_for_phase_2, calf_q_stop=c_q_for_phase_2,
                          thigh_initial_velocity=initial_velocity[0], calf_initial_velocity=initial_velocity[1])

        return dictionary

    def fill_initial_velocity(self, phase: int, initial_velocity: list, used_scenario: int):
        self.thigh_velocity[used_scenario][phase] = initial_velocity[0]
        self.calf_velocity[used_scenario][phase] = initial_velocity[1]

    def fill_dictionaries(self):
        i = 1
        for i in range(1, 12):
            self.list_of_equations_dictionaries.append(self.fill_equation_dictionary("phase_equation_" + str(i), i))
            i += 1

        print("thigh velocity list= ", self.thigh_velocity)
        print("calf velocity list= ", self.calf_velocity)
        pass

    def fill_velocity_list(self, velocity: float):
        for j in range(1, 4):
            for i in range(0, 14):
                self.thigh_velocity[j].append(velocity)
                self.calf_velocity[j].append(velocity)
