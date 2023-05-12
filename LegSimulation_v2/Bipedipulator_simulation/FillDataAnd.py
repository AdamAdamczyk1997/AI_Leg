from math import asin

import matplotlib.pyplot as plt
import pandas as pd

from LegSimulation_v2.Bipedipulator_simulation.Model import Model


def write_data_to_excel(model: Model):
    fill_date(model, 0, 0)
    fill_date(model, 1, 0)
    fill_equation(model)
    fill_data_for_txt(model, 0)
    fill_data_for_txt(model, 1)


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


def fill_data_for_txt(model: Model, leg_nr: int):
    global leg
    match leg_nr:
        case 0:
            leg = model.right_leg
        case 1:
            leg = model.left_leg
    file_name = str(leg.name) + '_exporting_data_.txt'
    dictionaries = leg.equations.list_of_equations_dictionaries
    write_list_of_dictionaries_to_txt_file(file_name, dictionaries)


def fill_equation(model: Model):
    columns2 = ['right_thigh_angles_list', 'right_calf_angles_list', 'left_thigh_angles_list', 'left_calf_angles_list']
    right_thigh_angles_list = []
    right_calf_angles_list = []
    left_thigh_angles_list = []
    left_calf_angles_list = []

    i = 0
    for r in model.right_leg.equations.thigh_angles_list:
        right_thigh_angles_list.append(model.right_leg.equations.thigh_angles_list[i])
        i += 1
    i = 0
    for r in model.right_leg.equations.calf_angles_list:
        right_calf_angles_list.append(model.right_leg.equations.calf_angles_list[i])
        i += 1
    i = 0
    for r in model.left_leg.equations.thigh_angles_list:
        left_thigh_angles_list.append(model.left_leg.equations.thigh_angles_list[i])
        i += 1
    i = 0
    for r in model.left_leg.equations.calf_angles_list:
        left_calf_angles_list.append(model.left_leg.equations.calf_angles_list[i])
        i += 1

    df2 = pd.DataFrame(list(zip(right_thigh_angles_list, right_calf_angles_list, left_thigh_angles_list,
                                left_calf_angles_list)),
                       columns=columns2)
    with pd.ExcelWriter("equations.xlsx") as writer:
        df2.to_excel(writer, sheet_name="equations", engine="xlsxwriter")


def fill_date(model: Model, leg_nr: int, scenario: int):
    global leg
    match leg_nr:
        case 0:
            leg = model.right_leg
        case 1:
            leg = model.left_leg
    columns = ['x_hip', 'y_hip', 'angle_thigh', 'x_knee', 'y_knee', 'angle_calf', 'x_ankle',
               'y_ankle', 'real_corps_y',
               'oscillation', 'oscillation_time', 'hip_velocity', 'knee_velocity', 'ankle_velocity',
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
    real_corps_y = []
    oscillation = []
    knee_velocity = []
    hip_velocity = []
    ankle_velocity = []
    current_thigh_velocity_value = []
    current_calf_velocity_value = []
    mirror_angle_thigh = []
    mirror_angle_calf = []

    mirror_angle_thigh_radians = []
    mirror_angle_calf_radians = []
    i = 1

    oscillation_time = []
    used_scenario = scenario

    while used_scenario <= 2:
        length = len(leg.relative_values[used_scenario].histories)
        for r in range(length - 2):
            usage_counter.append(leg.relative_values[used_scenario].histories[i][0])
            x_hip.append(leg.relative_values[used_scenario].histories[i][1])
            y_hip.append(leg.relative_values[used_scenario].histories[i][2])
            angle_thigh.append(leg.relative_values[used_scenario].histories[i][3])
            x_knee.append(leg.relative_values[used_scenario].histories[i][4])
            y_knee.append(leg.relative_values[used_scenario].histories[i][5])
            angle_calf.append(leg.relative_values[used_scenario].histories[i][6])
            x_ankle.append(leg.relative_values[used_scenario].histories[i][7])
            y_ankle.append(leg.relative_values[used_scenario].histories[i][8])
            real_corps_y.append(model.corps.body.position.y)
            oscillation.append(leg.relative_values[used_scenario].histories[i][9])
            knee_velocity.append(leg.relative_values[used_scenario].histories[i][10])
            hip_velocity.append(leg.relative_values[used_scenario].histories[i][11])
            ankle_velocity.append(leg.relative_values[used_scenario].histories[i][12])
            # change to velocity history every step
            current_thigh_velocity_value.append(leg.equations.velocities[used_scenario].histories[i][0])
            current_calf_velocity_value.append(leg.equations.velocities[used_scenario].histories[i][1])
            mirror_angle_thigh.append(-1 * (leg.relative_values[used_scenario].histories[i][3]))
            mirror_angle_calf.append(-1 * (leg.relative_values[used_scenario].histories[i][6]))

            mirror_angle_thigh_radians.append(asin(-1 * (leg.relative_values[used_scenario].histories[i][3])))
            mirror_angle_calf_radians.append(asin(-1 * (leg.relative_values[used_scenario].histories[i][6])))
            i += 1
        used_scenario += 1
        i = 1
        length = 0

    moves_counter_for_phase = 1
    phase_number = 0
    number_of_records = 0
    loop_number = 0
    previous_phase_value = 0
    total_value = 0
    for r in oscillation:
        number_of_records += 1
    while loop_number < number_of_records - 1:
        loop_number += 1
        if oscillation[loop_number] == oscillation[loop_number - 1]:
            moves_counter_for_phase += 1
        else:
            i = 0
            while i <= moves_counter_for_phase:
                i += 1
                last_phase_move_value = oscillation.__getitem__(loop_number - 1)
                oscillation_time.append((((last_phase_move_value - previous_phase_value) / moves_counter_for_phase) * i)
                                        + previous_phase_value + total_value)

            moves_counter_for_phase = 0
            previous_phase_value += (last_phase_move_value - previous_phase_value)
            if phase_number < 6:
                phase_number += 1
            else:
                phase_number = 1
                total_value += previous_phase_value
                previous_phase_value = 0

    while oscillation_time.__len__() != number_of_records:
        oscillation_time.append(0.0)

    df = pd.DataFrame(list(zip(x_hip, y_hip, angle_thigh, x_knee, y_knee, angle_calf, x_ankle, y_ankle,
                               real_corps_y, oscillation,
                               oscillation_time, hip_velocity, knee_velocity, ankle_velocity,
                               current_thigh_velocity_value, current_calf_velocity_value,mirror_angle_thigh,
                               mirror_angle_calf, mirror_angle_thigh_radians, mirror_angle_calf_radians)),
                      index=usage_counter,
                      columns=columns)

    match leg.name:
        case "right":
            with pd.ExcelWriter("right_leg_data.xlsx") as writer:
                df.to_excel(writer, sheet_name="right_leg", engine="xlsxwriter")
        case "left":
            with pd.ExcelWriter("left_leg_data.xlsx") as writer:
                df.to_excel(writer, sheet_name="left_leg", engine="xlsxwriter")
