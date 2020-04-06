# Helper classes and definitions


# *** Image and video definitions ***

ROTATIONS = [0, 1, 2, 3]

OCTOPUS = (17, 17)
FISH = (9, 11)
BAG = (11, 15)
ROCK = (12, 12)

NUM_FRAMES = 32

FRAME_SIZE = 256
NUM_SEGMENTS = 8
SEGMENT_SIZE = FRAME_SIZE / NUM_SEGMENTS
EDGE = 3
CLOSE_OCTO = 5

ROT_PROB = 0.1
MOVE_PIXELS = 15

NO_EVENT = "nothing"
MOVE_EVENT = "move"
ROTATE_LEFT_EVENT = "rotate-left"
ROTATE_RIGHT_EVENT = "rotate-right"


# *** QA Pairs ***

QS_PER_VIDEO = 10

QUESTION_OBJ_PROPS = ["colour", "rotation"]

ACTIONS = [MOVE_EVENT, ROTATE_LEFT_EVENT, ROTATE_RIGHT_EVENT]


# *** Number of objects ***

MIN_FISH = 5
MAX_FISH = 8

MIN_BAG = 2
MAX_BAG = 3

MIN_ROCK = 3
MAX_ROCK = 4


# *** Colour definitions ***

ROCK_COLOURS = ["brown", "blue", "purple", "green"]
OCTO_COLOUR = "red"
FISH_COLOUR = "silver"
BAG_COLOUR = "white"

BLACK_RGB = (0, 0, 0)

# Background
BACKGROUND_R = 62
BACKGROUND_G = 193
BACKGROUND_B = 179

GREY_RBG = (122, 122, 122)

# Objects
OCTO_RGB = (226, 29, 98)
FISH_RGB = (192, 190, 188)
BAG_RGB = (255, 255, 255)

BROWN_ROCK_RGB = (182, 122, 28)
BLUE_ROCK_RGB = (0, 0, 255)
PURPLE_ROCK_RGB = (182, 37, 218)
GREEN_ROCK_RGB = (0, 255, 0)
