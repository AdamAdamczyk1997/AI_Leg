from __future__ import annotations

from enum import Enum
from pymunk import vec2d, Vec2d

start_velocity_value = 0.25


class ChangeVelocitySignal(Enum):
    INCREASE_MAX = 0.1
    INCREASE = 0.05
    REDUCE = -0.05
    REDUCE_MAX = -0.1


def generate_equation(t_1: float, t_2: float, q_1: float, q_2: float):
    A = round(((q_2 - q_1) / (t_2 - t_1)), 4)
    B = round((q_1 - (A * t_1)), 4)
    equation = str(A) + " * t + " + str(B)

    return equation


def calculate_need_velocity(phase, part_phase, q_for_first: list, q_for_second: list):
    distance_1 = abs(q_for_first[0] - q_for_first[1])
    distance_2 = abs(q_for_second[0] - q_for_second[1])
    if distance_1 < distance_2:
        velocity_2 = 0.20
        velocity_1 = round(distance_1 / (distance_2 / velocity_2), 2)
    elif distance_1 > distance_2:
        velocity_1 = 0.20
        velocity_2 = round(distance_2 / (distance_1 / velocity_1), 2)
    else:
        velocity_1 = 0.20
        velocity_2 = 0.20
    print("Calculating velocity velocity_1/_2", velocity_1, velocity_2)


class Velocity(float):
    thigh_velocity: list
    cale_velocity: list

    thigh_time: list
    cale_time: list

    current_thigh_velocity_value: float
    current_cale_velocity_value: float

    def __init__(self, start_velocity: float):
        self.thigh_velocity = []
        self.cale_velocity = []
        self.current_thigh_velocity_value = 0.0
        self.current_cale_velocity_value = 0.0
        self.thigh_time = []
        self.cale_time = []

        if start_velocity:
            self.fill_velocity(start_velocity)
            self.fill_time_list(0)

    def update_current_velocity(self, thigh_velocity: float, cale_velocity: float, phase: int, phase_part: int):
        self.current_thigh_velocity_value = thigh_velocity
        if not thigh_velocity == 0.0:
            self.increment_leg_part_time_usage("thigh", phase, phase_part)
        self.current_cale_velocity_value = cale_velocity
        if not cale_velocity == 0.0:
            self.increment_leg_part_time_usage("cale", phase, phase_part)

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
            record_part_2 = []
            for j in range(2):
                record_part.append(velocity)
                record_part_2.append(velocity)
            self.thigh_velocity.append(record_part)
            self.cale_velocity.append(record_part_2)

    def fill_time_list(self, time: float):
        for i in range(0, 7):
            record_part = []
            record_part_2 = []
            for j in range(2):
                record_part.append(time)
                record_part_2.append(time)
            self.thigh_time.append(record_part)
            self.cale_time.append(record_part_2)

    def increment_leg_part_time_usage(self, body_part: str, phase: int, phase_part: int):
        match body_part:
            case "thigh":
                self.thigh_time[phase][phase_part] += 1
            case "cale":
                self.cale_time[phase][phase_part] += 1

    def show_velocity_lists(self):
        # print("thigh velocity list= ", self.thigh_velocity)
        # print("cale velocity list= ", self.cale_velocity)
        print("thigh time list= ", self.thigh_time)
        print("cale time list= ", self.cale_time)


class Equations(str):
    leg_name: str

    thigh_angles_list: list[list[list[float]]]
    cale_angles_list: list[list[list[float]]]

    current_angle_value_due_to_the_equation: float

    lifting_leg_function_equations: dict
    move_leg_to_the_back_equation: dict
    move_weight_to_leg: dict
    put_thigh_down: dict

    def __init__(self, leg_name: str):
        self.leg_name = leg_name
        self.fill_angles_list()
        self.fill_dictionaries()

    def fill_angles_list(self):
        match self.leg_name:
            case "right":
                self.thigh_angles_list = [[[0.2, 0.15], [0.15, 0.10]], [[0.10, 0.05], [0.05, 0.00]],
                                          [[0.00, 0.12], [0.12, 0.24]], [[0.24, 0.31], [0.31, 0.38]],
                                          [[0.38, 0.45], [0.45, 0.35]], [[0.35, 0.275], [0.275, 0.20]]]

                self.cale_angles_list = [[[-0.2, -0.3], [-0.3, -0.4]], [[-0.4, -0.5], [-0.5, -0.6]],
                                         [[-0.6, -0.5], [-0.5, -0.4]], [[-0.4, -0.3], [-0.3, -0.2]],
                                         [[-0.2, -0.1], [-0.1, -0.1]], [[-0.1, -0.3], [-0.3, -0.20]]]
            case "left":
                self.thigh_angles_list = [[[0.24, 0.31], [0.31, 0.38]], [[0.38, 0.45], [0.45, 0.35]],
                                          [[0.35, 0.275], [0.275, 0.20]], [[0.2, 0.15], [0.15, 0.10]],
                                          [[0.10, 0.05], [0.05, 0.00]], [[0.00, 0.12], [0.12, 0.24]]]

                self.cale_angles_list = [[[-0.4, -0.3], [-0.3, -0.2]], [[-0.2, -0.1], [-0.1, -0.1]],
                                         [[-0.1, -0.3], [-0.3, -0.20]], [[-0.2, -0.3], [-0.3, -0.4]],
                                         [[-0.4, -0.5], [-0.5, -0.6]], [[-0.6, -0.5], [-0.5, -0.4]]]
            case other:
                print("Equation leg name not specified")

    def get_angle(self, leg_part: str, phase: int, phase_part: int):
        match leg_part:
            case "thigh":
                return self.thigh_angles_list[phase - 1][phase_part][1]
            case "cale":
                return self.cale_angles_list[phase - 1][phase_part][1]

    def show_angles_lists(self):
        print("thigh angles list= ", self.thigh_angles_list)
        print("cale angles list= ", self.cale_angles_list)

    def fill_equation_dictionary(self, phase_1: int, part_phase_1: int, phase_2: int, part_phase_2: int):
        start_phase = ((phase_1 - 1) * 2) + part_phase_1
        stop_phase = ((phase_2 - 1) * 2) + part_phase_2
        phase_amount = 12

        t = [(start_phase / phase_amount), (stop_phase / phase_amount)]

        q_for_thigh = [self.thigh_angles_list[phase_1 - 1][part_phase_1][0],
                       self.thigh_angles_list[phase_2 - 1][part_phase_2][0]]
        q_for_cale = [self.cale_angles_list[phase_1 - 1][part_phase_1][0],
                      self.cale_angles_list[phase_2 - 1][part_phase_2][0]]

        calculate_need_velocity(0, 0, q_for_thigh, q_for_cale)

        thigh_equation = generate_equation(t[0], t[1], q_for_thigh[0], q_for_thigh[1])
        cale_equation = generate_equation(t[0], t[1], q_for_cale[0], q_for_cale[1])

        dictionary = dict(thigh_equation=thigh_equation, cale_equation=cale_equation, start_time=start_phase,
                          stop_time=stop_phase)

        return dictionary

    def fill_dictionaries(self):
        match self.leg_name:
            case "right":
                move_leg_to_the_back = self.fill_equation_dictionary(1, 0, 3, 0)
                lifting_leg_function_equations_part1 = self.fill_equation_dictionary(3, 0, 4, 0)
                lifting_leg_function_equations_part2 = self.fill_equation_dictionary(4, 0, 5, 1)
                put_thigh_down = self.fill_equation_dictionary(5, 1, 6, 0)
                move_weight_to_leg = self.fill_equation_dictionary(6, 0, 6, 1)
                print("move_leg_to_the_back = ", move_leg_to_the_back)
                print("lifting_leg_function_equations_part1 = ", lifting_leg_function_equations_part1)
                print("lifting_leg_function_equations_part2 = ", lifting_leg_function_equations_part2)
                print("put_thigh_down = ", put_thigh_down)
                print("move_weight_to_leg = ", move_weight_to_leg)
            case "left":
                pass

        pass
