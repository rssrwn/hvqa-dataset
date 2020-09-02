import random

from hvqadata.video.frame import Frame
from hvqadata.util.definitions import *


class Video:

    def __init__(self, frames, events):
        self.frames = frames
        self.events = events
        self.questions = []
        self.answers = []
        self.q_types = []

    @staticmethod
    def random_video():
        initial = Frame()
        initial.random_frame()

        frames = [initial]
        events = []

        curr = initial
        for frame in range(1, NUM_FRAMES):
            curr, events_ = curr.move()
            frames.append(curr)
            events.append(events_)

        video = Video(frames, events)
        return video

    def shuffle_questions_(self):
        q_idxs = list(range(len(self.questions)))
        random.shuffle(q_idxs)
        self.questions = [self.questions[q_idx] for q_idx in q_idxs]
        self.answers = [self.answers[q_idx] for q_idx in q_idxs]
        self.q_types = [self.q_types[q_idx] for q_idx in q_idxs]

    def add_question(self, question, q_type, answer):
        self.questions.append(question)
        self.q_types.append(q_type)
        self.answers.append(answer)

    def to_dict(self):
        return {
            "frames": [frame.to_dict() for frame in self.frames],
            "events": self.events,
            "questions": self.questions,
            "answers": self.answers,
            "question_types": self.q_types
        }
