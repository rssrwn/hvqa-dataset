import json
import argparse
import shutil
from PIL import Image
from pathlib import Path

from hvqadata.video.dataset import OceanQADataset
from hvqadata.draw import Drawer


SPLIT_PERC = 0.2


def write_json(out_dir, num_videos):
    print("Writing json to file...")

    # Create json videos
    videos = OceanQADataset.random_videos(num_videos)
    train, val, test = videos.split(SPLIT_PERC)

    train.write(out_dir + "/train")
    val.write(out_dir + "/val")
    test.write(out_dir + "/test")


def create_videos(out_dir):
    basepath = Path(out_dir)
    video_dirs = basepath.iterdir()

    print("Creating frames from json...")

    num_videos_total = 0
    num_frames_total = 0
    for video_dir in video_dirs:
        json_file = video_dir / "video.json"
        if json_file.exists():
            with json_file.open() as f:
                json_text = f.read()

            video_dict = json.loads(json_text)
            frames = video_dict["frames"]
            for i, frame in enumerate(frames):
                img = create_frame(frame)
                img.save(f"{video_dir}/frame_{i}.png")
                num_frames_total += 1

        else:
            print(f"No 'video.json' file found for {video_dir}/")

        num_videos_total += 1

    print(f"Successfully created {num_videos_total} videos with {num_frames_total} total frames")


def create_frame(frame):
    np_img = Drawer.draw_frame(frame)
    img = Image.fromarray(np_img, "RGB")
    return img


def delete_directory(name):
    directory = Path(f"./{name}")
    if directory.exists():
        response = input(f"About to delete {name} directory. Are you sure you want to continue? [y/n] ")
        if response != "y":
            print("Exiting...")
            exit()
        try:
            shutil.rmtree(name)
        except OSError as e:
            print("Error while deleting directory: %s - %s." % (e.filename, e.strerror))


def main(out_dir, num_videos, json_only, frames_only):
    if not frames_only:
        delete_directory(out_dir)
        path = Path(f"./{out_dir}")
        path.mkdir(parents=True, exist_ok=False)
        write_json(out_dir, num_videos)

    if not json_only:
        response = input(f"About to create frames. This could overwrite old frames. "
                         f"Are you sure you want to continue? [y/n] ")
        if response != "y":
            print("Exiting...")
            exit()

        create_videos(out_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script for building dataset")
    parser.add_argument("-j", "--json_only", action="store_true", default=False)
    parser.add_argument("-f", "--frames_only", action="store_true", default=False)
    parser.add_argument("out_dir", type=str)
    parser.add_argument("num_videos", type=int)
    args = parser.parse_args()
    main(args.out_dir, args.num_videos, args.json_only, args.frames_only)
