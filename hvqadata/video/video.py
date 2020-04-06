import random

from hvqadata.video.frame import Frame
from hvqadata.util.definitions import *
from hvqadata.util.func import close_to, append_in_dict_, format_rotation_value, increment_in_map_


class Video:

    def __init__(self):
        self.frames = []
        self.events = []
        self.questions = []
        self.answers = []
        self.q_idxs = []
        self._question_funcs = [
            # self._gen_prop_question,
            # self._gen_relations_question,
            self._gen_events_question,
            # self._gen_prop_changed_question,
            # self._gen_repetition_count_question,
            # self._gen_repeating_action_question,
            self._gen_state_transition_question
        ]
        self._relations = [
            (close_to, "close to")
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
            qa_pair = None
            func_idx = None
            func_idxs = list(range(len(self._question_funcs)))
            random.shuffle(func_idxs)
            for func_idx in func_idxs:
                q_func = self._question_funcs[func_idx]
                qa_pair = q_func()
                if qa_pair is not None:
                    break

            assert qa_pair is not None, "Could not find a question for video"

            question, answer = qa_pair
            questions.append(question)
            answers.append(answer)
            idxs.append(func_idx)

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

        # If this question fails, try another question
        if obj is None:
            return None

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

        question = f"What {prop} was the {obj_str} in frame {str(frame_idx)}?"
        answer = str(prop_val)

        return question, answer

    def _gen_relations_question(self):
        """
        Generate question asking about a relation between two objects in a single frame
        Q: Was the <object> <relation> to the <object> in frame <frame idx>?
        A: yes/no

        :return: (question: str, answer: str)
        """

        # Randomly select a (un)relation to use
        rel_q_prob = 0.75
        rel_q = random.random() < rel_q_prob
        idx = random.randint(0, len(self._relations) - 1)
        rel_func, rel_str = self._relations[idx]

        frame_idxs = list(range(NUM_FRAMES))
        random.shuffle(frame_idxs)

        frame_idx = None
        rels = None

        # Attempt to sample a question from each frame randomly
        for frame_idx in frame_idxs:
            frame = self.frames[frame_idx]
            unique_objs = self._find_unique_objs(frame)
            related_objs, unrelated_objs = self._find_related_objs(unique_objs, rel_func)
            if rel_q:
                if len(related_objs) > 0:
                    rels = related_objs
                    break
            else:
                if len(unrelated_objs) > 0:
                    rels = unrelated_objs
                    break

        # If cannot find required relation use unrelated on a random frame (with closeness relation)
        if rels is None:
            rel_q = False
            frame_idx = random.randint(0, NUM_FRAMES - 1)
            frame = self.frames[frame_idx]
            unique_objs = self._find_unique_objs(frame)
            _, rels = self._find_related_objs(unique_objs, close_to)

        # If this question fails, try another question
        if len(rels) == 0:
            return None

        rel_idx = random.randint(0, len(rels) - 1)
        rel = rels[rel_idx]
        obj1_str, obj2_str = rel

        question = f"Was the {obj1_str} {rel_str} the {obj2_str} in frame {frame_idx}?"
        answer = "yes" if rel_q else "no"

        return question, answer

    def _gen_events_question(self):
        """
        Generate a question which asks about which action occurred
        Q: Which action occurred immediately after frame <frame_idx>?
        A: move/rotate left/rotate right

        :return: (question: str, answer: str)
        """

        actions = {}
        for idx, events in enumerate(self.events):
            events = [event for event in events if event in ACTIONS]

            assert len(events) <= 1, f"Multiple actions in a single frame: {events}"

            if len(events) == 1:
                append_in_dict_(actions, events[0], idx)

        action_set = list(actions.keys())
        idx = random.randint(0, len(action_set) - 1)
        action = action_set[idx]
        frame_idxs = actions[action]
        idx = random.randint(0, len(frame_idxs) - 1)
        frame_idx = frame_idxs[idx]

        question = f"Which action occurred immediately after frame {frame_idx}?"
        answer = action

        return question, answer

    def _gen_prop_changed_question(self):
        """
        Generate a question about which property of an object changed (and what it changed to)
        Note: The object will always be an octopus
        Q: What happened to the <object> immediately after <frame_idx>?
        A: Its rotation/colour changed from <property value> to <property value>

        :return: (question: str, answer: str)
        """

        obj = self.frames[0].octopus
        obj_str = self._gen_unique_obj_str(obj, "class")
        colour = obj.colour
        rotation = obj.rotation

        deltas = {"colour": [], "rotation": []}

        # Generate possible property changes to sample from
        for idx, frame in enumerate(self.frames[1:]):
            if frame.octopus is not None:
                obj = frame.octopus
                if obj.colour != colour:
                    append_in_dict_(deltas, "colour", (idx, colour, obj.colour))
                    colour = obj.colour

                if obj.rotation != rotation:
                    append_in_dict_(deltas, "rotation", (idx, rotation, obj.rotation))
                    rotation = obj.rotation

        props = list(deltas.keys())
        random.shuffle(props)

        prop = None
        delta = None

        # Try to sample question from each property in random order
        for prop_ in props:
            prop_deltas = deltas[prop_]
            if len(prop_deltas) != 0:
                idx = random.randint(0, len(prop_deltas) - 1)
                delta = prop_deltas[idx]
                prop = prop_

        if delta is None:
            return None

        frame_idx, old_val, new_val = delta
        if prop == "rotation":
            old_val = format_rotation_value(old_val)
            new_val = format_rotation_value(new_val)

        question = f"What happened to the {obj_str} immediately after frame {frame_idx}?"
        answer = f"Its {prop} changed from {old_val} to {new_val}"

        return question, answer

    def _gen_repetition_count_question(self):
        """
        Generate a question asking about the number of times something (action or indirect effect) happened
        Q: How many times does the <object> <event>?
        A: <Non-negative Integer>
        Note: The object will always be the octopus

        :return: (question: str, answer: str)
        """

        event_counts = self._count_events()
        if event_counts.get(NO_EVENT) is not None:
            del event_counts[NO_EVENT]

        events = list(event_counts.keys())
        idx = random.randint(0, len(events) - 1)
        event = events[idx]
        count = event_counts[event]

        question = f"How many times does the octopus {event}?"
        answer = str(count)

        return question, answer

    def _gen_repeating_action_question(self):
        """
        Generate a question asking about which event occurs a given number of times
        Q: What does the <object> do <n> times?
        A: <event>
        Note: The object will always be the octopus

        :return: (question: str, answer: str)
        """

        event_counts = self._count_events()
        if event_counts.get(NO_EVENT) is not None:
            del event_counts[NO_EVENT]

        events = list(event_counts.keys())
        random.shuffle(events)

        # Track the number of times each count occurs
        counts = {}
        for _, count in event_counts.items():
            increment_in_map_(counts, count)

        question_count = None
        question_event = None

        for event in events:
            count = event_counts[event]
            num_counts = counts[count]
            if count != 0 and num_counts == 1:
                question_count = count
                question_event = event

        if question_count is None:
            return None

        question = f"What does the octopus do {question_count} times?"
        answer = question_event

        return question, answer

    def _gen_state_transition_question(self):
        """
        Generate a question about what the octopus does after something happens
        Q: What does the <object> do immediately after <event (preposition tense)> [for the <nth> time]?
        A: move/rotate left/rotate right
        Note: The object is always the octopus

        :return: (question: str, answer: str)
        """

        event_idxs = self._event_frame_idxs()

        # We don't care about frames that we know the octopus is not in
        if event_idxs.get(NO_EVENT) is not None:
            del event_idxs[NO_EVENT]
        if event_idxs.get(EAT_BAG_EVENT) is not None:
            del event_idxs[EAT_BAG_EVENT]

        # Move events are likely to be difficult to express succinctly
        if event_idxs.get(MOVE_EVENT) is not None:
            del event_idxs[MOVE_EVENT]

        # Remove events which we can't make a question out of
        for event, idxs in event_idxs.items():
            idxs = [idx for idx in idxs if idx < NUM_FRAMES - 2]
            idxs = [idx for idx in idxs if NO_EVENT not in set(self.events[idx + 1])]
            event_idxs[event] = idxs

        events = list(event_idxs.keys())
        random.shuffle(events)

        question_event = None
        nth = None
        is_single_occ = False
        frame_idx = None

        for event in events:
            idxs = event_idxs[event]
            if len(idxs) > MAX_OCCURRENCE:
                idxs = idxs[:MAX_OCCURRENCE]

            if len(idxs) > 0:
                idx = random.randint(0, len(idxs) - 1)
                nth, frame_idx = list(enumerate(idxs))[idx]
                question_event = event
                if len(idxs) == 1:
                    is_single_occ = True
                break

        if question_event is None:
            return None

        # Find next action (answer)
        actions = self.events[frame_idx + 1]
        actions = [action for action in actions if action in ACTIONS]

        assert len(actions) == 1, f"Multiple (or no) actions in a single frame: {actions}"

        action = actions[0]

        event_noun = EVENTS_TO_NOUN[question_event]
        occurrence_str = self._format_occ_str(nth + 1, is_single_occ)
        question = f"What does the octopus do immediately after {event_noun}{occurrence_str}?"
        answer = action

        return question, answer

    def _event_frame_idxs(self):
        idxs = {event: [] for event in EVENTS}
        for idx, events in enumerate(self.events):
            for event in events:
                if event[:CHANGE_COLOUR_LENGTH] == "change colour":
                    event = "change colour"

                idxs[event].append(idx)

        return idxs

    def _count_events(self):
        counts = {event: 0 for event in EVENTS}
        for events in self.events:
            for event in events:
                if event[:CHANGE_COLOUR_LENGTH] == "change colour":
                    event = "change colour"

                counts[event] += 1

        return counts

    def _find_unique_objs(self, frame):
        """
        Find all objects which can be uniquely identified in the frame
        Returns FrameObjects along with a string which uniquely identifies the object

        :param frame: Frame
        :return: List of pairs: (obj: FrameObject, obj_str: str)
        """

        objs = frame.get_objects()
        unique_objs = []
        for obj in objs:
            prop = self._unique_prop(obj, objs)
            if prop is not None:
                obj_str = self._gen_unique_obj_str(obj, prop)
                unique_objs.append((obj, obj_str))

        return unique_objs

    @staticmethod
    def _find_related_objs(objs, rel_func):
        """
        Find (un)related objects in frame
        Returns a list of related and unrelated objs
        Each element is (obj1_str, obj2_str)

        :param objs: List of (FrameObjects, obj_str) to search through
        :param rel_func: Relation function
        :return: (related, unrelated)
        """

        related_objs = []
        unrelated_objs = []
        for obj1, obj1_str in objs:
            for obj2, obj2_str in objs:
                is_related = rel_func(obj1, obj2)
                rel = (obj1_str, obj2_str)
                if obj1_str != obj2_str:
                    if is_related:
                        related_objs.append(rel)
                    else:
                        unrelated_objs.append(rel)

        return related_objs, unrelated_objs

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
            if obj.obj_type == obj_.obj_type and obj.position != obj_.position:
                unique_class = False
                if obj.colour == obj_.colour:
                    unique_colour = False
                if obj.rotation == obj_.rotation:
                    unique_rotation = False

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
    def _format_occ_str(occ, is_singular_occ):
        if is_singular_occ:
            return ""

        assert occ <= MAX_OCCURRENCE, f"Number of occurrences: {occ} is too large. Max is: {MAX_OCCURRENCE}"

        occ_str = OCCURRENCES[occ]
        occ_str = f" for the {occ_str}"
        return occ_str

    @staticmethod
    def _gen_unique_obj_str(obj, prop):
        unique_prop_val = ""
        if prop != "class":
            unique_prop_val = obj.get_prop_val(prop)
            if prop == "rotation":
                unique_prop_val = format_rotation_value(unique_prop_val)

            unique_prop_val = str(unique_prop_val) + " "

        obj_str = f"{unique_prop_val}{obj.obj_type}"
        return obj_str

    def to_dict(self):
        return {
            "frames": [frame.to_dict() for frame in self.frames],
            "events": self.events,
            "questions": self.questions,
            "answers": self.answers,
            "question_types": self.q_idxs
        }
