import argparse

from hvqadata.util.func import get_video_dicts, increment_in_map_
from hvqadata.util.definitions import CHANGE_COLOUR_LENGTH


def extract_event(event):
    if event[0:CHANGE_COLOUR_LENGTH] == "change colour":
        event = "change colour"

    return event


def count_events(video_dicts):
    event_list = []
    num_frame_changes = 0
    for video in video_dicts:
        events = video["events"]
        num_frame_changes += len(events)
        flat_events = [event for subevents in events for event in subevents]
        events = [extract_event(event) for event in flat_events]
        event_list.extend(events)

    event_dict = {}
    for event in event_list:
        increment_in_map_(event_dict, event)

    print(f"{'Event name' :<20}{'Occurrences' :<15}Frequency")
    for event, num in event_dict.items():
        print(f"{event:<20}{num:<15}{(num / num_frame_changes) * 100:.3g}%")

    print(f"\nTotal number of frame changes: {num_frame_changes}\n")


def count_colours(video_dicts):
    rock_colours = {}
    octo_colours = {}
    num_frames = 0
    for video in video_dicts:
        frames = video["frames"]
        for frame in frames:
            num_frames += 1
            objects = frame["objects"]
            for obj in objects:
                if obj["class"] == "rock":
                    increment_in_map_(rock_colours, obj["colour"])
                elif obj["class"] == "octopus":
                    increment_in_map_(octo_colours, obj["colour"])

    print(f"{'Rock colour' :<20}{'Occurrences' :<15}Frequency")
    for colour, num in rock_colours.items():
        print(f"{colour:<20}{num:<15}{(num / num_frames) * 100:.3g}%")

    print(f"\n{'Octopus colour' :<20}{'Occurrences' :<15}Frequency")
    for colour, num in octo_colours.items():
        print(f"{colour:<20}{num:<15}{(num / num_frames) * 100:.3g}%")

    print(f"\nTotal number of frames: {num_frames}\n")


def count_rotations(video_dicts):
    rotations = {}
    num_frames = 0
    for video in video_dicts:
        frames = video["frames"]
        for frame in frames:
            num_frames += 1
            objects = frame["objects"]
            for obj in objects:
                if obj["class"] == "octopus":
                    increment_in_map_(rotations, obj["rotation"])

    print(f"{'Octopus rotations' :<20}{'Occurrences' :<15}Frequency")
    for rotation, num in rotations.items():
        print(f"{rotation:<20}{num:<15}{(num / num_frames) * 100:.3g}%")

    print(f"\nTotal number of frames: {num_frames}\n")


def count_fish_eaten(video_dicts):
    fish_eaten = {}
    num_videos = 0
    for video in video_dicts:
        events = video["events"]
        num_videos += 1
        num_fish_eaten = 0
        for event_list in events:
            if "eat fish" in event_list:
                num_fish_eaten += 1

        increment_in_map_(fish_eaten, num_fish_eaten)

    fish_eaten = fish_eaten.items()
    fish_eaten = sorted(fish_eaten, key=lambda eaten: eaten[0])

    print(f"{'Fish eaten' :<15}{'Occurrences' :<15}Frequency")
    for num_eaten, cnt in fish_eaten:
        print(f"{num_eaten:<15}{cnt:<15}{(cnt / num_videos) * 100:.3g}%")

    print(f"Total number of videos: {num_videos}")


def analyse_questions(video_dicts):
    counts = {}
    for video in video_dicts:
        question_types = video["question_types"]
        for question in question_types:
            increment_in_map_(counts, question)

    num_questions = sum([cnt for _, cnt in counts.items()])

    counts = counts.items()
    counts = sorted(counts, key=lambda pair: pair[0])

    print(f"{'Question Type' :<20}{'Occurrences' :<15}Frequency")
    for question_type, count in counts:
        print(f"{question_type:<20}{count:<15}{(count / num_questions) * 100:.3}%")

    print(f"Total number of questions: {num_questions}")


def main(data_dir, events, colours, rotations, fish, questions):
    video_dicts = get_video_dicts(data_dir)

    if events:
        print("Analysing event occurrences...")
        count_events(video_dicts)

    if colours:
        print("Analysing object colours...")
        count_colours(video_dicts)

    if rotations:
        print("Analysing octopus rotations...")
        count_rotations(video_dicts)

    if fish:
        print("Analysing number of fish eaten...")
        count_fish_eaten(video_dicts)

    if questions:
        print("Analysing question distribution...")
        analyse_questions(video_dicts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script for analysing built dataset")
    parser.add_argument("-e", "--events", action="store_true", default=False)
    parser.add_argument("-c", "--colours", action="store_true", default=False)
    parser.add_argument("-r", "--rotations", action="store_true", default=False)
    parser.add_argument("-f", "--fish", action="store_true", default=False)
    parser.add_argument("-q", "--questions", action="store_true", default=False)
    parser.add_argument("data_dir", type=str)
    args = parser.parse_args()
    main(args.data_dir, args.events, args.colours, args.rotations, args.fish, args.questions)
