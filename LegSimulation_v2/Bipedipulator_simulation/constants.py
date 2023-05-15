"""Constants used through the simulation."""
from math import sqrt, pow

from pymunk import Vec2d

GRAVITY: float = -981.0
ROTATION_RATE: float = 1

CORPS_WEIGHT: int = 50
THIGH_WEIGHT: int = 10
calf_WEIGHT: int = 10
FOOT_WEIGHT: int = 5

BOUNDS_WIDTH: int = 1800
MAX_X: float = BOUNDS_WIDTH / 2
MIN_X: float = -MAX_X
VIEW_WIDTH: int = BOUNDS_WIDTH + 20

BOUNDS_HEIGHT: int = 1300
MAX_Y: float = BOUNDS_HEIGHT / 2
MIN_Y: float = -MAX_Y
VIEW_HEIGHT: int = BOUNDS_HEIGHT + 20

CONVERTER: float = 0.5
HANDLER_LENGTH: float = 300

CORPS_HEIGHT: float = 150
CORPS_WIDTH: float = 150

THIGH_HEIGHT: float = 440
THIGH_WIDTH: float = 20

CALF_HEIGHT: float = 430
CALF_WIDTH: float = 20

FOOT_HEIGHT: float = 20
FOOT_WIDTH: float = 280 * CONVERTER
FLOOR_HEIGHT: float = 6

LEG_HEIGHT: float = (0.5 * CORPS_HEIGHT) + THIGH_HEIGHT + CALF_HEIGHT + FOOT_HEIGHT + FLOOR_HEIGHT

CORPS_POSITION = Vec2d(1000, LEG_HEIGHT + 10)

JOINT_RADIUS: float = 20 * CONVERTER


def fill_angles_list_v1(leg_name):
    match leg_name:
        case "right":
            thigh_angles_list = [0.30, 0.25, 0.20, 0.15, 0.1,
                                 0.3, 0.38, 0.41, 0.48,
                                 0.55, 0.45, 0.375, 0.30]

            calf_angles_list = [-0.32, -0.35, -0.4, -0.45, -0.5,
                                -0.55, -0.6, -0.55, -0.35,
                                -0.25, -0.28, -0.3, -0.32]
            return [thigh_angles_list, calf_angles_list]
        case "left":
            thigh_angles_list = [0.38, 0.41, 0.48, 0.55, 0.45,
                                 0.375, 0.30, 0.25, 0.20,
                                 0.15, 0.1, 0.3, 0.38]

            calf_angles_list = [-0.6, -0.55, -0.35, -0.25, -0.28,
                                -0.3, -0.32, -0.35, -0.4,
                                -0.45, -0.5, -0.55, -0.6]
            return [thigh_angles_list, calf_angles_list]
        case other:
            print("Equation leg name not specified")


def fill_angles_list_v2(leg_name: str):
    match leg_name:
        case "right":
            thigh_angles_list = [0.452, 0.389, 0.276, 0.119, 0.049,
                                 0.361, 0.628, 0.696,
                                 0.605, 0.556, 0.488,
                                 0.470, 0.452]

            calf_angles_list = [-0.488, -0.531, -0.572, -0.589, -0.681,
                                -0.724, -0.514, -0.159,
                                -0.129, -0.285, -0.389,
                                -0.443, -0.488]
            return [thigh_angles_list, calf_angles_list]
        case "left":
            thigh_angles_list = [0.628, 0.696, 0.605, 0.556, 0.488,
                                 0.470, 0.452, 0.389,
                                 0.276, 0.119, 0.049,
                                 0.361, 0.628]

            calf_angles_list = [-0.514, -0.159, -0.129, -0.285, -0.389,
                                -0.443, -0.488, -0.531,
                                -0.572, -0.589, -0.681,
                                -0.724, -0.514]
            return [thigh_angles_list, calf_angles_list]
        case other:
            print("Equation leg name not specified")


def fill_angles_list_v3(leg_name: str):
    match leg_name:
        case "right":
            thigh_angles_list = [0.496880138, 0.333487092, 0.149438132, -0.079914694,
                                 0.019998667, 0.479425539, 0.767543502,
                                 0.717356091, 0.605186406, 0.581035161,
                                 0.522687229, 0.522687229, 0.496880138]

            calf_angles_list = [-0.841, -0.78332691, -0.703279419, -0.605186406,
                                -0.78332691, -0.98544973, -0.948984619,
                                -0.644217687, -0.496880138, -0.703279419,
                                -0.78332691, -0.813415505, -0.841]
            return [thigh_angles_list, calf_angles_list]
        case "left":
            thigh_angles_list = [0.767543502, 0.717356091, 0.605186406, 0.581035161,
                                 0.522687229, 0.522687229, 0.496880138,
                                 0.333487092, 0.149438132, -0.079914694,
                                 0.019998667, 0.479425539, 0.767543502]

            calf_angles_list = [-0.948984619, -0.644217687, -0.496880138, -0.703279419,
                                -0.78332691, -0.813415505, -0.841,
                                -0.78332691, -0.703279419, -0.605186406,
                                -0.78332691, -0.98544973, -0.948984619]
            return [thigh_angles_list, calf_angles_list]
        case other:
            print("Equation leg name not specified")
