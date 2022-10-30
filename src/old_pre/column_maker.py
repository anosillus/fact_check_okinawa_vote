#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: column_maker.py
# First Edit: 2022-10-25
# Last Change: 2022-10-25

import hashlib
import logging
import pickle
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime
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
from structlog.processors import format_exc_info
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

structlog.stdlib.recreate_defaults()


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
