import random

from hvqadata.video.frame import Frame
from hvqadata.util.definitions import *


class Video:

    def __init__(self):
        self.frames = []
        self.events = []
        self.questions = []
        self.answers = []
        self.q_idxs = []
        self._question_funcs = [
            self._gen_prop_question
        ]

    def random_video(self):
        initial = Frame()
        initial.random_frame()
        self.frames.append(initial)

        curr = initial
        for frame in range(1, NUM_FRAMES):
            curr, events = curr.move()
            self.frames.append(curr)
            self.events.append(events)

        questions, answers, idxs = self._gen_qa_pairs()
        self.questions = questions
        self.answers = answers
        self.q_idxs = idxs

    def _gen_qa_pairs(self):
        questions = []
        answers = []
        idxs = []
        for q_idx in range(QS_PER_VIDEO):
            func_idx = random.randint(0, len(self._question_funcs) - 1)
            q_func = self._question_funcs[func_idx]
            question, answer = q_func()
            questions.append(question)
            answers.append(answer)
            idxs.append(q_idx)

        return questions, answers, idxs

    def _gen_prop_question(self):
        """
        Generate question asking about a property of an object for a single frame
        Q: What <property> was the <object> in frame <frame_idx>?
        A: <property_val>

        :return: (question: str, answer: str)
        """

        frame_idx = random.randint(0, NUM_FRAMES - 1)
        frame = self.frames[frame_idx]

        # Find obj for question
        # If no unique obj exists, use first frame which is guaranteed to contain octopus
        obj = self._find_unique_obj(frame)
        if obj is None:
            obj = self._find_unique_obj(self.frames[0])

        assert obj is not None, "Cannot find unique object in the first frame of the video"

        # If class uniquely identifies obj leave additional identifier blank
        # Otherwise use value of additional identifier
        obj, unique_prop = obj
        obj_str = self._gen_unique_obj_str(obj, unique_prop)

        # Get the property value (the answer)
        props = QUESTION_OBJ_PROPS[:]
        if unique_prop != "class":
            props.remove(unique_prop)

        idx = random.randint(0, len(props) - 1)
        prop = props[idx]
        prop_val = obj.get_prop_val(prop)

        question = f"What {prop} was the {obj_str} in frame {str(frame_idx)}"
        answer = str(prop_val)

        return question, answer
    
    # def _gen_relations_question(self):
    #     """
    #     Generate question asking about a relation between two objects in a single frame
    #     Q: Was the <object> <relation> to the <object> in frame <frame idx>?
    #     A: yes/no
    #
    #     :return: (question: str, answer: str)
    #     """
    #
    #     frame_idx = random.randint(0, NUM_FRAMES - 1)
    #     frame = self.frames[frame_idx]
    #
    #     # Find objects which are unique in the frame
    #     objs = frame.get_objects()
    #     unique_objs = []
    #     for obj in objs:
    #         prop = self._unique_prop(obj, objs)
    #         if prop is not None:
    #             obj_str = self._gen_unique_obj_str(obj, prop)
    #             unique_objs.append((obj, obj_str))
    #
    #

    def _find_unique_obj(self, frame):
        """
        Find an object which is uniquely identified in the frame
        Return FrameObject and a property which uniquely identifies the object
        Return None if not possible

        :param frame: FrameObject
        :return: (FrameObject: obj, property: str)
        """

        objs = frame.get_objects()
        classes = list(set([obj.obj_type for obj in objs]))
        random.shuffle(classes)

        unique_obj = None
        prop = None

        for cls in classes:
            cls_objs = [obj for obj in objs if obj.obj_type == cls]
            random.shuffle(cls_objs)
            for obj in cls_objs:
                prop = self._unique_prop(obj, cls_objs)
                if prop is not None:
                    unique_obj = obj
                    break

            if unique_obj is not None:
                break

        if unique_obj is None:
            return None

        return unique_obj, prop

    @staticmethod
    def _unique_prop(obj, objs):
        """
        Find name of property which uniquely identifies <obj> within <objs>
        Return None if none exist

        :param obj: FrameObject
        :param objs: List of FrameObjects
        :return: Name of property (could be None)
        """

        unique_colour = True
        unique_rotation = True
        unique_class = True
        for obj_ in objs:
            if obj.position != obj_.position:
                if obj.colour == obj_.colour:
                    unique_colour = False
                if obj.rotation == obj_.rotation:
                    unique_rotation = False
                if obj.obj_type == obj_.obj_type:
                    unique_class = False

            if not (unique_colour or unique_rotation or unique_class):
                break

        if unique_class:
            return "class"

        unique_props = []
        if unique_colour:
            unique_props.append("colour")
        if unique_rotation:
            unique_props.append("rotation")

        num_props = len(unique_props)
        if num_props > 1:
            idx = random.randint(0, num_props - 1)
            return unique_props[idx]
        elif num_props == 1:
            return unique_props[0]

        return None

    @staticmethod
    def _gen_unique_obj_str(obj, prop):
        unique_prop_val = ""
        if prop != "class":
            unique_prop_val = str(obj.get_prop_val(prop))
            if prop == "rotation":
                if unique_prop_val == 0:
                    unique_prop_val = "upward-facing"
                elif unique_prop_val == 1:
                    unique_prop_val = "right-facing"
                elif unique_prop_val == 2:
                    unique_prop_val = "downward-facing"
                elif unique_prop_val == 3:
                    unique_prop_val = "left-facing"

        obj_str = f"{unique_prop_val} {obj.obj_type}"
        return obj_str

    def to_dict(self):
        return {
            "frames": [frame.to_dict() for frame in self.frames],
            "events": self.events,
            "questions": self.questions,
            "answers": self.answers,
            "question_types": self.q_idxs
        }
