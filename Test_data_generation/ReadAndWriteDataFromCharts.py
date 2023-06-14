from __future__ import annotations

import cv2
import matplotlib.pyplot as plt


def read_data(img, array):
    for i in range(0, img.shape[0]):
        col = []
        for j in range(0, img.shape[1]):
            blue, red, green = (img[i, j])
            if blue == 0:
                col.append(1)
            else:
                col.append(0)
        array.append(col)
    pass


def write_data_to_txt(array: list, part_name: str):
    # write 0 and 1 to file.txt
    name = part_name + '_read_values.txt'
    with open(name, 'w') as f:
        f.write(str(array))
    pass


def calibration_data(img, leg_part: str):
    # dane do kalibracji
    height_scale_radians = 100
    pixel_height = int(img.shape[0])
    match leg_part:
        case 'hip':
            width_scale_time = 31
        case 'knee':
            width_scale_time = 30  # z powodu różnej wielkości próbek

    pixel_width = int(img.shape[1])
    width_scale = round((width_scale_time / pixel_width), 2)
    height_scale = round((height_scale_radians / pixel_height), 2)
    data = {
        'scale_for_height': height_scale,
        'scale_for_width': width_scale
    }

    return data


def make_exact_data_chart(img, img_array, cal_data: dict, numb_rows_cols: list, leg_part: str):
    start_column_point = 5
    stop_column_point = numb_rows_cols[1]
    start_rows_point = 10
    stop_rows_point = numb_rows_cols[0] - 10
    match leg_part:
        case 'hip':
            start_point_radians = 0
            occur_time = 9.56
        case 'knee':
            start_point_radians = 1.4
            occur_time = 7.27

    angle_values = []
    time_values = []
    occurs_col = []
    occurs = []

    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if start_rows_point < i < stop_rows_point and start_column_point < j < stop_column_point:
                if img_array[i][j] == 1:
                    angle_value = round(start_point_radians - i * cal_data['scale_for_height'] * 0.01, 3)
                    angle_values.append(angle_value)
                    time_value = round(j * cal_data['scale_for_width'] - occur_time, 2)
                    time_values.append(time_value)
                    if time_value not in occurs_col:
                        occurs_col.append(time_value)
                        occurs.append([int(time_value), angle_value])

    generate_charts(time_values, angle_values, leg_part + "_exact")

    return occurs


def make_real_data_chart(occurs, leg_part: str):
    sort_occurs = occurs.copy()
    sort_occurs.sort(key=lambda x: x[0])

    angles_list = []
    time_values = []
    for i in range(0, sort_occurs.__len__()):
        time_value = sort_occurs[i][0]
        angle = sort_occurs[i][1]
        if time_value not in time_values:
            time_values.append(time_value)
            angles_list.append(angle)

    print(leg_part + ": Real time values =", time_values)
    print(leg_part + ": Real angles values =", angles_list)

    return angles_list


def generate_charts(x_data, y_data, leg_part: str):
    chart_name = leg_part + "_flexion_chart_generated"
    file_name = chart_name + ".png"
    plt.scatter(x_data, y_data)
    plt.title(chart_name)
    plt.savefig(file_name)
    plt.close('all')
    pass


def customize_data(hip, knee):
    hip_flexion = [(x * -1) for x in hip]
    knee_f = [(x * -1) for x in knee]
    knee_flexion = []
    for j in range(0, knee_f.__len__()):
        data = round(knee_f[j] + hip_flexion[j], 3)
        knee_flexion.append(data)

    time = []
    for i in range(0, hip_flexion.__len__()):
        time.append(i)

    print("hip_flexion =", hip_flexion)
    generate_charts(time, hip_flexion, "hip_customize_data")
    write_data_to_txt(hip_flexion, "hip_customize")
    print("knee_flexion =", knee_flexion)
    generate_charts(time, knee_flexion, "knee_customize_data")
    write_data_to_txt(knee_flexion, "knee_customize")

    pass


def print_image_shape(img, joint_type):
    numb_rows = img.shape[0]
    numb_cols = img.shape[1]
    print(f"{joint_type.capitalize()}: no. rows: {numb_rows}. no. Columns: {numb_cols}")

    return [numb_rows, numb_cols]


def process_image(joint_type: str):
    img = cv2.imread(joint_type + ".png")
    numb_rows_cols = print_image_shape(img, joint_type)

    img_list = []
    read_data(img, img_list)
    write_data_to_txt(img_list, joint_type + "_list")

    data = calibration_data(img, joint_type)
    gen_data = make_exact_data_chart(img, img_list, data, numb_rows_cols, joint_type)
    gen_data_per_phase = make_real_data_chart(gen_data, joint_type)

    return gen_data_per_phase


def main():
    hip_gen_data_per_phase = process_image("hip")
    knee_gen_data_per_phase = process_image("knee")
    customize_data(hip_gen_data_per_phase, knee_gen_data_per_phase)


if __name__ == "__main__":
    main()
