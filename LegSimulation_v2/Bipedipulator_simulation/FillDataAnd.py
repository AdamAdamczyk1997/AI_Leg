from math import asin

import pandas as pd

from LegSimulation_v2.Bipedipulator_simulation.Leg import Leg
from LegSimulation_v2.Bipedipulator_simulation.Model import Model


def write_data_to_excel(model: Model):
    fill_data_for_txt(model.right_leg)
    fill_data_for_txt(model.left_leg)
    fill_date(model.left_leg, 2)
    fill_date(model.right_leg, 2)
    fill_equation(model)


def fill_data_for_txt(leg_entity: Leg):
    file_name = '../resources/' + str(leg_entity.name) + '_exporting_data_.txt'
    dictionaries = leg_entity.equations.list_of_equations_dictionaries
    write_list_of_dictionaries_to_txt_file(file_name, dictionaries)


def write_list_of_dictionaries_to_txt_file(file_name: str, list_of_dictionaries: list):
    try:
        with open(file_name, 'w') as file:
            for dictionary in list_of_dictionaries:
                for key, value in dictionary.items():
                    file.write(f'{key}: {value}\n')
                file.write('\n')

    except FileExistsError:
        with open(file_name, 'w') as file:
            for dictionary in list_of_dictionaries:
                for key, value in dictionary.items():
                    file.write(f'{key}: {value}\n')
                file.write('\n')


def fill_equation(model: Model):
    columns2 = ['right_thigh_angles_list', 'right_calf_angles_list', 'left_thigh_angles_list', 'left_calf_angles_list']
    right_thigh_angles_list = []
    right_calf_angles_list = []
    left_thigh_angles_list = []
    left_calf_angles_list = []

    for i in range(0, len(model.right_leg.equations.thigh_angles_list)):
        right_thigh_angles_list.append(model.right_leg.equations.thigh_angles_list[i])
        i += 1
    for i in range(0, len(model.right_leg.equations.calf_angles_list)):
        right_calf_angles_list.append(model.right_leg.equations.calf_angles_list[i])
        i += 1
    for i in range(0, len(model.left_leg.equations.thigh_angles_list)):
        left_thigh_angles_list.append(model.left_leg.equations.thigh_angles_list[i])
        i += 1
    for i in range(0, len(model.left_leg.equations.calf_angles_list)):
        left_calf_angles_list.append(model.left_leg.equations.calf_angles_list[i])
        i += 1

    df2 = pd.DataFrame(list(zip(right_thigh_angles_list, right_calf_angles_list, left_thigh_angles_list,
                                left_calf_angles_list)),
                       columns=columns2)
    with pd.ExcelWriter("../resources/equations.xlsx") as writer:
        df2.to_excel(writer, sheet_name="equations", engine="xlsxwriter")


def fill_date(leg_entity: Leg, scenario: int):
    # TODO: refactor this, move something to another methods
    columns = ['x_hip', 'y_hip', 'angle_thigh', 'x_knee', 'y_knee', 'angle_calf', 'x_ankle',
               'y_ankle', 'hip_velocity', 'knee_velocity', 'ankle_velocity',
               'current_thigh_velocity_value', 'current_calf_velocity_value', 'mirror_angle_thigh', 'mirror_angle_calf',
               'mirror_angle_thigh_radians', 'mirror_angle_calf_radians']

    usage_counter = []
    x_hip = []
    y_hip = []
    angle_thigh = []
    x_knee = []
    y_knee = []
    angle_calf = []
    x_ankle = []
    y_ankle = []
    knee_velocity = []
    hip_velocity = []
    ankle_velocity = []
    current_thigh_velocity_value = []
    current_calf_velocity_value = []
    mirror_angle_thigh = []
    mirror_angle_calf = []
    mirror_angle_thigh_radians = []
    mirror_angle_calf_radians = []
    used_scenario = scenario

    while used_scenario <= 2:
        length = len(leg_entity.relative_values[used_scenario].histories)
        for i in range(1, length):
            usage_counter.append(leg_entity.relative_values[used_scenario].histories[i][0])
            x_hip.append(leg_entity.relative_values[used_scenario].histories[i][1])
            y_hip.append(leg_entity.relative_values[used_scenario].histories[i][2])
            angle_thigh.append(leg_entity.relative_values[used_scenario].histories[i][3])
            x_knee.append(leg_entity.relative_values[used_scenario].histories[i][4])
            y_knee.append(leg_entity.relative_values[used_scenario].histories[i][5])
            angle_calf.append(leg_entity.relative_values[used_scenario].histories[i][6])
            x_ankle.append(leg_entity.relative_values[used_scenario].histories[i][7])
            y_ankle.append(leg_entity.relative_values[used_scenario].histories[i][8])
            knee_velocity.append(leg_entity.relative_values[used_scenario].histories[i][10])
            hip_velocity.append(leg_entity.relative_values[used_scenario].histories[i][11])
            ankle_velocity.append(leg_entity.relative_values[used_scenario].histories[i][12])
            current_thigh_velocity_value.append(leg_entity.equations.velocities[used_scenario].histories[i][0])
            current_calf_velocity_value.append(leg_entity.equations.velocities[used_scenario].histories[i][1])
            mirror_angle_thigh.append(-1 * (leg_entity.relative_values[used_scenario].histories[i][3]))
            mirror_angle_calf.append(-1 * (leg_entity.relative_values[used_scenario].histories[i][6]))
            mirror_angle_thigh_radians.append(asin(-1 * (leg_entity.relative_values[used_scenario].histories[i][3])))
            mirror_angle_calf_radians.append(asin(-1 * (leg_entity.relative_values[used_scenario].histories[i][6])))
            i += 1
        used_scenario += 1

    df = pd.DataFrame(list(zip(x_hip, y_hip, angle_thigh, x_knee, y_knee, angle_calf, x_ankle, y_ankle
                               , hip_velocity, knee_velocity, ankle_velocity,
                               current_thigh_velocity_value, current_calf_velocity_value, mirror_angle_thigh,
                               mirror_angle_calf, mirror_angle_thigh_radians, mirror_angle_calf_radians)),
                      index=usage_counter,
                      columns=columns)

    match leg_entity.name:
        case "right":
            with pd.ExcelWriter("../resources/right_leg_data.xlsx") as writer:
                df.to_excel(writer, sheet_name="right_leg", engine="xlsxwriter")
        case "left":
            with pd.ExcelWriter("../resources/left_leg_data.xlsx") as writer:
                df.to_excel(writer, sheet_name="left_leg", engine="xlsxwriter")
