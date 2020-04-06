import random

from hvqadata.util.definitions import *
from hvqadata.util.exceptions import *


class FrameObject:

    def __init__(self, frame):
        self.frame = frame
        self.obj_type = None
        self.position = None
        self.colour = None
        self.rotation = None

    def to_dict(self):
        return {
            "position": self.position,
            "class": self.obj_type,
            "colour": self.colour,
            "rotation": self.rotation
        }

    def get_prop_val(self, prop_str):
        if prop_str == "class":
            return self.obj_type
        elif prop_str == "position":
            return self.position
        elif prop_str == "colour":
            return self.colour
        elif prop_str == "rotation":
            return self.rotation
        else:
            raise UnknownPropertyException(f"Unknown property {prop_str}")

    def random_obj(self, obj_type):
        """
        Create random object of type <obj_type>

        :param obj_type: String of type of object to be initialised
        """

        if obj_type == "octopus":
            self._init_octopus()
        elif obj_type == "fish":
            self._init_fish()
        elif obj_type == "bag":
            self._init_bag()
        elif obj_type == "rock":
            self._init_rock()
        else:
            raise UnknownObjectTypeException()

    def _init_octopus(self):
        rot = random.choice(ROTATIONS)
        box = self.frame.obj_box(OCTOPUS, rot)
        self.obj_type = "octopus"
        self.position = box
        self.colour = OCTO_COLOUR
        self.rotation = rot

    def _init_fish(self):
        rot = random.choice(ROTATIONS)
        box = self.frame.obj_box(FISH, rot)
        self.obj_type = "fish"
        self.position = box
        self.colour = FISH_COLOUR
        self.rotation = rot

    def _init_bag(self):
        rot = random.choice(ROTATIONS)
        box = self.frame.obj_box(BAG, rot)
        self.obj_type = "bag"
        self.position = box
        self.colour = BAG_COLOUR
        self.rotation = rot

    def _init_rock(self):
        rot = 0
        colour = random.choice(ROCK_COLOURS)
        box = self.frame.obj_box(ROCK, rot)
        self.obj_type = "rock"
        self.position = box
        self.colour = colour
        self.rotation = rot

    def rotate(self):
        """
        Rotate the object left or right with equal probability
        Note: We assume the octopus is square

        :return: Event (rotate_left or rotate_right) (str)
        """

        rand = random.random()
        if rand < 0.5:
            self._rotate_left()
            event = ROTATE_LEFT_EVENT
        else:
            self._rotate_right()
            event = ROTATE_RIGHT_EVENT

        return event

    def _rotate_left(self):
        self.rotation -= 1
        if self.rotation == -1:
            self.rotation = 3

    def _rotate_right(self):
        self.rotation += 1
        if self.rotation == 4:
            self.rotation = 0

    def move(self, move_pixels, frame_size):
        """
        Move the octopus forward (in direction of rotation)
        Note: If the octopus cannot be moved (as it is too close to the edge) it will rotate instead

        :param move_pixels: Number of pixels the octopus is moved by
        :param frame_size: Max length of frame
        :return: Event which occurred (only 'move' or 'rotate')
        """

        x1, y1, x2, y2 = self.position
        if self.rotation == 0:
            y1 -= move_pixels
            y2 -= move_pixels
        elif self.rotation == 1:
            x1 += move_pixels
            x2 += move_pixels
        elif self.rotation == 2:
            y1 += move_pixels
            y2 += move_pixels
        elif self.rotation == 3:
            x1 -= move_pixels
            x2 -= move_pixels

        max_pixel = frame_size - EDGE
        if (0 <= x1 < max_pixel) and (0 <= x2 < max_pixel) and (0 <= y1 < max_pixel) and (0 <= y2 < max_pixel):
            self.position = [x1, y1, x2, y2]
            event = MOVE_EVENT
        else:
            event = self.rotate()

        return event

    def copy(self, frame):
        copy = FrameObject(frame)
        copy.obj_type = self.obj_type
        copy.position = self.position
        copy.colour = self.colour
        copy.rotation = self.rotation
        return copy
