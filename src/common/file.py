import os


def file(path: str, current_file: str):
    current_dir = os.path.dirname(current_file)

    absolute_path = os.path.join(current_dir, path)

    return open(absolute_path)
