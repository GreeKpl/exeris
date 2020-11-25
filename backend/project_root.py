# it exists only to show where is module root
import os


def _remove_last_part(text):
    return "/".join(text.split("/")[:-1])


ROOT_PATH = _remove_last_part(__file__)


def relative_to_project_root(path):
    return os.path.relpath(path, ROOT_PATH)
