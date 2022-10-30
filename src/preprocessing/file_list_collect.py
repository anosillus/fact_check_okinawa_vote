import datetime
import hashlib
import json
import logging
import operator
import os
import re
from abc import ABCMeta
from abc import abstractmethod
from pathlib import Path
from re import Pattern
from typing import Any
from typing import Final
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
import structlog
from bs4 import BeautifulSoup
from pydantic import FileUrl
from pydantic import HttpUrl
from requests import RequestException
from requests import Response
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from .data_path import RAW_DATA_DIR
from .data_path import ROOT_DIR
from .util import default_save_dir


class FileListCollecter:
    def __init__(self):
        self.catalog_url: Final[
            HttpUrl
        ] = "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.save_dir: Path = default_save_dir()
        self.res: Response
        self.url_list: list[FileUrl]

    def request_catalog_data(self) -> Response:
        try:
            self.res = requests.get(self.catalog_url, timeout=5)
        except RequestException as err:
            self.logger.exception("catalog request failed with :%s", err.response.text)

    def collect_url_from_catalog(self):
        def is_inactive_link_of_okinawa(link: str) -> bool:
            # check if the link is inactive one.

            return link != "2019/pop201904r  (2).xls"

        self.url_list = [
            urljoin(self.res.url, link.get("href"))
            for link in BeautifulSoup(self.res.text, "html.parser").find_all("a")
            if isinstance(link.get("href"), str)
            and link.get("href").endswith(".xls")
            and is_inactive_link_of_okinawa(link)
        ]

    def save_file_list(self):
        self.save_dir.mkdir(exist_ok=True)
