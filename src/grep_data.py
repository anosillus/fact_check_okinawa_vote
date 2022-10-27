#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: grep_data.py
# First Edit: 2022-10-13
# Last Change: 2022-10-13

import hashlib
import logging
import pickle
import re
from datetime import date, datetime
from itertools import groupby
from pathlib import Path
from re import Pattern
from typing import Final, NamedTuple, Optional
from urllib.parse import urljoin

import click
import requests
import structlog
from bs4 import BeautifulSoup
from pydantic import FileUrl, HttpUrl
from requests import RequestException, Response
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from data_type import FileInfo, LocalFileInfo

structlog.stdlib.recreate_defaults()
logger = structlog.stdlib.get_logger()


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
