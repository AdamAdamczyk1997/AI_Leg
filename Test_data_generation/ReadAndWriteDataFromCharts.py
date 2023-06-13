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


def write_data_to_txt(array: list, leg_part: str):
    # write 0 and 1 to file.txt
    name = leg_part + '_read_values.txt'
    with open(name, 'w') as f:
        f.write(str(array))
    pass


def calibration_data(img, leg_part: str):
    # dane do kalibracji
    wysRadSkala = 100
    wysPixSkala = int(img.shape[0])
    szerCzasSkala = 30
    szerPixSkala = int(img.shape[1])
    szSkala = round((szerCzasSkala / szerPixSkala), 2)
    wysSkala = round((wysRadSkala / wysPixSkala), 2)
    data = {
        'scale_for_height': wysSkala,
        'scale_for_width': szSkala
    }

    print("Jeden pixel w osi czasu (szerokość) dla" + leg_part + ": ", szSkala)
    print("Jeden pixel w osi amplitudy (wysokość) dla" + leg_part + ": ", wysSkala)
    return data


def make_exact_data_chart(img, img_array, calibration_data: dict, leg_part: str):
    match leg_part:
        case 'hip':
            start_column_point = 5
            start_rows_point = 5
            start_point_radians = 0
            occur_time = 10
        case 'knee':
            start_column_point = 20
            start_rows_point = 5
            start_point_radians = 1.4
            occur_time = 8

    angle_values = []
    time_values = []
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if start_rows_point < i < 400 and start_column_point < j < 100:
                if img_array[i][j] == 1:
                    angle_values.append(round(start_point_radians - i * calibration_data['scale_for_height'] * 0.01, 3))
                    time_values.append(j * calibration_data['scale_for_width'] - occur_time)

    print(leg_part + ": Długość wspolzedneX= ", angle_values.__len__())
    print(leg_part + ": Długość wspolzedneY= ", time_values.__len__())
    generate_charts(time_values, angle_values, leg_part)


def generate_charts(y_data, x_data, leg_part: str):
    chart_name = leg_part + "_flexion_chart_generated"
    file_name = chart_name + ".png"
    plt.scatter(y_data, x_data)
    plt.title(chart_name)
    plt.savefig(file_name)
    plt.close('all')
    pass


def customize_data():
    pass


def main():
    print("Start program")
    img_hip = cv2.imread("hip.png")
    img_knee = cv2.imread('knee.png')

    print(img_hip.shape)
    print("Hip - Rows: ", img_hip.shape[0], ". Columns: ", img_hip.shape[1])
    print(img_knee.shape)
    print("Hip - Rows: ", img_knee.shape[0], ". Columns: ", img_knee.shape[1])

    hip_img_array = []
    knee_img_array = []

    read_data(img_hip, hip_img_array)
    write_data_to_txt(hip_img_array, "hip_flexion")
    read_data(img_knee, knee_img_array)
    write_data_to_txt(knee_img_array, "knee_flexion")

    hip_calibration_data = calibration_data(img_hip, "hip")
    knee_calibration_data = calibration_data(img_knee, "knee")

    make_exact_data_chart(img_hip, hip_img_array, hip_calibration_data, "hip")
    make_exact_data_chart(img_knee, knee_img_array, knee_calibration_data, "knee")


if __name__ == "__main__":
    main()
