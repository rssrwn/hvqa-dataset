import argparse

import matplotlib.pyplot as plt

from hvqadata.util.func import get_video_dicts, increment_in_map_, append_in_dict_
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

    q_types = [q_cnt[0]+1 for q_cnt in counts]
    cnts = [q_cnt[1] for q_cnt in counts]

    fontsize = 18

    plt.figure(figsize=(12,6))
    plt.bar(q_types, cnts)
    plt.xlabel("Question Type", fontsize=fontsize)
    plt.ylabel("Number of questions", fontsize=fontsize)
    plt.xticks(q_types, fontsize=fontsize)
    plt.yticks([0, 400, 800, 1200, 1600], fontsize=fontsize)
    plt.show()


def _print_cnt_dict(counts, col_name):
    total = sum([cnt for _, cnt in counts.items()])

    counts = counts.items()
    counts = sorted(counts, key=lambda pair: pair[0])

    print(f"\n{col_name:<20}{'Occurrences' :<15}Frequency")
    for col, count in counts:
        print(f"{col:<20}{count:<15}{(count / total) * 100:.3}%")


def analyse_answers(video_dicts):
    q_type_video_dict_map = {}
    for video in video_dicts:
        q_types = video["question_types"]
        for q_idx, q_type in enumerate(q_types):
            question = video["questions"][q_idx]
            answer = video["answers"][q_idx]
            append_in_dict_(q_type_video_dict_map, q_type, (question, answer))

    _analyse_q_0(q_type_video_dict_map[0])
    _analyse_q_1(q_type_video_dict_map[1])
    _analyse_q_2(q_type_video_dict_map[2])
    _analyse_q_3(q_type_video_dict_map[3])
    _analyse_q_4(q_type_video_dict_map[4])
    _analyse_q_5(q_type_video_dict_map[5])
    _analyse_q_6(q_type_video_dict_map[6])


def _analyse_q_0(qa_pairs):
    print("\nAnalysing property QA pairs...")

    prop_cnt = {}
    prop_val_cnt = {"colour": {}, "rotation": {}}
    for question, answer in qa_pairs:
        prop = question.split(" ")[1]
        prop_val = answer
        increment_in_map_(prop_cnt, prop)
        increment_in_map_(prop_val_cnt[prop], prop_val)

    _print_cnt_dict(prop_cnt, "Property")
    _print_cnt_dict(prop_val_cnt["colour"], "Colour Value")
    _print_cnt_dict(prop_val_cnt["rotation"], "Rotation Value")


def _analyse_q_1(qa_pairs):
    print("\nAnalysing relation QA pairs...")

    ans_cnt = {}
    for question, answer in qa_pairs:
        increment_in_map_(ans_cnt, answer)

    _print_cnt_dict(ans_cnt, "Answer")


def _analyse_q_2(qa_pairs):
    print("\nAnalysing event QA pairs...")

    action_cnt = {}
    for question, answer in qa_pairs:
        increment_in_map_(action_cnt, answer)

    _print_cnt_dict(action_cnt, "Action")


def _analyse_q_3(qa_pairs):
    print("\nAnalysing prop changed QA pairs...")

    prop_cnt = {}
    for question, answer in qa_pairs:
        prop = answer.split(" ")[1]
        increment_in_map_(prop_cnt, prop)

    _print_cnt_dict(prop_cnt, "Property")


def _analyse_q_4(qa_pairs):
    print("\nAnalysing repetition count QA pairs...")

    event_cnt = {}
    for question, answer in qa_pairs:
        event = question.split(" ")[-1][:-1]
        increment_in_map_(event_cnt, event)

    _print_cnt_dict(event_cnt, "Event")


def _analyse_q_5(qa_pairs):
    print("\nAnalysing repeating action QA pairs...")

    event_cnt = {}
    for question, answer in qa_pairs:
        increment_in_map_(event_cnt, answer)

    _print_cnt_dict(event_cnt, "Event")


def _analyse_q_6(qa_pairs):
    print("\nAnalysing state transition QA pairs...")

    action_cnt = {}
    for question, answer in qa_pairs:
        increment_in_map_(action_cnt, answer)

    _print_cnt_dict(action_cnt, "Action")


def main(data_dir, events, colours, rotations, fish, questions, answers):
    video_dicts = get_video_dicts(data_dir)

    if events:
        print("\nAnalysing event occurrences...")
        count_events(video_dicts)

    if colours:
        print("\nAnalysing object colours...")
        count_colours(video_dicts)

    if rotations:
        print("\nAnalysing octopus rotations...")
        count_rotations(video_dicts)

    if fish:
        print("\nAnalysing number of fish eaten...")
        count_fish_eaten(video_dicts)

    if questions:
        print("\nAnalysing question distribution...")
        analyse_questions(video_dicts)

    if answers:
        print("\nAnalysing distributions of answers to questions...")
        analyse_answers(video_dicts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script for analysing built dataset")
    parser.add_argument("-e", "--events", action="store_true", default=False)
    parser.add_argument("-c", "--colours", action="store_true", default=False)
    parser.add_argument("-r", "--rotations", action="store_true", default=False)
    parser.add_argument("-f", "--fish", action="store_true", default=False)
    parser.add_argument("-q", "--questions", action="store_true", default=False)
    parser.add_argument("-a", "--answers", action="store_true", default=False)
    parser.add_argument("data_dir", type=str)
    args = parser.parse_args()
    main(args.data_dir,
         args.events,
         args.colours,
         args.rotations,
         args.fish,
         args.questions,
         args.answers)
