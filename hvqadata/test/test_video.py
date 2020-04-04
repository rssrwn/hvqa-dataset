import unittest

from hvqadata.video.video import Video
from hvqadata.video.frame_object import FrameObject
from hvqadata.video.frame import Frame


frames = []
events = []

obj1 = FrameObject(Frame())
obj1.obj_type = "octopus"
obj1.colour = "red"
obj1.position = (10, 100, 20, 110)
obj1.rotation = 3

obj2 = FrameObject(Frame())
obj2.obj_type = "bag"
obj2.colour = "white"
obj2.position = (50, 100, 60, 110)
obj2.rotation = 3

obj3 = FrameObject(Frame())
obj3.obj_type = "rock"
obj3.colour = "blue"
obj3.position = (70, 200, 80, 210)
obj3.rotation = 0

obj4 = FrameObject(Frame())
obj4.obj_type = "fish"
obj4.colour = "silver"
obj4.position = (200, 100, 210, 110)
obj4.rotation = 1

obj5 = FrameObject(Frame())
obj5.obj_type = "bag"
obj5.colour = "white"
obj5.position = (220, 100, 230, 110)
obj5.rotation = 1

obj6 = FrameObject(Frame())
obj6.obj_type = "rock"
obj6.colour = "purple"
obj6.position = (150, 100, 160, 110)
obj6.rotation = 0

obj7 = FrameObject(Frame())
obj7.obj_type = "octopus"
obj7.colour = "blue"
obj7.position = (180, 150, 190, 160)
obj7.rotation = 0

obj8 = FrameObject(Frame())
obj8.obj_type = "bag"
obj8.colour = "white"
obj8.position = (200, 100, 210, 110)
obj8.rotation = 3


class VideoTest(unittest.TestCase):
    def setUp(self):
        self.video = Video()
        self.video.frames = frames
        self.video.events = events

    def test_gen_unique_prop_str_octo(self):
        obj_str = self.video._gen_unique_obj_str(obj1, "class")
        expected = "octopus"
        self.assertEqual(expected, obj_str)

    def test_gen_unique_prop_str_bag(self):
        obj_str = self.video._gen_unique_obj_str(obj2, "class")
        expected = "bag"
        self.assertEqual(expected, obj_str)

    def test_gen_unique_prop_str_rock(self):
        obj_str = self.video._gen_unique_obj_str(obj3, "colour")
        expected = "blue rock"
        self.assertEqual(expected, obj_str)

    def test_gen_unique_prop_str_fish(self):
        obj_str = self.video._gen_unique_obj_str(obj4, "rotation")
        expected = "right-facing fish"
        self.assertEqual(expected, obj_str)

    def test_unique_prop_identifies_class(self):
        prop = self.video._unique_prop(obj1, [obj1, obj2, obj3, obj4])
        expected = "class"
        self.assertEqual(expected, prop)

    def test_unique_prop_identifies_rotation(self):
        prop = self.video._unique_prop(obj2, [obj1, obj2, obj5])
        expected = "rotation"
        self.assertEqual(expected, prop)

    def test_unique_prop_identifies_colour(self):
        prop = self.video._unique_prop(obj3, [obj3, obj6, obj7])
        expected = "colour"
        self.assertEqual(expected, prop)

    def test_unique_prop_identifies_none(self):
        prop = self.video._unique_prop(obj2, [obj2, obj8])
        expected = None
        self.assertEqual(expected, prop)
