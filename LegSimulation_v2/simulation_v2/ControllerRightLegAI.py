from LegSimulation_v2.simulation_v2.Leg import Leg
from LegSimulation_v2.simulation_v2.LegMotorController import Controller
from matplotlib import pyplot as plt

import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from LegSimulation_v2.simulation_v2.Model import Model


def write_data_to_excel(model: Model):
    fill_date(model, 0)
    fill_date(model, 1)


def fill_date(model: Model, leg_nr: int):
    global leg
    match leg_nr:
        case 0:
            leg = model.right_leg
        case 1:
            leg = model.left_leg
    columns = ['x_hip', 'y_hip', 'angle_thigh', 'x_knee', 'y_knee', 'angle_cale', 'x_ankle',
               'y_ankle', 'x_toe', 'y_toe', 'x_heel', 'y_heel', 'x_foot', 'y_foot', 'angle_foot', 'real_corps_y',
               'oscillation', 'oscillation_time']

    usage_counter = []
    x_hip = []
    y_hip = []
    angle_thigh = []
    x_knee = []
    y_knee = []
    angle_cale = []
    x_ankle = []
    y_ankle = []
    x_toe = []
    y_toe = []
    x_heel = []
    y_heel = []
    x_foot = []
    y_foot = []
    angle_foot = []
    real_corps_y = []
    oscillation = []
    i = 0

    oscillation_time = []

    for r in leg.relative_values.histories:
        usage_counter.append(leg.relative_values.histories[i][0])
        x_hip.append(leg.relative_values.histories[i][1])
        y_hip.append(leg.relative_values.histories[i][2])
        angle_thigh.append(leg.relative_values.histories[i][3])
        x_knee.append(leg.relative_values.histories[i][4])
        y_knee.append(leg.relative_values.histories[i][5])
        angle_cale.append(leg.relative_values.histories[i][6])
        x_ankle.append(leg.relative_values.histories[i][7])
        y_ankle.append(leg.relative_values.histories[i][8])
        x_toe.append(leg.relative_values.histories[i][9])
        y_toe.append(leg.relative_values.histories[i][10])
        x_heel.append(leg.relative_values.histories[i][11])
        y_heel.append(leg.relative_values.histories[i][12])
        x_foot.append(leg.relative_values.histories[i][13])
        y_foot.append(leg.relative_values.histories[i][14])
        angle_foot.append(leg.relative_values.histories[i][15])
        real_corps_y.append(model.corps.body.position.y)
        oscillation.append(leg.relative_values.histories[i][16])
        i += 1

    moves_counter_for_phase = 1
    phase_number = 0
    number_of_records = 0
    loop_number = 0
    previous_phase_value = 0
    total_value = 0
    for r in oscillation:
        number_of_records += 1

    print("number_of_records =", number_of_records)
    while loop_number < number_of_records - 1:
        loop_number += 1
        if oscillation[loop_number] == oscillation[loop_number - 1]:
            moves_counter_for_phase += 1
        else:
            i = 0
            print("phase_number =", phase_number)
            print("previous_phase_value =", previous_phase_value)
            print("moves_counter_for_phase =", moves_counter_for_phase)
            print("loop_number =", loop_number)
            while i <= moves_counter_for_phase:
                i += 1
                last_phase_move_value = oscillation.__getitem__(loop_number - 1)
                oscillation_time.append((((
                                                      last_phase_move_value - previous_phase_value) / moves_counter_for_phase) * i) + previous_phase_value + total_value)

            moves_counter_for_phase = 0
            previous_phase_value += (last_phase_move_value - previous_phase_value)
            print("last_phase_move_value =", last_phase_move_value)
            print("previous_phase_value =", previous_phase_value)
            if phase_number < 6:
                phase_number += 1
            else:
                phase_number = 1
                total_value += previous_phase_value
                previous_phase_value = 0
                print("previous_phase_value =", previous_phase_value)
            print("total_value =", total_value)
            print("-------------------------------------------------------------")

    print("loop_number =", loop_number)
    while oscillation_time.__len__() != number_of_records:
        oscillation_time.append(0.0)
    print(oscillation_time)

    df = pd.DataFrame(list(zip(x_hip, y_hip, angle_thigh, x_knee, y_knee, angle_cale, x_ankle, y_ankle,
                               x_toe, y_toe, x_heel, y_heel, x_foot, y_foot, angle_foot, real_corps_y, oscillation,
                               oscillation_time)),
                      index=usage_counter,
                      columns=columns)

    match leg.name:
        case "right":
            with pd.ExcelWriter("right_leg_data.xlsx") as writer:
                df.to_excel(writer, sheet_name="right_leg", engine="xlsxwriter")
        case "left":
            with pd.ExcelWriter("left_leg_data.xlsx") as writer:
                df.to_excel(writer, sheet_name="left_leg", engine="xlsxwriter")


class VisualizeDataMatplotlib:

    def __init__(self):
        self.str = str
        self.switch = "ON"

    def run(self, name: str):
        data = pd.read_excel(name)
        # print(data)
        angle_thigh = list(data['angle_thigh'])
        oscillation_time = list(data['oscillation_time'])

        df = pd.DataFrame(data)
        # plt.plot(df)
        # plt.hist(df)
        # plt.show()

        plt.style.use('_mpl-gallery')

        # plot
        fig, ax = plt.subplots()

        ax.plot(oscillation_time, angle_thigh, linewidth=1.0)

        # plt.show()

        print(df)

        pass
