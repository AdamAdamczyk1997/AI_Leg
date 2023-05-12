from __future__ import annotations

from LegSimulation_v2.Bipedipulator_simulation.constants import fill_angles_list_v2

start_velocity_value = 0.25


def calculate_velocity_change_angle(time: float, velocity: float):
    # velocity is first derivative angle of time, example for Q=-0.6t + 1, velocity is -0.6
    velocity_change_angle = velocity / time
    return velocity_change_angle


def generate_equation(q_1: float, q_2: float):
    B = round(q_1, 3)
    A = round((q_2 - B), 3)
    equation = str(A) + " * t + " + str(B)

    return [equation, A, B]


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

    velocities: list[Velocity]

    def __init__(self, leg_name: str):
        self.leg_name = leg_name
        self.thigh_velocity = []
        self.calf_velocity = []
        self.list_of_equations_dictionaries = []

        self.fill_velocity_lists(start_velocity_value)
        # self.fill_angles_list_v1()
        angles = fill_angles_list_v2(leg_name)
        self.thigh_angles_list = angles[0]
        self.calf_angles_list = angles[1]
        # self.fill_angles_list_v3()
        self.fill_dictionaries()
        self.velocities = [Velocity([start_velocity_value], [start_velocity_value]),
                           Velocity(self.thigh_velocity[0], self.calf_velocity[0]),
                           Velocity(self.thigh_velocity[1], self.calf_velocity[1])]

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
        self.fill_upgrade_velocities_lists(phase, initial_velocity)

        dictionary = dict(name=dict_name, thigh_equation=thigh_equation[0], calf_equation=calf_equation[0],
                          time=phase, thigh_q_stop=t_q_for_phase_1, calf_q_stop=c_q_for_phase_1,
                          thigh_initial_velocity=abs(round(initial_velocity[0], 3)),
                          calf_initial_velocity=abs(round(initial_velocity[1], 3)))

        return dictionary

    def fill_upgrade_velocities_lists(self, phase: int, initial_velocity: list):
        used_scenario = 1
        self.thigh_velocity[used_scenario][phase] = abs(round(initial_velocity[0], 3))
        self.calf_velocity[used_scenario][phase] = abs(round(initial_velocity[1], 3))

    def fill_dictionaries(self):
        for i in range(1, 12):
            self.list_of_equations_dictionaries.append(self.fill_equation_dictionary("phase_equation_" + str(i), i))
            i += 1

        print("thigh velocity list= ", self.thigh_velocity)
        print("calf velocity list= ", self.calf_velocity)
        pass

    def fill_velocity_lists(self, velocity: float):
        for j in range(0, 2):
            self.thigh_velocity.append([])
            self.calf_velocity.append([])
            for i in range(0, 13):
                self.thigh_velocity[j].append(velocity)
                self.calf_velocity[j].append(velocity)
