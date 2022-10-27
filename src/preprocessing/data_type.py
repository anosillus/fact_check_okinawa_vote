from typing import NamedTuple

from pydantic import FileUrl
from pathlib import Path


class FileInfo(NamedTuple):
    name: str
    url: FileUrl


class LocalFileInfo(NamedTuple):
    name: str
    url: FileUrl
    path: Path
    hash_value: str
    download_date: str
