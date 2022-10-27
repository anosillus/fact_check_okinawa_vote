#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: arrange_data.py
# First Edit: 2022-10-27
# Last Change: 2022-10-27

import datetime
from os import remove
import neologdn
import hashlib
import logging
import pickle
import re
import unicodedata
from itertools import groupby
from pathlib import Path
from re import Pattern
from typing import Final, NamedTuple, Optional
from urllib.parse import urljoin

import click
import numpy as np
import pandas as pd
import requests
import structlog
from bs4 import BeautifulSoup
from pandas import Series
from pydantic import FileUrl, HttpUrl
from requests import RequestException, Response
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from data_type import FileInfo, LocalFileInfo
from data_path import DATA_PATH


RAW_DATA_PATH: Final[Path] = Path("./../data/raw/")


with open("./../data/raw/file_log_2022-10-13.pickle", "rb") as f:
    local_file_info = pickle.load(f)


file_names = [
    RAW_DATA_PATH / str(i.download_date) / i.info.name for i in local_file_info
]

name = file_names[141]
excel_data = pd.ExcelFile(name)
sheets = excel_data.sheet_names

sheet = sheets[0]
df = pd.read_excel(excel_data, sheet_name=sheet, index_col=None, header=None)


def find_value_data_positon(df):
    for side, col_str in enumerate(df.columns):
        for vert, value in enumerate(df[col_str]):
            if value == "県計":
                return (side, vert, True)

    return -1, -1, False


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
