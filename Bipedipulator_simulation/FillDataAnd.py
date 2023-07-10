import pandas as pd

from Bipedipulator_simulation.Leg import Leg
from Bipedipulator_simulation.Model import Model
from Bipedipulator_simulation.constants import NUMBER_SIMULATION_STEPS


def export_data_to_files(model: Model):
    export_data_to_txt(model.right_leg)
    export_data_to_txt(model.left_leg)
    export_data_to_excel(model.left_leg)
    export_data_to_excel(model.right_leg)
    export_angles_lists_to_excel(model)
    save_usage_lists_to_excel(model)


def save_to_excel(data: list, file_name="gravity_validation_results.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)


def save_usage_lists_to_excel(model_entity: Model):
    file_name = "../resources/usage_lists_results.xlsx"
    # columns = ['right_leg_usage_list_v_constant', 'right_leg_usage_list_v_mutable', 'left_leg_usage_list_v_constant',
    #            'left_leg_usage_list_v_mutable']

    columns = ['right_thigh_angular_velocity_usage_constant', 'right_calf_angular_velocity_usage_constant',
               'left_thigh_angular_velocity_usage_constant', 'left_calf_angular_velocity_usage_constant',
               'right_thigh_angular_velocity_usage_mutable', 'right_calf_angular_velocity_usage_mutable',
               'left_thigh_angular_velocity_usage_constant', 'left_calf_angular_velocity_usage_mutable']


    # data = {col: [] for col in columns}
    # data = [model_entity.right_leg.relative_values[1].counters.phase_usage_list, model_entity.right_leg.relative_values[2].counters.phase_usage_list,
    #         model_entity.left_leg.relative_values[1].counters.phase_usage_list, model_entity.left_leg.relative_values[2].counters.phase_usage_list]

    data = [model_entity.right_leg.equations.angular_velocities[1].thigh_angular_velocity_usage,
            model_entity.right_leg.equations.angular_velocities[1].calf_angular_velocity_usage,
            model_entity.left_leg.equations.angular_velocities[1].thigh_angular_velocity_usage,
            model_entity.left_leg.equations.angular_velocities[1].calf_angular_velocity_usage,
            model_entity.right_leg.equations.angular_velocities[2].thigh_angular_velocity_usage,
            model_entity.right_leg.equations.angular_velocities[2].calf_angular_velocity_usage,
            model_entity.left_leg.equations.angular_velocities[2].thigh_angular_velocity_usage,
            model_entity.left_leg.equations.angular_velocities[2].calf_angular_velocity_usage,
            ]

    df = pd.DataFrame(zip(*data), columns=columns)

    df.to_excel(file_name, index=False)


def export_data_to_txt(leg_entity: Leg):
    file_name = '../resources/' + str(leg_entity.leg_name) + '_exporting_data_.txt'
    dictionaries = leg_entity.equations.angular_velocities_dictionaries_list
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


def export_angles_lists_to_excel(model: Model):
    columns = ['right_thigh_angles_list', 'right_calf_angles_list', 'left_thigh_angles_list', 'left_calf_angles_list']
    data = [model.right_leg.equations.thigh_angles_list, model.right_leg.equations.calf_angles_list,
            model.left_leg.equations.thigh_angles_list, model.left_leg.equations.calf_angles_list]

    df2 = pd.DataFrame(zip(*data), columns=columns)

    with pd.ExcelWriter("../resources/equations.xlsx") as writer:
        df2.to_excel(writer, sheet_name="equations", engine="xlsxwriter")


def export_data_to_excel(leg_entity: Leg):
    columns = ['iteration no.', 'x_hip', 'y_hip', 'angle_thigh', 'x_knee', 'y_knee', 'angle_calf', 'x_ankle',
               'y_ankle', 'hip_velocity', 'knee_velocity', 'ankle_velocity',
               'current_thigh_velocity_value', 'current_calf_velocity_value', 'mirror_angle_thigh', 'mirror_angle_calf']

    data = {col: [] for col in columns}
    start_simulation_step = 1

    for used_scenario in range(start_simulation_step, NUMBER_SIMULATION_STEPS):
        histories = leg_entity.relative_values[used_scenario].histories
        velocities = leg_entity.equations.angular_velocities[used_scenario].angular_velocities_histories

        for i in range(len(histories)):
            data['iteration no.'].append(i + 1)
            data['x_hip'].append(histories[i][1])
            data['y_hip'].append(histories[i][2])
            data['angle_thigh'].append(histories[i][3])
            data['x_knee'].append(histories[i][4])
            data['y_knee'].append(histories[i][5])
            data['angle_calf'].append(histories[i][6])
            data['x_ankle'].append(histories[i][7])
            data['y_ankle'].append(histories[i][8])
            data['knee_velocity'].append(histories[i][9])
            data['hip_velocity'].append(histories[i][10])
            data['ankle_velocity'].append(histories[i][11])
            data['current_thigh_velocity_value'].append(velocities[i][0])
            data['current_calf_velocity_value'].append(velocities[i][1])
            data['mirror_angle_thigh'].append(-1 * histories[i][3])
            data['mirror_angle_calf'].append(-1 * histories[i][6])

    df = pd.DataFrame(data, index=data['iteration no.'])

    file_path = f"../resources/{leg_entity.leg_name}_leg_data.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name=f"{leg_entity.leg_name}_leg", engine="xlsxwriter", index=False)
