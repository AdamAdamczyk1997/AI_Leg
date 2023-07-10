from __future__ import annotations

from Bipedipulator_simulation.constants import THIGH_ANGLES_LIST, CALF_ANGLES_LIST, \
    BASE_ANGULAR_VELOCITY_VALUE, NUMBER_SIMULATION_STEPS, AMOUNT_PHASES, SCENARIO


class AngularVelocities:
    thigh_angular_velocity_list: list
    calf_angular_velocity_list: list

    thigh_angular_velocity_usage: list
    calf_angular_velocity_usage: list

    current_thigh_angular_velocity_value: float
    current_calf_angular_velocity_value: float

    angular_velocities_histories: list

    def __init__(self, thigh_velocity: list, calf_velocity: list):
        self.fill_angular_velocity(thigh_velocity, calf_velocity)
        self.angular_velocities_histories = [[self.current_thigh_angular_velocity_value,
                                              self.current_calf_angular_velocity_value]]
        self.show_velocity_lists()

    def update_current_velocity(self, thigh_velocity: float, calf_velocity: float, phase: int):
        history_record = [self.current_thigh_angular_velocity_value, self.current_calf_angular_velocity_value]
        self.angular_velocities_histories.append(history_record)

        self.current_thigh_angular_velocity_value = thigh_velocity
        if not thigh_velocity == 0.0:
            self.increment_angular_velocity_usage("thigh", phase)
        self.current_calf_angular_velocity_value = calf_velocity
        if not calf_velocity == 0.0:
            self.increment_angular_velocity_usage("calf", phase)

    def fill_angular_velocity(self, thigh_velocity: list, calf_velocity: list):
        self.thigh_angular_velocity_list = []
        self.calf_angular_velocity_list = []

        self.current_thigh_angular_velocity_value = 0.0
        self.current_calf_angular_velocity_value = 0.0

        self.thigh_angular_velocity_usage = []
        self.calf_angular_velocity_usage = []

        self.thigh_angular_velocity_list = thigh_velocity
        self.calf_angular_velocity_list = calf_velocity

        self.fill_angular_velocity_usage_list()

    def fill_angular_velocity_usage_list(self):
        for i in range(0, AMOUNT_PHASES + 1):
            self.thigh_angular_velocity_usage.append(0)
            self.calf_angular_velocity_usage.append(0)

    def increment_angular_velocity_usage(self, body_part: str, phase: int):
        match body_part:
            case "thigh":
                self.thigh_angular_velocity_usage[phase] += 1
            case "calf":
                self.calf_angular_velocity_usage[phase] += 1

    def show_velocity_lists(self):
        print("thigh velocity list= ", self.thigh_angular_velocity_list)
        print("calf velocity list= ", self.calf_angular_velocity_list)


class Equations(str):
    leg_name: str

    thigh_angles_list: list[float]
    calf_angles_list: list[float]

    angular_velocities_dictionaries_list: list[dict]
    angular_velocities: list[AngularVelocities]

    def __init__(self, leg_name: str):
        self.leg_name = leg_name
        self.angular_velocities_dictionaries_list = []

        angles = fill_angles_list(leg_name)
        self.thigh_angles_list = angles[0]
        self.calf_angles_list = angles[1]

        constant_angular_velocities = fill_velocity_lists(BASE_ANGULAR_VELOCITY_VALUE, BASE_ANGULAR_VELOCITY_VALUE,
                                                          AMOUNT_PHASES + 1)
        different_angular_velocities = self.fill_dictionaries()
        angular_velocities = [constant_angular_velocities, different_angular_velocities]
        # angular_velocities = [constant_angular_velocities, constant_angular_velocities]

        self.angular_velocities = [AngularVelocities([BASE_ANGULAR_VELOCITY_VALUE], [BASE_ANGULAR_VELOCITY_VALUE])]
        for i in range(0, NUMBER_SIMULATION_STEPS - 1):
            self.angular_velocities.append(
                AngularVelocities(angular_velocities[i][0], angular_velocities[i][1]))

        for t in range(1, self.angular_velocities.__len__()):
            print(f"Lists of angular velocities for simulation step {t}: {angular_velocities[t - 1]}")

    def fill_dictionaries(self):
        other_leg_angles = get_other_leg_angles(self.leg_name)
        thigh_velocity = [BASE_ANGULAR_VELOCITY_VALUE]
        calf_velocity = [BASE_ANGULAR_VELOCITY_VALUE]
        for i in range(1, AMOUNT_PHASES + 1):
            dictionary_per_phase = self.fill_dictionary("phase_equation_" + str(i), i, other_leg_angles)
            self.angular_velocities_dictionaries_list.append(dictionary_per_phase)
            thigh_velocity.append(dictionary_per_phase['thigh_initial_angular_velocity'])
            calf_velocity.append(dictionary_per_phase['calf_initial_angular_velocity'])

        return [thigh_velocity, calf_velocity]

    def fill_dictionary(self, dict_name: str, phase: int, other_leg_angles: list):
        current_phase_angle_thigh = self.thigh_angles_list[phase]
        previous_phase_angle_thigh = self.thigh_angles_list[phase - 1]
        current_phase_angle_calf = self.calf_angles_list[phase]
        previous_phase_angle_calf = self.calf_angles_list[phase - 1]

        other_leg_change_angle_thigh = abs(other_leg_angles[0][phase - 1] -
                                           other_leg_angles[0][phase])
        other_leg_change_angle_calf = abs(other_leg_angles[1][phase - 1] -
                                          other_leg_angles[1][phase])

        initial_angular_velocity = calculate_angular_velocities(
            abs(previous_phase_angle_thigh - current_phase_angle_thigh),
            abs(previous_phase_angle_calf - current_phase_angle_calf),
            other_leg_change_angle_thigh, other_leg_change_angle_calf)

        dictionary = dict(name=dict_name,
                          thigh_initial_angular_velocity=abs(round(initial_angular_velocity[0], 2)),
                          calf_initial_angular_velocity=abs(round(initial_angular_velocity[1], 2)))

        return dictionary

    def get_angle(self, leg_part: str, phase: int):
        match leg_part:
            case "thigh":
                return self.thigh_angles_list[phase]
            case "calf":
                return self.calf_angles_list[phase]


def fill_velocity_lists(thigh_velocities: float, calf_velocities: float, range_phase: int):
    thigh_velocity = []
    calf_velocity = []
    for i in range(0, range_phase):
        thigh_velocity.append(thigh_velocities)
        calf_velocity.append(calf_velocities)

    return [thigh_velocity, calf_velocity]


def calculate_angular_velocities(thigh_angle, calf_angle, other_thigh_ang, other_calf_ang):
    angles = [thigh_angle, calf_angle, other_thigh_ang, other_calf_ang]

    min_angular_velocity = 0.15
    max_angular_velocity = 0.35
    min_angle = min(angles)
    max_angle = max(angles)

    angular_velocities = []
    for angle in angles:
        if angle == min_angle:
            angular_velocities.append(min_angular_velocity)
        elif angle == max_angle:
            angular_velocities.append(max_angular_velocity)
        else:
            scale = (angle - min_angle) / (max_angle - min_angle)
            angular_velocities.append(min_angular_velocity + scale * (max_angular_velocity - min_angular_velocity))

    return [angular_velocities[0], angular_velocities[1]]


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
