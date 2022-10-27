"""
data path list.
"""

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

if os.environ.get("ROOT_DIR"):
    ROOT_DIR = Path(os.environ.get("ROOT_DIR"))

else:
    ROOT_DIR: Final[Path] = Path(
        os.path.dirname(os.path.abspath(__file__))
    ).parent.parent.resolve()


if os.environ.get("DATA_DIR"):
    DATA_DIR = Path(os.environ.get("DATA_DIR"))

else:
    DATA_DIR: Final[Path] = ROOT_DIR.relative_to("./../data").resolve()

RAW_DATA_PATH: Path = DATA_DIR / "raw"
INTERIM_DATA_PATH: Path = DATA_DIR / "interim"


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
