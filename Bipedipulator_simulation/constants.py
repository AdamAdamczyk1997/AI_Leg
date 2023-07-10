"""Constants used through the simulation."""

from pymunk import Vec2d

SCENARIO: int = 1_1
NUMBER_SIMULATION_STEPS: int = 3

FPS: int = 60
DISPLAY_FLAGS: int = 0
GRAVITY: float = -981.0
BOUNDS_WIDTH: int = 1800
BOUNDS_HEIGHT: int = 1100

ROTATION_RATE: float = 1
BASE_ANGULAR_VELOCITY_VALUE: float = 0.25

CORPS_WEIGHT: int = 50
THIGH_WEIGHT: int = 10
CALF_WEIGHT: int = 10
FOOT_WEIGHT: int = 5

CORPS_HEIGHT: float = 150
CORPS_WIDTH: float = 150
THIGH_HEIGHT: float = 440
THIGH_WIDTH: float = 20
CALF_HEIGHT: float = 430
CALF_WIDTH: float = 20
FOOT_HEIGHT: float = 20
FOOT_WIDTH: float = 140

FLOOR_HEIGHT: float = 6
FLOOR_LENGTH: float = 100000
FLOOR_VELOCITY: float = -65

LEG_HEIGHT: float = (0.5 * CORPS_HEIGHT) + THIGH_HEIGHT + CALF_HEIGHT + FOOT_HEIGHT + FLOOR_HEIGHT
CORPS_POSITION = Vec2d(1000, LEG_HEIGHT + 10)
THIGH_ANGLES_LIST: dict = {
    1: {
        "right": [0.452, 0.389, 0.276, 0.119, 0.049,
                  0.361, 0.628, 0.696,
                  0.605, 0.556, 0.488,
                  0.470, 0.452],
        "left": [0.628, 0.696, 0.605, 0.556, 0.488,
                 0.470, 0.452, 0.389,
                 0.276, 0.119, 0.049,
                 0.361, 0.628]
    },
    1_1: {
        "right": [0.06, 0.2, 0.476, 0.683,
                  0.66, 0.616, 0.543, 0.495,
                  0.478, 0.462, 0.426, 0.352,
                  0.232, 0.122, 0.058],
        "left": [0.495, 0.478, 0.462, 0.426,
                 0.352, 0.232, 0.122, 0.058,
                 0.2, 0.476, 0.683, 0.66,
                 0.616, 0.543, 0.495]
    },
    2: {
        "right": [0.30, 0.25, 0.20, 0.15, 0.1,
                  0.3, 0.38, 0.41, 0.48,
                  0.55, 0.45, 0.375, 0.30],
        "left": [0.38, 0.41, 0.48, 0.55, 0.45,
                 0.375, 0.30, 0.25, 0.20,
                 0.15, 0.1, 0.3, 0.38]
    }
}
CALF_ANGLES_LIST: dict = {
    1: {
        "right": [-0.488, -0.531, -0.572, -0.589, -0.681,
                  -0.724, -0.514, -0.159,
                  -0.129, -0.285, -0.389,
                  -0.443, -0.488],
        "left": [-0.514, -0.159, -0.129, -0.285, -0.389,
                 -0.443, -0.488, -0.531,
                 -0.572, -0.589, -0.681,
                 -0.724, -0.514]
    },
    1_1: {
        "right": [-1.101, -1.2, -0.931, -0.393,
                  -0.179, -0.236, -0.317, -0.413,
                  -0.482, -0.499, -0.485, -0.473,
                  -0.464, -0.763, -1.101],
        "left": [-0.413, -0.482, -0.499, -0.485,
                 -0.473, -0.464, -0.763, -1.101,
                 -1.199, -0.931, -0.393, -0.179,
                 -0.236, -0.317, -0.413]
    },
    2: {
        "right": [-0.32, -0.35, -0.4, -0.45, -0.5,
                  -0.55, -0.6, -0.55, -0.35,
                  -0.25, -0.28, -0.3, -0.32],
        "left": [-0.6, -0.55, -0.35, -0.25, -0.28,
                 -0.3, -0.32, -0.35, -0.4,
                 -0.45, -0.5, -0.55, -0.6]
    }
}

AMOUNT_PHASES: int = len(THIGH_ANGLES_LIST[SCENARIO]["right"]) - 1
