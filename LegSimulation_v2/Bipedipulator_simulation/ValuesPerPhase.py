from enum import Enum

start_velocity_value = 0.25


class ChangeVelocitySignal(Enum):
    INCREASE_MAX = 0.1
    INCREASE = 0.05
    REDUCE = -0.05
    REDUCE_MAX = -0.1


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


class Equations:
    right_thigh_angles_list: list[list[list[float]]]
    right_cale_angles_list: list[list[list[float]]]

    left_thigh_angles_list: list[list[list[float]]]
    left_cale_angles_list: list[list[list[float]]]

    def __init__(self):
        self.fill_angles_list()

    def fill_angles_list(self):
        self.right_thigh_angles_list = [[[0.2, 0.15], [0.15, 0.10]], [[0.10, 0.05], [0.05, 0.00]],
                                        [[0.00, 0.12], [0.12, 0.24]], [[0.24, 0.31], [0.31, 0.38]],
                                        [[0.38, 0.45], [0.45, 0.35]], [[0.35, 0.25], [0.25, 0.20]]]

        self.right_cale_angles_list = [[[-0.2, -0.3], [-0.3, -0.4]], [[-0.4, -0.5], [-0.5, -0.6]],
                                       [[-0.6, -0.5], [-0.5, -0.4]], [[-0.4, -0.3], [-0.3, -0.2]],
                                       [[-0.2, -0.1], [-0.1, -0.1]], [[-0.1, -0.3], [-0.3, -0.20]]]

        self.left_thigh_angles_list = [[[0.24, 0.31], [0.31, 0.38]], [[0.38, 0.45], [0.45, 0.35]],
                                       [[0.35, 0.25], [0.25, 0.20]], [[0.2, 0.15], [0.15, 0.10]],
                                       [[0.10, 0.05], [0.05, 0.00]], [[0.00, 0.12], [0.12, 0.24]]]

        self.left_cale_angles_list = [[[-0.4, -0.3], [-0.3, -0.2]], [[-0.2, -0.1], [-0.1, -0.1]],
                                      [[-0.1, -0.3], [-0.3, -0.20]], [[-0.2, -0.3], [-0.3, -0.4]],
                                      [[-0.4, -0.5], [-0.5, -0.6]], [[-0.6, -0.5], [-0.5, -0.4]]]

    def get_angle(self, leg: str, leg_part: str, phase: int, phase_part: int):
        match leg:
            case "right":
                match leg_part:
                    case "thigh":
                        return self.right_thigh_angles_list[phase][phase_part]
                    case "cale":
                        return self.right_cale_angles_list[phase][phase_part]
            case "left":
                match leg_part:
                    case "thigh":
                        return self.left_thigh_angles_list[phase][phase_part]
                    case "cale":
                        return self.left_cale_angles_list[phase][phase_part]
