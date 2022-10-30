from pathlib import Path
from typing import NamedTuple

from pydantic import FileUrl


class EventInfo(NamedTuple):
    name: str
    url: FileUrl
    path: Path
    hash_value: str
    download_date: str
