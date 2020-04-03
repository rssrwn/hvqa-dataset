# *** Util functions ***

import json
from pathlib import Path

from hvqadata.util.definitions import CLOSE_OCTO as CLOSE_TO


def get_video_dicts(data_dir):
    directory = Path(data_dir)

    dicts = []
    num_dicts = 0
    for video_dir in directory.iterdir():
        json_file = video_dir / "video.json"
        if json_file.exists():
            with json_file.open() as f:
                json_text = f.read()

            video_dict = json.loads(json_text)
            dicts.append(video_dict)
            num_dicts += 1

        else:
            raise FileNotFoundError(f"{json_file} does not exist")

    print(f"Successfully extracted {num_dicts} video dictionaries from json files")
    return dicts


def close_to(obj1, obj2):
    """
    Returns whether the obj1 is close to the obj2
    A border is created around the obj1, obj2 is close if it is within the border

    :param obj1: FrameObject
    :param obj2: FrameObject
    :return: bool
    """

    obj1_x1, obj1_y1, obj1_x2, obj1_y2 = obj1.position
    obj1_x1 -= CLOSE_TO
    obj1_x2 += CLOSE_TO
    obj1_y1 -= CLOSE_TO
    obj1_y2 += CLOSE_TO

    x1, y1, x2, y2 = obj2.position
    obj_corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

    x_overlap = x2 >= obj1_x2 and x1 <= obj1_x1
    y_overlap = y2 >= obj1_y2 and y1 <= obj1_y1

    for x, y in obj_corners:
        match_x = obj1_x1 <= x <= obj1_x2 or x_overlap
        match_y = obj1_y1 <= y <= obj1_y2 or y_overlap
        if match_x and match_y:
            return True

    return False
