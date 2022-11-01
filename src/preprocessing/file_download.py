"""set up file url list for downlaod xls files."""
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
from typing import Optional
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
import structlog
from bs4 import BeautifulSoup
from pydantic import FileUrl
from pydantic import HttpUrl
from requests import RequestException
from requests import Response
from structlog import BoundLogger
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from .data_path import RAW_DATA_DIR
from .data_path import ROOT_DIR
from .data_type import EventInfo
from .util import default_data_dir
from .util import read_json_file
from .util import time_for_record
from .util import today
from .util import write_json_file


class FileDownloader:
    def __init__(self, urls_dict_path: Path ):
        self.urls_dict_path = urls_dict_path
        self.urls:lsit[FileUrl] = []
        self.file_place =
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.res: Response
        self.url_list: list[FileUrl]
        # self.data_dict: dict[str, str | list[FileUrl]]

    def run(self):
        self.dowload_files()

    def target_urls(self):
        urls_json_data = read_json_data(self.urls_dict_path)

        self.urls = urls_json_data.get("urls")
        self.logger.info("read json data",
                json_path=self.urls_dict_path,
                file_saved_date=urls_json_data.get("date"),
                urls_amount = len(self.urls))







    @staticmethod
    def _download_file(url: FileUrl, file_path:Path):
        res = requests.get(url, stream=True, timeout=10)
        with tqdm.wrapattr(
            open(file_path, "wb"),
            "write",
            desc=file_path.name,
            dynamic_ncols=True,
            leave=False,
            miniters=1,
            total=int(res.headers.get("content-length", 0)),
            unit="B",
            unit_divisor=1024,
            unit_scale=True,
        ) as file:
            for chunk in res.iter_content(chunk_size=4096):
                file.write(chunk)

    def download_files(self) -> None:
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_logger.setLevel(logging.CRITICAL)
        self.file_place.mkdir(exist_ok=True)

        try:
            for file_url in tqdm(self.file_urls):
                file_name = Path(file_url).name
                self._download_file(
                    file_url=file_url,
                    file_path=Path(self.file_place / file_name),
                )
                self.download_event_log.append(
                    self._shape_event_log(name=file_name, url=file_url)
                )

        except Exception as err:
            self.logger.info(
                "Stopped at files downloading.",
                trouble_file=file_name,
                file_place=self.file_place,
                message=err,
                download_event_log=self.download_event_log,
            )

        finally:
            self.save_log()
