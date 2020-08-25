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
ROTATE_LEFT_EVENT = "rotate anti-clockwise"
ROTATE_RIGHT_EVENT = "rotate clockwise"

EAT_FISH_EVENT = "eat a fish"
EAT_BAG_EVENT = "eat a bag"
COLOUR_CHANGE_EVENT = "change colour from {from_colour} to {to_colour}"
CHANGE_COLOUR_LENGTH = 13


# *** QA Pairs ***

QS_PER_VIDEO = 50

QUESTION_OBJ_PROPS = ["colour", "rotation"]

ACTIONS = [MOVE_EVENT, ROTATE_LEFT_EVENT, ROTATE_RIGHT_EVENT]
EVENTS = [MOVE_EVENT, ROTATE_LEFT_EVENT, ROTATE_RIGHT_EVENT, EAT_FISH_EVENT, EAT_BAG_EVENT, "change colour", NO_EVENT]

MAX_OCCURRENCE = 5
OCCURRENCES = {
    1: "first time",
    2: "second time",
    3: "third time",
    4: "fourth time",
    5: "fifth time"
}

EVENTS_TO_NOUN = {
    MOVE_EVENT: "moving",
    ROTATE_LEFT_EVENT: "rotating left",
    ROTATE_RIGHT_EVENT: "rotating right",
    EAT_FISH_EVENT: "eating a fish",
    EAT_BAG_EVENT: "eating a bag",
    "change colour": "changing colour"
}


# *** Number of objects ***

MIN_FISH = 5
MAX_FISH = 7

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
