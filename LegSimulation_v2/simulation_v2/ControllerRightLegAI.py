from LegSimulation_v2.simulation_v2.Leg import Leg
from LegSimulation_v2.simulation_v2.LegMotorController import Controller
from matplotlib import pyplot as plt

import pandas as pd

import matplotlib.pyplot as plt
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

    the_same_counter = 0
    oscillation_value_amount_temp = 0
    j = 0
    m = 1
    for r in oscillation:
        j += 1

    print("j =", j)
    while m < j - 1:
        if oscillation[m] == oscillation[m - 1]:
            the_same_counter += 1
        else:
            i = 0
            print("oscillation_value_amount_temp =", oscillation_value_amount_temp)
            print("the_same_counter =", the_same_counter)
            print("m =", m)
            while i <= the_same_counter:
                val = oscillation.__getitem__(m - 1)
                if the_same_counter == 0:
                    oscillation_time.append((val * i))
                else:
                    oscillation_time.append(((val / the_same_counter) * i))
                i += 1

            if oscillation_value_amount_temp < 6:
                oscillation_value_amount_temp += 1
            else:
                oscillation_value_amount_temp = 1
            the_same_counter = 0
        m += 1

    print("m =", m)
    while oscillation_time.__len__() != j:
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

        df = pd.DataFrame(data)
        # plt.plot(df)
        # plt.hist(df)
        # plt.show()

        print(df)

        pass
