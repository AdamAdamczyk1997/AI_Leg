"""Constants used through the simulation."""
from math import sqrt, pow

from pymunk import Vec2d

GRAVITY: float = -981.0
ROTATION_RATE: float = 1

CORPS_WEIGHT: int = 50
THIGH_WEIGHT: int = 10
PATELLA_WEIGHT: int = 1
calf_WEIGHT: int = 10
FOOT_WEIGHT: int = 5

BOUNDS_WIDTH: int = 1800
MAX_X: float = BOUNDS_WIDTH / 2
MIN_X: float = -MAX_X
VIEW_WIDTH: int = BOUNDS_WIDTH + 20

BOUNDS_HEIGHT: int = 1000
MAX_Y: float = BOUNDS_HEIGHT / 2
MIN_Y: float = -MAX_Y
VIEW_HEIGHT: int = BOUNDS_HEIGHT + 20

CONVERTER: float = 0.5
HANDLER_LENGTH: float = 300

CORPS_HEIGHT: float = 150 * CONVERTER
CORPS_WIDTH: float = 150 * CONVERTER

THIGH_HEIGHT: float = 400 * CONVERTER
THIGH_WIDTH: float = 20 * CONVERTER

calf_HEIGHT: float = 300 * CONVERTER
calf_WIDTH: float = 20 * CONVERTER

PATELLA_HEIGHT: float = 10 * CONVERTER
PATELLA_WIDTH: float = 40 * CONVERTER

FOOT_HEIGHT: float = 20 * CONVERTER
FOOT_WIDTH: float = 120 * CONVERTER
FLOOR_HEIGHT: float = 6

LEG_HEIGHT: float = (0.5*CORPS_HEIGHT) + THIGH_HEIGHT + calf_HEIGHT + FOOT_HEIGHT + FLOOR_HEIGHT

CORPS_POSITION = Vec2d(1000, LEG_HEIGHT + 10)

JOINT_RADIUS: float = 20 * CONVERTER

MIN_CORPS_THIGH: float = sqrt(pow(((1 / 2) * CORPS_WIDTH - (2 * JOINT_RADIUS)), 2) + pow((2 * JOINT_RADIUS), 2))
MIN_TCFJ: float = sqrt(pow(THIGH_HEIGHT, 2) + pow(10, 2))
MIN_CFFJ: float = sqrt(pow(calf_HEIGHT, 2) + pow(10, 2))

MIN_CMFJ: float = (sqrt(pow(((1 / 2) * CORPS_WIDTH), 2) + pow((0.25 * THIGH_HEIGHT), 2)))
MIN_CMBJ: float = (sqrt(pow(((1 / 2) * CORPS_WIDTH), 2) + pow((0.25 * THIGH_HEIGHT), 2)))

MIN_PTJ: float = (sqrt(pow(PATELLA_WIDTH, 2) + pow((0.25 * THIGH_HEIGHT) - ((1 / 8) * THIGH_HEIGHT), 2)))
MIN_PCJ: float = (sqrt(pow(PATELLA_WIDTH, 2) + pow((0.25 * calf_HEIGHT) - ((1 / 8) * calf_HEIGHT), 2)))

CELL_RADIUS: float = 15
CELL_COUNT: float = 100
CELL_SPEED: float = 5.0

