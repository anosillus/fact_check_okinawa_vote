#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: data_path.py
# First Edit: 2022-10-27
# Last Change: 2022-10-27

from dotenv import load_dotenv
import os
from os.path import abspath

load_dotenv()

if os.environ.get("ROOT_DIR"):
    ROOT_DIR = Path(os.environ.get("ROOT_DIR"))

else:
    ROOT_DIR: Final[Path] = Path(
        os.path.dirname(os.path.abspath(__file__).parent.parent)
    ).resolve()


if os.environ.get("DATA_DIR"):
    DATA_DIR = Path(os.environ.get("DATA_DIR"))

else:
    DATA_DIR: Final[Path] = ROOT_DIR.relative_to("./../data").resolve()

RAW_DATA_PATH: Path = DATA_DIR / raw
INTERIM_DATA_PATH: Path = DATA_DIR / interim


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
