"""This module is for util functions for preprocessing."""
import datetime as dt
import hashlib
import json
import operator
from pathlib import Path
from typing import Any
from typing import NamedTuple
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import FileUrl
from structlog.stdlib import BoundLogger

from .data_path import RAW_DATA_DIR
from .data_path import ROOT_DIR


class DownloadLog(NamedTuple):
    name: str
    url: str
    path: str
    hash_value: str
    download_date: str


def today():
    return str(dt.datetime.date(dt.datetime.today()))


def default_data_dir() -> Path:
    return RAW_DATA_DIR / today()


def time_for_record():
    return dt.datetime.now(ZoneInfo("Asia/Tokyo")).replace(microsecond=0).isoformat()


def write_json_file(
    json_path: Path, data_dict: dict[str, str], logger: BoundLogger = None
):
    with open(json_path, "w") as file:
        json.dump(data_dict, file)

        if logger:
            logger.info("save data as json", json_path=json_path)


def read_json_file(json_path: Optional[Path] = None):
    return json.load(open(json_path))


def sha256sum(file_path: Path) -> str:
    # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(file_path, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])

    return h.hexdigest()


# def sort_dicts_by_name(dicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
# return sorted(dicts, key=operator.itemgetter("name"))


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
