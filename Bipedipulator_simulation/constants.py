"""Constants used through the simulation."""

from pymunk import Vec2d

SCENARIO: int = 1
AMOUNT_SCENARIOS: int = 2

FPS: int = 60
DISPLAY_FLAGS: int = 0
GRAVITY: float = -981.0
ROTATION_RATE: float = 1
START_VELOCITY_VALUE: float = 0.25

CORPS_WEIGHT: int = 50
THIGH_WEIGHT: int = 10
calf_WEIGHT: int = 10
FOOT_WEIGHT: int = 5

BOUNDS_WIDTH: int = 1800
BOUNDS_HEIGHT: int = 1100

CORPS_HEIGHT: float = 150
CORPS_WIDTH: float = 150
THIGH_HEIGHT: float = 440
THIGH_WIDTH: float = 20
CALF_HEIGHT: float = 430
CALF_WIDTH: float = 20
FOOT_HEIGHT: float = 20
FOOT_WIDTH: float = 140
FLOOR_HEIGHT: float = 6

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
        "right": [0.06, 0.08, 0.2, 0.38, 0.57, 0.68,
                  0.74, 0.72, 0.66, 0.63, 0.6, 0.56,
                  0.52, 0.49, 0.49, 0.48, 0.47, 0.45,
                  0.43, 0.38, 0.33, 0.27, 0.2, 0.12, 0.06],

        "left": [0.52, 0.49, 0.49, 0.48, 0.47, 0.45,
                 0.43, 0.38, 0.33, 0.27, 0.2, 0.12,
                 0.06, 0.08, 0.2, 0.38, 0.57, 0.68,
                 0.74, 0.72, 0.66, 0.63, 0.6, 0.56, 0.52]
    },
    2: {
        "right": [0.30, 0.25, 0.20, 0.15, 0.1,
                  0.3, 0.38, 0.41, 0.48,
                  0.55, 0.45, 0.375, 0.30],
        "left": [0.38, 0.41, 0.48, 0.55, 0.45,
                 0.375, 0.30, 0.25, 0.20,
                 0.15, 0.1, 0.3, 0.38]
    },
    3: {
        "right": [0.496880138, 0.333487092, 0.149438132, -0.079914694,
                  0.019998667, 0.479425539, 0.767543502,
                  0.717356091, 0.605186406, 0.581035161,
                  0.522687229, 0.522687229, 0.496880138],
        "left": [0.767543502, 0.717356091, 0.605186406, 0.581035161,
                 0.522687229, 0.522687229, 0.496880138,
                 0.333487092, 0.149438132, -0.079914694,
                 0.019998667, 0.479425539, 0.767543502]
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
        "right": [-0.488, -0.531, -0.572, -0.589, -0.681,
                  -0.724, -0.514, -0.159,
                  -0.129, -0.285, -0.389,
                  -0.443, -0.488, -0.531, -0.572, -0.589, -0.681,
                  -0.724, -0.514, -0.159,
                  -0.129, -0.285, -0.389,
                  -0.443, -0.488],
        "left": [-0.514, -0.159, -0.129, -0.285, -0.389,
                 -0.443, -0.488, -0.531,
                 -0.572, -0.589, -0.681,
                 -0.724, -0.514, -0.159, -0.129, -0.285, -0.389,
                 -0.443, -0.488, -0.531,
                 -0.572, -0.589, -0.681,
                 -0.724, -0.514]
    },
    2: {
        "right": [-0.32, -0.35, -0.4, -0.45, -0.5,
                  -0.55, -0.6, -0.55, -0.35,
                  -0.25, -0.28, -0.3, -0.32],
        "left": [-0.6, -0.55, -0.35, -0.25, -0.28,
                 -0.3, -0.32, -0.35, -0.4,
                 -0.45, -0.5, -0.55, -0.6]
    },
    3: {
        "right": [-0.841, -0.78332691, -0.703279419, -0.605186406,
                  -0.78332691, -0.98544973, -0.948984619,
                  -0.644217687, -0.496880138, -0.703279419,
                  -0.78332691, -0.813415505, -0.841],
        "left": [-0.948984619, -0.644217687, -0.496880138, -0.703279419,
                 -0.78332691, -0.813415505, -0.841,
                 -0.78332691, -0.703279419, -0.605186406,
                 -0.78332691, -0.98544973, -0.948984619]
    }

}

AMOUNT_PHASES: int = len(THIGH_ANGLES_LIST[SCENARIO]["right"]) - 1