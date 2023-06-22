import pathlib
from ftplib import FTP
from ftplib import error_perm
from decouple import config

FTP_PORT = config("FTP_PORT", cast=int, default=21)
FTP_HOST = config("FTP_HOST")
FTP_USER = config("FTP_USER")
FTP_PASS = config("FTP_PASS")
FTP_BASE_DIR = config("FTP_BASE_DIR")
FTP_PASSIV = config("FTP_PASSIV", cast=bool, default=True)
BASE_DIR = config("BASE_DIR")


def upload(path: str):
    with FTP() as client:
        client.set_pasv(FTP_PASSIV)
        client.connect(FTP_HOST, FTP_PORT)
        client.login(FTP_USER, FTP_PASS)
        path = pathlib.Path(path)
        real_path = pathlib.Path(BASE_DIR, path)
        if not real_path.exists():
            raise Exception(f"DATEI EXISTIERT NICHT! {path}")
        if real_path.is_dir():
            return

        dest = str(pathlib.PurePosixPath(FTP_BASE_DIR, path.as_posix()))
        _create_dirs(str(path), client)

        print("[FTP]: UPLOAD", dest)
        client.storbinary("STOR " + dest, real_path.open("rb"))


def delete(path: str):
    with FTP() as client:
        client.set_pasv(False)
        client.connect(FTP_HOST, FTP_PORT)
        client.login(FTP_USER, FTP_PASS)

        dest = str(pathlib.PurePosixPath(
            FTP_BASE_DIR, pathlib.Path(path).as_posix()))
        print("[FTP]: DELETE", dest)
        client.delete(dest)


def _create_dirs(path: str, ftp: FTP):
    real_path = pathlib.Path(BASE_DIR, path)
    path = pathlib.Path(FTP_BASE_DIR, path).as_posix()
    if not real_path.exists():
        raise Exception(f"FILE {real_path} DOES NOT EXIST!")
        return
    if real_path.is_file():
        path = "/".join(list(filter(None, path.split("/")[:-1])))

    parts = list(filter(None, path.split("/")))
    not_exists = []
    for i in range(len(parts), 0, -1):
        check = "/"+"/".join(parts[0:i])
        try:
            ftp.sendcmd(f"MLST {check}")
        except error_perm:
            not_exists.append(check)
    for dir in not_exists[::-1]:
        print("[FTP]: MKDIR", dir)
        ftp.mkd(dir)
