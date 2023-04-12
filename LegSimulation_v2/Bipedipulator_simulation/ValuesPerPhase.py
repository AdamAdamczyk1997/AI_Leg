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
    A = round(((q_2 - q_1) / (t_2 - t_1)), 4)
    B = round((q_1 - (A * t_1)), 4)
    equation = str(A) + " * t + " + str(B)

    return equation


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

    lifting_leg_function_equations_part1: dict
    lifting_leg_function_equations_part2: dict
    move_leg_to_the_back_equations: dict
    move_weight_to_leg_equations: dict
    put_thigh_down_equations: dict

    list_of_equations_dictionaries: list

    thigh_velocity: list
    calf_velocity: list

    velocities: Velocity
    new_velocities: Velocity

    def __init__(self, leg_name: str):
        self.thigh_velocity = []
        self.calf_velocity = []
        self.leg_name = leg_name
        self.fill_velocity_list(start_velocity_value)
        self.fill_angles_list()
        self.fill_dictionaries()
        self.velocities = Velocity(self.thigh_velocity, self.calf_velocity)

    def fill_angles_list(self):
        match self.leg_name:
            case "right":
                self.thigh_angles_list = [0.15, 0.10, 0.05, 0.00,
                                          0.12, 0.24, 0.31, 0.38,
                                          0.45, 0.35, 0.275, 0.20]

                self.calf_angles_list = [-0.3, -0.4, -0.5, -0.6,
                                         -0.5, -0.4, -0.3, -0.2,
                                         -0.1, -0.1, -0.3, -0.20]
            case "left":
                self.thigh_angles_list = [0.31, 0.38, 0.45, 0.35,
                                          0.275, 0.20, 0.15, 0.10,
                                          0.05, 0.00, 0.12, 0.24]

                self.calf_angles_list = [-0.3, -0.2, -0.1, -0.1,
                                         -0.3, -0.20, -0.3, -0.4,
                                         -0.5, -0.6, -0.5, -0.4]
            case other:
                print("Equation leg name not specified")

    def get_angle(self, leg_part: str, phase: int):
        match leg_part:
            case "thigh":
                return self.thigh_angles_list[phase - 1]
            case "calf":
                return self.calf_angles_list[phase - 1]

    def show_angles_lists(self):
        print("thigh angles list= ", self.thigh_angles_list)
        print("calf angles list= ", self.calf_angles_list)

    def fill_equation_dictionary(self, dict_name: str, phase_1: int, phase_2: int):
        start_phase = phase_1 - 1
        stop_phase = phase_2 - 1
        phase_amount = 12

        t = [(start_phase / phase_amount), (stop_phase / phase_amount)]

        q_for_thigh = [self.thigh_angles_list[phase_1 - 1],
                       self.thigh_angles_list[phase_2 - 1]]
        q_for_calf = [self.calf_angles_list[phase_1 - 1],
                      self.calf_angles_list[phase_2 - 1]]

        initial_velocity = calculate_initial_velocity(q_for_thigh, q_for_calf)
        self.fill_initial_thigh_velocity(phase_1, phase_2, initial_velocity)

        thigh_equation = generate_equation(t[0], t[1], q_for_thigh[0], q_for_thigh[1])
        calf_equation = generate_equation(t[0], t[1], q_for_calf[0], q_for_calf[1])

        dictionary = dict(name=dict_name, thigh_equation=thigh_equation, calf_equation=calf_equation,
                          start_time=start_phase, stop_time=stop_phase,
                          thigh_initial_velocity=initial_velocity[0], calf_initial_velocity=initial_velocity[1])

        return dictionary

    def fill_initial_thigh_velocity(self, phase_1: int, phase_2: int, initial_velocity: list):
        phase = int(phase_1)
        for i in range(phase_1, phase_2):
            self.thigh_velocity[phase] = initial_velocity[0]
            self.calf_velocity[phase] = initial_velocity[1]
            phase += 1

    def fill_dictionaries(self):
        match self.leg_name:
            case "right":
                self.move_leg_to_the_back_equations = \
                    self.fill_equation_dictionary("move_leg_to_the_back_equations", 1, 4)
                self.lifting_leg_function_equations_part1 = \
                    self.fill_equation_dictionary("lifting_leg_function_equations_part1", 4, 7)
                self.lifting_leg_function_equations_part2 = \
                    self.fill_equation_dictionary("lifting_leg_function_equations_part2", 7, 9)
                self.put_thigh_down_equations = \
                    self.fill_equation_dictionary("put_thigh_down_equations", 9, 11)
                self.move_weight_to_leg_equations = \
                    self.fill_equation_dictionary("move_weight_to_leg_equations", 11, 12)
                self.list_of_equations_dictionaries = [
                    self.move_leg_to_the_back_equations, self.lifting_leg_function_equations_part1,
                    self.lifting_leg_function_equations_part2, self.put_thigh_down_equations,
                    self.move_weight_to_leg_equations
                ]
            case "left":
                self.lifting_leg_function_equations_part2 = \
                    self.fill_equation_dictionary("lifting_leg_function_equations_part2", 1, 3)
                self.put_thigh_down_equations = \
                    self.fill_equation_dictionary("put_thigh_down_equations", 3, 5)
                self.move_weight_to_leg_equations = \
                    self.fill_equation_dictionary("move_weight_to_leg_equations", 5, 6)
                self.move_leg_to_the_back_equations = \
                    self.fill_equation_dictionary("move_leg_to_the_back_equations", 6, 9)
                self.lifting_leg_function_equations_part1 = \
                    self.fill_equation_dictionary("lifting_leg_function_equations_part1", 9, 12)
                self.list_of_equations_dictionaries = [
                    self.lifting_leg_function_equations_part2, self.put_thigh_down_equations,
                    self.move_weight_to_leg_equations, self.move_leg_to_the_back_equations,
                    self.lifting_leg_function_equations_part1
                ]
                print("lifting_leg_function_equations_part2 = ", self.lifting_leg_function_equations_part2)
                print("put_thigh_down = ", self.put_thigh_down_equations)
                print("move_weight_to_leg = ", self.move_weight_to_leg_equations)
                print("move_leg_to_the_back = ", self.move_leg_to_the_back_equations)
                print("lifting_leg_function_equations_part1 = ", self.lifting_leg_function_equations_part1)

        print("thigh velocity list= ", self.thigh_velocity)
        print("calf velocity list= ", self.calf_velocity)
        pass

    def fill_velocity_list(self, velocity: float):
        for i in range(0, 14):
            self.thigh_velocity.append(velocity)
            self.calf_velocity.append(velocity)
