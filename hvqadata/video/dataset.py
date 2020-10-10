import json
import random
from pathlib import Path

import hvqadata.util.func as util
from hvqadata.video.video import Video
from hvqadata.util.definitions import *


class OceanQADataset:
    def __init__(self, videos):
        self._question_funcs = [
            self._gen_prop_question,
            self._gen_relations_question,
            self._gen_action_question,
            self._gen_prop_changed_question,
            self._gen_repetition_count_question,
            self._gen_repeating_action_question,
            self._gen_state_transition_question,
            self._gen_explanation_question,
            self._gen_counterfactual_question
        ]
        self._relations = {
            "close to": util.close_to,
            "above": util.above,
            "below": util.below
        }
        self.videos = videos

    @staticmethod
    def random_videos(num_videos, qs_attempts=None, min_questions=2):
        videos = [Video.random_video() for _ in range(num_videos)]
        dataset = OceanQADataset(videos)
        dataset._gen_qa_pairs(qs_attempts=qs_attempts, min_questions=min_questions)
        return dataset

    def _gen_qa_pairs(self, qs_attempts=None, min_questions=2):
        qs_attempts = len(self.videos) * 4 if qs_attempts is None else qs_attempts

        q_type_cnts = {q_type: 0 for q_type in range(len(self._question_funcs))}
        q_dim_cnts = {
            0: {
                "colour": {col: 0 for col in COLOURS},
                "rotation": {rot: 0 for rot in ROTATIONS}
            },
            1: {rel: {"yes": 0, "no": 0} for rel, _ in self._relations.items()},
            2: {action: 0 for action in ACTIONS},
            3: {
                "colour": {col: 0 for col in ROCK_COLOURS},
                "rotation": {rot: 0 for rot in ROTATIONS}
            },
            4: {event: 0 for event in ACTIONS + EFFECTS},
            5: {event: 0 for event in ACTIONS + EFFECTS},
            6: {
                event: {action: 0 for action in ACTIONS}
                for event in [ROTATE_LEFT_EVENT, ROTATE_RIGHT_EVENT, EAT_FISH_EVENT, "change colour"]
            },
            7: {answer: 0 for answer in ["The octopus ate a bag", "The bag was eaten", "The fish was eaten"]},
            8: {answer: 0 for answer in [OCTO_COLOUR] + ROCK_COLOURS}
        }

        for _ in range(qs_attempts):
            v_idxs = list(range(len(self.videos)))
            random.shuffle(v_idxs)

            q_func, q_type = self._sample_q_func(q_type_cnts)
            sample = self._sample_from_arb_dict(q_dim_cnts[q_type])

            for v_idx in v_idxs:
                video = self.videos[v_idx]
                qa_pair = q_func(video, sample, q_dim_cnts[q_type])
                if qa_pair is not None:
                    question, answer = qa_pair
                    video.add_question(question, q_type, answer)
                    q_type_cnts[q_type] += 1
                    break

        # Shuffle all questions in each video and remove any video with less than 2 questions
        new_videos = []
        for video in self.videos:
            if len(video.questions) >= min_questions:
                video.shuffle_questions_()
                new_videos.append(video)

        self.videos = new_videos

        num_videos = len(self.videos)
        avg = "nan" if num_videos == 0 else f"{sum([len(video.questions) for video in self.videos]) / num_videos:.2f}"
        print(f"Kept {num_videos} videos in dataset...")
        print(f"With an average of {avg} questions per video.")

    def split(self, split_perc):
        num_videos = len(self.videos)
        num_val = round(num_videos * split_perc)

        idxs = set(range(num_videos))
        val_idxs = random.sample(idxs, num_val)
        random.shuffle(val_idxs)
        val_videos = [self.videos[idx] for idx in val_idxs]
        val_dataset = OceanQADataset(val_videos)

        remaining_idxs = idxs - set(val_idxs)
        test_idxs = random.sample(remaining_idxs, num_val)
        random.shuffle(test_idxs)
        test_videos = [self.videos[idx] for idx in test_idxs]
        test_dataset = OceanQADataset(test_videos)

        train_idxs = remaining_idxs - set(test_idxs)
        random.shuffle(list(train_idxs))
        train_videos = [self.videos[idx] for idx in train_idxs]
        train_dataset = OceanQADataset(train_videos)

        return train_dataset, val_dataset, test_dataset

    def write(self, out_dir):
        num_videos_written = 0
        for video_num, video in enumerate(self.videos):
            # Write text to file
            text = json.dumps(video.to_dict())
            video_dir = Path(f"./{out_dir}/{video_num}")
            if not video_dir.exists():
                video_dir.mkdir(parents=True, exist_ok=False)

            file = open(f"./{out_dir}/{video_num}/video.json", "w")
            file.write(text)
            file.close()

            num_videos_written += 1

        print(f"Successfully written {num_videos_written} json files")

    def _sample_q_func(self, q_type_cnts):
        q_type = self._sample_from_dict(q_type_cnts)
        q_func = self._question_funcs[q_type]
        return q_func, q_type

    def _sample_from_arb_dict(self, cnts):
        if type(list(cnts.values())[0]) == dict:
            result = self._sample_from_2_layer_dict(cnts)
            result = (result, self._sample_from_dict(cnts[result]))
        else:
            result = (self._sample_from_dict(cnts),)

        return result

    @staticmethod
    def _sample_from_dict(cnts):
        total = sum(cnts.values())
        item_weights = {item: total - cnt for item, cnt in cnts.items()}
        items, weights = tuple(zip(*item_weights.items()))
        if sum(weights) == 0:
            item = random.choices(items, k=1)[0]
        else:
            item = random.choices(items, weights=weights, k=1)[0]

        return item

    @staticmethod
    def _sample_from_2_layer_dict(cnts):
        total = sum([sum(cnts_.values()) for _, cnts_ in cnts.items()])
        weight_dict = {prop: total - sum(cnts_.values()) for prop, cnts_ in cnts.items()}
        items, weights = tuple(zip(*weight_dict.items()))
        if sum(weights) == 0:
            item = random.choices(items, k=1)[0]
        else:
            item = random.choices(items, weights=weights, k=1)[0]

        return item

    def _gen_prop_question(self, video, sample, q_cnts):
        """
        Generate question asking about a property of an object for a single frame
        Q: What <property> was the <object> in frame <frame_idx>?
        A: <property_val>

        :return: (question: str, answer: str)
        """

        prop, prop_val = sample

        qa_pair = None

        frame_idxs = list(range(NUM_FRAMES))
        random.shuffle(frame_idxs)
        for frame_idx in frame_idxs:
            if qa_pair is not None:
                break

            frame = video.frames[frame_idx]
            unique_objs = self._find_unique_objs(frame)
            random.shuffle(unique_objs)

            for obj, obj_str in unique_objs:
                if obj.get_prop_val(prop) == prop_val:
                    question = f"What {prop} was the {obj_str} in frame {str(frame_idx)}?"
                    answer = util.format_rotation_value(prop_val) if prop == "rotation" else str(prop_val)
                    if question not in video.questions:
                        qa_pair = question, answer
                        break

        if qa_pair is not None:
            q_cnts[prop][prop_val] += 1

        return qa_pair

    def _gen_relations_question(self, video, sample, q_cnts):
        """
        Generate question asking about a relation between two objects in a single frame
        Q: Was the <object> <relation> to the <object> in frame <frame idx>?
        A: yes/no

        :return: (question: str, answer: str)
        """

        rel, answer = sample

        rel_func = self._relations[rel]
        is_yes = answer == "yes"
        rels, frame_idx = self._sample_relation(video, rel_func, is_yes)

        # If this question fails, try another question
        if rels is None:
            return None

        qa_pair = None

        random.shuffle(rels)
        for rel_idx in range(len(rels)):
            rel_objs = rels[rel_idx]
            obj1_str, obj2_str = rel_objs
            question = f"Was the {obj1_str} {rel} the {obj2_str} in frame {frame_idx}?"
            if question not in video.questions:
                qa_pair = question, answer
                break

        if qa_pair is not None:
            q_cnts[rel][answer] += 1

        return qa_pair

    def _gen_action_question(self, video, sample, q_cnts):
        """
        Generate a question which asks about which action occurred
        Q: Which action occurred immediately after frame <frame_idx>?
        A: move/rotate left/rotate right

        :return: (question: str, answer: str)
        """

        answer = sample[0]

        frame_idxs = [idx for idx, events in enumerate(video.events) if answer in events]
        if len(frame_idxs) == 0:
            return None

        qa_pair = None

        random.shuffle(frame_idxs)
        for frame_idx in frame_idxs:
            question = f"Which action occurred immediately after frame {frame_idx}?"
            if question not in video.questions:
                qa_pair = question, answer
                break

        if qa_pair is not None:
            q_cnts[answer] += 1

        return qa_pair

    def _gen_prop_changed_question(self, video, sample, q_cnts):
        """
        Generate a question about which property of an object changed (and what it changed to)
        Q: What happened to the octopus immediately after <frame_idx>?
        A: Its rotation/colour changed from <property value> to <property value>

        :return: (question: str, answer: str)
        """

        prop, prop_val = sample

        obj = video.frames[0].octopus
        obj_str = self._gen_unique_obj_str(obj, "class")
        colour = obj.colour
        rotation = obj.rotation

        deltas = []

        # Generate possible property changes to choose from
        for idx, frame in enumerate(video.frames[1:]):
            if frame.octopus is not None:
                obj = frame.octopus
                if prop == "colour" and obj.colour != colour and obj.colour == prop_val:
                    deltas.append((idx, colour, obj.colour))
                    colour = obj.colour

                if prop == "rotation" and obj.rotation != rotation and obj.rotation == prop_val:
                    deltas.append((idx, rotation, obj.rotation))
                    rotation = obj.rotation

        if len(deltas) == 0:
            return None

        random.shuffle(deltas)
        qa_pair = None

        for delta in deltas:
            frame_idx, old_val, new_val = delta
            if prop == "rotation":
                old_val = util.format_rotation_value(old_val)
                new_val = util.format_rotation_value(new_val)

            question = f"What happened to the {obj_str} immediately after frame {frame_idx}?"
            answer = f"Its {prop} changed from {old_val} to {new_val}"
            if question not in video.questions:
                qa_pair = question, answer
                break

        if qa_pair is not None:
            q_cnts[prop][prop_val] += 1

        return qa_pair

    def _gen_repetition_count_question(self, video, sample, q_cnts):
        """
        Generate a question asking about the number of times something (action or indirect effect) happened
        Q: How many times does the octopus <event>?
        A: <Non-negative Integer>

        :return: (question: str, answer: str)
        """

        event = sample[0]

        event_counts = self._count_events(video)
        if event_counts[event] == 0:
            return None

        question = f"How many times does the octopus {event}?"
        if question in video.questions:
            return None

        answer = str(event_counts[event])
        qa_pair = question, answer
        q_cnts[event] += 1

        return qa_pair

    def _gen_repeating_action_question(self, video, sample, q_cnts):
        """
        Generate a question asking about which event occurs a given number of times
        Q: What does the octopus do <n> times?
        A: <event>

        :return: (question: str, answer: str)
        """

        event = sample[0]

        event_counts = self._count_events(video)
        if event_counts[event] == 0:
            return None

        # Track the number of times each count occurs
        counts = {}
        for _, count in event_counts.items():
            util.increment_in_map_(counts, count)

        # Ensure the count is unique
        question_cnt = event_counts[event]
        if counts[question_cnt] > 1:
            return None

        question = f"What does the octopus do {question_cnt} times?"
        if question in video.questions:
            return None

        qa_pair = question, event
        q_cnts[event] += 1

        return qa_pair

    def _gen_state_transition_question(self, video, sample, q_cnts):
        """
        Generate a question about what the octopus does after something happens
        Q: What does the octopus do immediately after <event (preposition tense)> [for the <nth> time]?
        A: move/rotate left/rotate right

        :return: (question: str, answer: str)
        """

        event, answer = sample

        event_idxs = self._event_frame_idxs(video)
        frame_idxs = event_idxs[event]
        if len(frame_idxs) == 0:
            return None

        usable_events = []
        for event_idx, frame_idx in enumerate(frame_idxs):
            if (frame_idx + 2) < NUM_FRAMES and event_idx < MAX_OCCURRENCE and answer in video.events[frame_idx + 1]:
                usable_events.append(event_idx)

        if len(usable_events) == 0:
            return None

        random.shuffle(usable_events)
        nth = usable_events[0]
        event_noun = EVENTS_TO_NOUN[event]
        is_single_occ = len(frame_idxs) == 1
        occurrence_str = self._format_occ_str(nth + 1, is_single_occ)
        question = f"What does the octopus do immediately after {event_noun}{occurrence_str}?"
        if question in video.questions:
            return None

        qa_pair = question, answer
        q_cnts[event][answer] += 1

        return qa_pair

    def _gen_explanation_question(self, video, sample, q_cnts):
        """
        Generate a question asking why something happened
        Q: Why did the <rotation> object disappear?
        A: The octopus ate a bag / the bag was eaten / the fish was eaten

        :return: (question: str, answer: str)
        """

        answer = sample[0]

        # Find disappeared objs
        disappear = self._find_disappear_objs(video.frames)
        disappear = [obj for obj, _ in disappear]

        # Find objs with a unique rotation within the disappeared list
        unique_objs = []
        for obj1 in disappear:
            unique = True
            for obj2 in disappear:
                if obj1.rotation == obj2.rotation and obj1.position != obj2.position:
                    unique = False

            if unique:
                unique_objs.append(obj1)

        if len(unique_objs) == 0:
            return None

        question_obj = None

        random.shuffle(unique_objs)
        for obj in unique_objs:
            if (answer == "The octopus ate a bag" and obj.obj_type == "octopus")\
                    or (answer == "The bag was eaten" and obj.obj_type == "bag")\
                    or (answer == "The fish was eaten" and obj.obj_type == "fish"):
                question_obj = obj
                break

        if question_obj is None:
            return None

        rot = util.format_rotation_value(question_obj.rotation)
        question = f"Why did the {rot} object disappear?"
        if question in video.questions:
            return None

        q_cnts[answer] += 1

        return question, answer

    def _gen_counterfactual_question(self, video, sample, q_cnts):
        """
        Generate a question asking what the state would be like if an object was not there
        Q: What colour would the octopus be in its final frame without the <colour> rock?
        A: <colour>

        :return: (question: str, answer: str)
        """

        answer = sample[0]

        unique_objs = self._find_unique_objs(video.frames[0])
        unique_rocks = [obj for obj, _ in unique_objs if obj.obj_type == "rock"]
        unique_colours = [rock.colour for rock in unique_rocks]
        random.shuffle(unique_colours)

        # If no unique rocks, we cannot sample this type of question
        if len(unique_rocks) == 0:
            return None

        question = None

        for rock_colour in unique_colours:
            check_q = self._check_counterfactual_answer(video, rock_colour, answer)
            qs = f"What colour would the octopus be in its final frame without the {rock_colour} rock?"
            if check_q and qs not in video.questions:
                question = qs
                break

        qa_pair = None

        if question is not None:
            qa_pair = question, answer
            q_cnts[answer] += 1

        return qa_pair

    def _check_counterfactual_answer(self, video, rock_colour, answer):
        # Note: We assume the rock with <rock_colour> is unique

        colour_changes = self._find_colour_changes(video.frames)
        colours_wo_rock = [OCTO_COLOUR] + [col_to for _, col_to in colour_changes if col_to != rock_colour]
        qa_pair_correct = colours_wo_rock[-1] == answer
        return qa_pair_correct

    def _find_colour_changes(self, frames):
        changes = []
        curr_colour = frames[0].octopus.colour
        for frame in frames[1:]:
            if frame.octopus is not None:
                colour = frame.octopus.colour
                if colour != curr_colour:
                    changes.append((curr_colour, colour))
                    curr_colour = colour

        return changes

    def _find_disappear_objs(self, frames):
        disappear = []
        curr_objs = frames[0].get_objects()
        for frame_idx, frame in enumerate(frames[1:]):
            next_objs = frame.get_objects()
            for curr_obj in curr_objs:
                disappeared = True
                for next_obj in next_objs:
                    if curr_obj.obj_type == "octopus" and next_obj.obj_type == "octopus" \
                            or curr_obj.position == next_obj.position:
                        disappeared = False

                if disappeared:
                    disappear.append((curr_obj, frame_idx))

            curr_objs = next_objs

        return disappear

    def _sample_relation(self, video, rel_func, is_yes):
        frame_idxs = list(range(NUM_FRAMES))
        random.shuffle(frame_idxs)

        frame_idx = None
        rels = None

        # Attempt to sample a question from each frame randomly
        for frame_idx in frame_idxs:
            frame = video.frames[frame_idx]
            unique_objs = self._find_unique_objs(frame)
            related_objs, unrelated_objs = self._find_related_objs(unique_objs, rel_func)
            if is_yes:
                if len(related_objs) > 0:
                    rels = related_objs
                    break
            else:
                if len(unrelated_objs) > 0:
                    rels = unrelated_objs
                    break

        return rels, frame_idx

    @staticmethod
    def _event_frame_idxs(video):
        idxs = {event: [] for event in EVENTS}
        for idx, events in enumerate(video.events):
            for event in events:
                if event[:CHANGE_COLOUR_LENGTH] == "change colour":
                    event = "change colour"

                idxs[event].append(idx)

        return idxs

    @staticmethod
    def _count_events(video):
        counts = {event: 0 for event in EVENTS}
        for events in video.events:
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

        :param objs: List of (FrameObject, obj_str) to search through
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
                unique_prop_val = util.format_rotation_value(unique_prop_val)

            unique_prop_val = str(unique_prop_val) + " "

        obj_str = f"{unique_prop_val}{obj.obj_type}"
        return obj_str
