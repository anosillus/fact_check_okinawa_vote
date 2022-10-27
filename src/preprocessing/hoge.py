#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: hoge.py
# First Edit: 2022-10-21
# Last Change: 2022-10-21
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

# pd.set_option("display.width", 40)
RAW_DATA_PATH: Final[Path] = Path("./../../data/raw/")

with open("./../../data/raw/file_log_2022-10-13.pickle", "rb") as f:
    local_file_info = pickle.load(f)

file_names = [
    RAW_DATA_PATH / str(i.download_date) / i.info.name for i in local_file_info
]


def remove_pattern(df, pattern):
    df.applymap(
        lambda cell_value: pattern.sub("", cell_value)
        if isinstance(cell_value, str)
        else cell_value
    )

    return df


# = file_names[0]
# b = pd.ExcelFile(a)
# c = b.sheet_names
# df = pd.read_excel(b, sheet_name=c[0], index_col=None, header=None)
# df = df.applymap(lambda x: neologdn.normalize(x) if isinstance(x, str) else x)
# all_alphabet_reg: Pattern = r"[^a-zA-Z]"
# all_alphabet_pattern: Pattern = re.compile(all_alphabet_reg)

# df = remove_pattern(df, all_alphabet_pattern)

# df = e.dropna(axis=0, how="all")


def find_value_data_positon(df):
    for side, col_str in enumerate(df.columns):
        for vert, value in enumerate(df[col_str]):
            if value == "県計":
                return (side, vert, True)

    return -1, -1, False


# side, vert = find_value_data_positon(df)
# print(df.iloc[vert, side])
# data = df.iloc[vert:, side + 1 :]
# print(data)

for name in file_names[141:]:
    excel_data = pd.ExcelFile(name)
    sheets = excel_data.sheet_names

    for sheet in sheets:
        df = pd.read_excel(excel_data, sheet_name=sheet, index_col=None, header=None)
        all_alphabet_reg: Pattern = r"[^a-zA-Z]"
        all_alphabet_pattern: Pattern = re.compile(all_alphabet_reg)
        df = remove_pattern(df, all_alphabet_pattern)
        df = df.dropna(axis=0, how="all").applymap(
            lambda x: neologdn.normalize(x) if isinstance(x, str) else x
        )

        side, vert, flag = find_value_data_positon(df)

        if flag:
            all_data = df.iloc[vert:, side + 1 :]
            data = df.iloc[vert, side + 1]

            if not np.isnan(data):
                print(data, all_data.shape)
            else:
                print(name)

            break

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
