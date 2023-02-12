import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy import matrix

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
               'y_ankle', 'x_foot', 'y_foot', 'angle_foot', 'real_corps_y',
               'oscillation', 'oscillation_time', 'hip_velocity', 'knee_velocity', 'ankle_velocity',
               'current_thigh_velocity_value', 'current_cale_velocity_value']

    usage_counter = []
    x_hip = []
    y_hip = []
    angle_thigh = []
    x_knee = []
    y_knee = []
    angle_cale = []
    x_ankle = []
    y_ankle = []
    x_foot = []
    y_foot = []
    angle_foot = []
    real_corps_y = []
    oscillation = []
    knee_velocity = []
    hip_velocity = []
    ankle_velocity = []
    current_thigh_velocity_value = []
    current_cale_velocity_value = []
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
        x_foot.append(leg.relative_values.histories[i][9])
        y_foot.append(leg.relative_values.histories[i][10])
        angle_foot.append(leg.relative_values.histories[i][11])
        real_corps_y.append(model.corps.body.position.y)
        oscillation.append(leg.relative_values.histories[i][12])
        knee_velocity.append(leg.relative_values.histories[i][13])
        hip_velocity.append(leg.relative_values.histories[i][14])
        ankle_velocity.append(leg.relative_values.histories[i][15])
        current_thigh_velocity_value.append(leg.relative_values.histories[i][16])
        current_cale_velocity_value.append(leg.relative_values.histories[i][17])

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
                oscillation_time.append((((last_phase_move_value - previous_phase_value) / moves_counter_for_phase) * i)
                                        + previous_phase_value + total_value)

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

    df = pd.DataFrame(list(zip(x_hip, y_hip, angle_thigh, x_knee, y_knee, angle_cale, x_ankle, y_ankle,
                               x_foot, y_foot, angle_foot, real_corps_y, oscillation,
                               oscillation_time, hip_velocity, knee_velocity, ankle_velocity,
                               current_thigh_velocity_value, current_cale_velocity_value)),
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

# class GeneticAlgorithm:
#
#
#
#
#     void
#     solution::fit_fun(matrix * ud, matrix * ad)
#     {
#         ++f_calls;
#     int
#     N = 1001;
#     static
#     matrix
#     X(N, 2);
#     if (solution::f_calls == 1)
#         {
#             ifstream
#         S("polozenia.txt");
#         S >> X;
#         S.close();
#         }
#
#         matrix
#         Y0(4, 1);
#         matrix * Y = solve_ode(0, 0.1, 100, Y0, & x);
#         y = 0;
#         for (int i = 0; i < N; ++i) {
#             y = y + abs(X(i, 0) - Y[1](i, 0)) + abs(X(i, 1) - Y[1](i, 2));
#         }
#         if (ud) {
#         ( * ud)(0, 0) = Y[1](0, 0);
#         ( * ud)(0, 1) = Y[1](0, 2);
#         for (int i = 1; i < N; ++i) {
#         ( * ud).add_row();
#         ( * ud)(i, 0) = Y[1](i, 0);
#         ( * ud)(i, 1) = Y[1](i, 2);
#         }
#         }
#         y = y / (2 * N);
#
#         # endif
#     }
#
# def hess(ud: Matrix, ad: Matrix):
#     ++H_calls;
#
# solution::solution(double L)
# {
#     x = L;
#     g = NAN;
#     H = NAN;
#     y = NAN;
# }
#
# def solution(a: matrix):
#     x = a
#     g = not.
#     H = NAN
#     y = NAN
#
#
# solution::solution(int n, double* A)
# {
#     x = matrix(n, A);
#     g = NAN;
#     H = NAN;
#     y = NAN;
# }
#
# int get_dim(const solution& A)
# {
#     return get_len(A.x);
# }
#
# void solution::clear_calls()
# {
#     f_calls = 0;
#     g_calls = 0;
#     H_calls = 0;
# }
#
# ostream& operator<<(ostream& S, const solution& A)
# {
#     S << "x = " << A.x << endl;
#     S << "y = " << A.y << endl;
#     S << "f_calls = " << solution::f_calls << endl;
#     if (solution::g_calls > 0)
#         S << "g_calls = " << solution::g_calls << endl;
#     if (solution::H_calls)
#         S << "H_calls = " << solution::H_calls << endl;
#     return S;
# }
#
# class Matrix:
# 	int n, m;
# 	double **M;
# 	friend int *get_size(const matrix &);
# 	friend int get_len(const matrix &); // throw (char*);
#
# 	matrix(double = 0.0);
# 	matrix(int, int, double = 0.0); // throw (char*);
# 	matrix(int, double *); // throw (char*);
# 	matrix(int, int, double **); // throw (char*);
# 	matrix(const matrix &);
# 	~matrix();
# 	matrix &operator=(const matrix &);
# 	matrix operator[](int) const; // throw (char*);
# 	double &operator()(int = 0, int = 0); // throw (char*);
# 	double &operator()(int = 0, int = 0) const; // throw (char*);
# 	void set_col(const matrix &, int); // throw (char*);
# 	void set_row(const matrix &, int); // throw (char*);
# 	void add_col(double = 0.0);
# 	void add_row(double = 0.0);
# 	void add_col(const matrix &); // throw (char*);
# 	void add_row(const matrix &); // throw (char*);
