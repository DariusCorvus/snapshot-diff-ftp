import ftp
import pathlib
import time
from watchdog.utils.dirsnapshot import DirectorySnapshotDiff, DirectorySnapshot
import hashlib
from decouple import config
hashs = {}
data = {}
INTERVAL = config("INTERVAL", default=1, cast=int)
BASE_DIR = config("BASE_DIR")
FTP_BASE_DIR = config("FTP_BASE_DIR")


def is_invalid(path):
    return path == "."


def handle_path(path, event):
    if is_invalid(path):
        return

    data.update({path: event})


def print_paths(paths: list, event: str):
    [handle_path(x.replace(BASE_DIR, "."), event) for x in paths]


def action_file(path, event):
    real_path = pathlib.Path(BASE_DIR, path)
    if real_path.is_dir():
        return
    if "DELETED" in event:
        ftp.delete(path)
        del hashs[path]
        return
    hash = hash_file(path)
    is_equal_hash = hash == hashs.get(path)
    if is_equal_hash:
        return

    if "MODIFIED" in event:
        hashs.update({path: hash})

        ftp.upload(path)

    if "CREATED" in event:
        hashs.update({path: hash})

        ftp.upload(path)


def action(actions):
    while (len(actions)):
        path, event = actions.popitem()
        _path = pathlib.Path(path)
        if _path.is_file() or not _path.exists():
            action_file(path, event)


def handle_diff(diff: DirectorySnapshotDiff):
    print_paths(diff.dirs_deleted, "DELETED_DIR")
    print_paths(diff.dirs_modified, "MODIFIED_DIR")
    print_paths(diff.dirs_created, "CREATED_DIR")
    print_paths(diff.dirs_moved, "MOVED_DIR")
    print_paths(diff.files_deleted, "DELETED_FILE")
    print_paths(diff.files_modified, "MODIFIED_FILE")
    print_paths(diff.files_created, "CREATED_FILE")
    print_paths(diff.files_moved, "MOVED_FILE")
    # print("-"*20)
    # print("PATHS TO TAKE ACTION")
    # print("-"*20)
    # print(data)
    action(data)


def hash_file(path):
    """This function returns the SHA-1 hash
    of the file passed into it"""

    # make a hash object
    h = hashlib.sha1()

    real_path = pathlib.Path(BASE_DIR, path)
    # open file for reading in binary mode
    with open(str(real_path), 'rb') as file:

        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()


def is_invalid_path(path):
    _path = str(path)
    if _path in (".\\", "./"):
        return True
    if _path.startswith("./.venv"):
        return True
    if _path.startswith("./.git"):
        return True

    return False


if __name__ == "__main__":
    try:
        ref = DirectorySnapshot(BASE_DIR)
        for path in ref.paths:
            path = path.replace(BASE_DIR, ".")
            real_path = pathlib.Path(BASE_DIR, path)
            if real_path.is_file():
                if is_invalid_path(str(real_path)):
                    continue
                hashs.update({path: hash_file(path)})
        print("INITIALIZED... IM WATCHING YOU!")
        while True:
            time.sleep(INTERVAL)
            cur = DirectorySnapshot(BASE_DIR)
            diff = DirectorySnapshotDiff(ref, cur)
            ref = cur
            handle_diff(diff)
    except KeyboardInterrupt:
        pass
