from __future__ import annotations

from LegSimulation_v2.Bipedipulator_simulation.constants import THIGH_ANGLES_LIST, CALF_ANGLES_LIST

start_velocity_value = 0.25


def generate_equation(q_1: float, q_2: float):
    B = round(q_1, 3)
    A = round((q_2 - B), 3)
    equation = str(A) + " * t + " + str(B)

    return [equation, A, B]


def fill_angles_list(leg_name: str):
    thigh_angles_list = THIGH_ANGLES_LIST[leg_name]
    calf_angles_list = CALF_ANGLES_LIST[leg_name]
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
        for i in range(0, 13):
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

        constant_velocities = fill_velocity_lists(start_velocity_value, start_velocity_value, 13)
        different_velocities = self.fill_dictionaries()
        self.velocities = [Velocity([start_velocity_value], [start_velocity_value]),
                           Velocity(constant_velocities[0], constant_velocities[1]),
                           Velocity(different_velocities[0], different_velocities[1])]

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

        thigh_equation = generate_equation(q_for_thigh[0], q_for_thigh[1])
        calf_equation = generate_equation(q_for_calf[0], q_for_calf[1])

        t_q_for_phase_1 = round(thigh_equation[1] + thigh_equation[2], 3)
        c_q_for_phase_1 = round(calf_equation[1] + calf_equation[2], 3)

        initial_velocity = [(thigh_equation[1] * 100), (calf_equation[1] * 100)]

        dictionary = dict(name=dict_name, thigh_equation=thigh_equation[0], calf_equation=calf_equation[0],
                          time=phase, thigh_q_stop=t_q_for_phase_1, calf_q_stop=c_q_for_phase_1,
                          thigh_initial_velocity=abs(round(initial_velocity[0], 3)),
                          calf_initial_velocity=abs(round(initial_velocity[1], 3)))

        return dictionary

    def fill_dictionaries(self):
        thigh_velocity = [start_velocity_value]
        calf_velocity = [start_velocity_value]
        for i in range(1, 13):
            dictionary_per_phase = self.fill_equation_dictionary("phase_equation_" + str(i), i)
            self.list_of_equations_dictionaries.append(dictionary_per_phase)
            different_velocities = fill_velocity_lists(dictionary_per_phase['thigh_initial_velocity'],
                                                       dictionary_per_phase['calf_initial_velocity'], 1)
            thigh_velocity.append(different_velocities[0][0])
            calf_velocity.append(different_velocities[1][0])
            i += 1

        return [thigh_velocity, calf_velocity]
