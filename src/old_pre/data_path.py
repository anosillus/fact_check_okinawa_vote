"""
data path list.
"""
import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(os.environ.get("ROOT_DIR")).absolute()
DATA_DIR = Path(os.environ.get("DATA_DIR")).absolute()

RAW_DATA_DIR: Path = Path(os.environ.get("RAW_DATA_DIR")).absolute()
INTERIM_DATA_DIR: Path = Path(os.environ.get("INTERIM_DATA_DIR")).absolute()


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et: