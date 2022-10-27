#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: foo.py
# First Edit: 2022-10-24
# Last Change: 2022-10-24
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
from pandas import DataFrame

import requests
import structlog
from bs4 import BeautifulSoup
from pandas import Series
from pydantic import FileUrl, HttpUrl
from requests import RequestException, Response
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from data_type import FileInfo, LocalFileInfo


RAW_DATA_PATH: Final[Path] = Path("./../../data/raw/")


with open("./../../data/raw/file_log_2022-10-13.pickle", "rb") as f:
    local_file_info = pickle.load(f)


file_names = [
    RAW_DATA_PATH / str(i.download_date) / i.info.name for i in local_file_info
]

# name = file_names[141]


def remove_noise(x: str | int):
    if not isinstance(x, str):
        return x
    x = neologdn.normalize(x)
    x = re.sub("[a-zA-Z]+", "", x)
    x = x.replace("-", "")
    x = x.replace("&", "")

    if x in ("()", ",", ".", ""):
        x = np.nan

    return x


FAMILY_NUMBER_JP = "市町村別人口総数及び世帯数"


def find_value_data_positon(df):
    for side, col_str in enumerate(df.columns):
        for vert, value in enumerate(df[col_str]):
            if value == "県計":
                return (side, vert, True)

    return -1, -1, False


def is_there_target_value(df: DataFrame, target_value: str):
    for side, col_str in enumerate(df.columns):
        for vert, value in enumerate(df[col_str]):
            if target_value in value:
                return True

    return False


for name in file_names:
    excel_data = pd.ExcelFile(name)
    sheets = excel_data.sheet_names
    count = 0

    for sheet in sheets:
        df = pd.read_excel(excel_data, sheet_name=sheet, index_col=None, header=None)
        df = df.dropna(axis=0, how="all").applymap(remove_noise)
        side, vert, flag = find_value_data_positon(df)

        if flag:
            # print(count)
            all_data = df.iloc[vert:, side + 1 :]
            data = df.iloc[vert, side + 1]

            if not np.isnan(data):
                # print(data, all_data.shape)

                if not is_there_target_value(df, FAMILY_NUMBER_JP):
                    # print("*" * 20)
                    # print(name, ":", sheet)
                    # print("*" * 20)
                else:
                    count += 1

            else:
                print(name)

        else:
            pass
            # print(flag)
            # print(name, ":", sheet)
    else:
        if not count != 1:
            print("Double", name)
        # print("=" * 20)
        # print(count, ":", name)
        # print("=" * 20)

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
