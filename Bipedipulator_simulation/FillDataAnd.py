import pandas as pd

from Bipedipulator_simulation.Leg import Leg
from Bipedipulator_simulation.Model import Model


def write_data_to_excel(model: Model):
    fill_data_for_txt(model.right_leg)
    fill_data_for_txt(model.left_leg)
    fill_data(model.left_leg, 1)
    fill_data(model.right_leg, 1)
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
    columns = ['right_thigh_angles_list', 'right_calf_angles_list', 'left_thigh_angles_list', 'left_calf_angles_list']
    data = [model.right_leg.equations.thigh_angles_list, model.right_leg.equations.calf_angles_list,
            model.left_leg.equations.thigh_angles_list, model.left_leg.equations.calf_angles_list]

    df2 = pd.DataFrame(zip(*data), columns=columns)

    with pd.ExcelWriter("../resources/equations.xlsx") as writer:
        df2.to_excel(writer, sheet_name="equations", engine="xlsxwriter")


def fill_data(leg_entity: Leg, scenario: int):
    columns = ['x_hip', 'y_hip', 'angle_thigh', 'x_knee', 'y_knee', 'angle_calf', 'x_ankle',
               'y_ankle', 'hip_velocity', 'knee_velocity', 'ankle_velocity',
               'current_thigh_velocity_value', 'current_calf_velocity_value', 'mirror_angle_thigh', 'mirror_angle_calf']

    data = {col: [] for col in columns}

    for used_scenario in range(scenario, 3):
        histories = leg_entity.relative_values[used_scenario].histories
        velocities = leg_entity.equations.velocities[used_scenario].histories

        for i in range(len(histories)):
            data['x_hip'].append(histories[i][1])
            data['y_hip'].append(histories[i][2])
            data['angle_thigh'].append(histories[i][3])
            data['x_knee'].append(histories[i][4])
            data['y_knee'].append(histories[i][5])
            data['angle_calf'].append(histories[i][6])
            data['x_ankle'].append(histories[i][7])
            data['y_ankle'].append(histories[i][8])
            data['knee_velocity'].append(histories[i][10])
            data['hip_velocity'].append(histories[i][11])
            data['ankle_velocity'].append(histories[i][12])
            data['current_thigh_velocity_value'].append(velocities[i][0])
            data['current_calf_velocity_value'].append(velocities[i][1])
            data['mirror_angle_thigh'].append(-1 * histories[i][3])
            data['mirror_angle_calf'].append(-1 * histories[i][6])

    df = pd.DataFrame(data, index=data['x_hip'])

    file_path = f"../resources/{leg_entity.name}_leg_data.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name=f"{leg_entity.name}_leg", engine="xlsxwriter")
