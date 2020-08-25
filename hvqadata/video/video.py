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
            curr, events = curr.move()
            frames.append(curr)
            events.append(events)

        video = Video(frames, events)
        return video

    def to_dict(self):
        return {
            "frames": [frame.to_dict() for frame in self.frames],
            "events": self.events,
            "questions": self.questions,
            "answers": self.answers,
            "question_types": self.q_types
        }
