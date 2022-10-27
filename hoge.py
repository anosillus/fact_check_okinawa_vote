#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: hoge.py
# First Edit: 2022-10-21
# Last Change: 2022-10-21
import datetime
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

a = file_names[0]
b = pd.ExcelFile(a)
c = b.sheet_names
d = pd.read_excel(b, sheet_name=c[0], index_col=None, header=None)
e = d.applymap(lambda x: neologdn.normalize(x) if isinstance(x, str) else x)
f = e.dropna(axis=0, how="all")

for col_index, col_str in enumerate(f.columns):
    for vert_index, value in enumerate(f[col_str]):
        if value == "県計":
            print(f.iloc[vert_index, col_index])

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
