"""Constants used through the simulation."""
from math import sqrt, pow

BOUNDS_WIDTH: int = 2000
MAX_X: float = BOUNDS_WIDTH / 2
MIN_X: float = -MAX_X
VIEW_WIDTH: int = BOUNDS_WIDTH + 20

BOUNDS_HEIGHT: int = 1200
MAX_Y: float = BOUNDS_HEIGHT / 2
MIN_Y: float = -MAX_Y
VIEW_HEIGHT: int = BOUNDS_HEIGHT + 20

CONVERTER: float = 0.5

CORPS_HEIGHT: float = 150*CONVERTER
CORPS_WIDTH: float = 300*CONVERTER

THIGH_HEIGHT: float = 400*CONVERTER
THIGH_WIDTH: float = 50*CONVERTER

CALE_HEIGHT: float = 300*CONVERTER
CALE_WIDTH: float = 50*CONVERTER

FOOT_HEIGHT: float = 30*CONVERTER
FOOT_WIDTH: float = 200*CONVERTER

JOINT_RADIUS: float = 50*CONVERTER

MIN_CORPS_THIGH: float = sqrt(pow(((1 / 2) * CORPS_WIDTH - (2 * JOINT_RADIUS)), 2) + pow((2 * JOINT_RADIUS), 2))
MIN_CTBJ: float = sqrt(pow(((1/2)*CORPS_WIDTH- (2*JOINT_RADIUS)), 2) + pow((2 * JOINT_RADIUS), 2))

MIN_CMFJ: float = sqrt(pow(((1/2)*CORPS_WIDTH-((1/2)*CALE_WIDTH)), 2) + pow(JOINT_RADIUS*4 + THIGH_HEIGHT + ((1/3)*CALE_HEIGHT), 2))
MIN_CMBJ: float = sqrt(pow(((1/2)*CORPS_WIDTH-((1/2)*CALE_WIDTH)), 2) + pow(JOINT_RADIUS*4 + THIGH_HEIGHT + ((1/3)*CALE_HEIGHT), 2))



CELL_RADIUS: float = 15
CELL_COUNT: float = 100
CELL_SPEED: float = 5.0

GRAVITY: float = -900.0
