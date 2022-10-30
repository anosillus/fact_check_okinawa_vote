"""DataCollecter is download statistics files from web and save download log.
OkinawaDataCollecter fix and remove noise data on the web.
"""
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
from .data_type import EventInfo

structlog.stdlib.recreate_defaults()


class DataCollecter(metaclass=ABCMeta):
    def __init__(self, catalog_url: HttpUrl):
        self.catalog_url = catalog_url
        self.file_urls: list[HttpUrl] = []
        self.file_save_dir: Path
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.download_event_log: list[EventInfo] = []
        self.json_dir: Path
        self.json_name: str = ""

    def collect_target_urls(self) -> None:
        response = self._requests_data_catalog()
        self.file_urls = self._parse_catalog(response)

    @staticmethod
    @abstractmethod
    def _parse_catalog(respons: Response) -> list[HttpUrl]:
        ...

    def _requests_data_catalog(self) -> Response:
        try:
            res = requests.get(self.catalog_url, timeout=5)
        except RequestException as err:
            self.logger.exception("catalog request failed with :%s", err.response.text)
        finally:
            self.logger.info("data catalog download finished!!")

        return res

    @staticmethod
    def _download_file(file_url: HttpUrl, file_path: Path) -> None:
        res = requests.get(file_url, stream=True, timeout=10)
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

    @abstractmethod
    def download_files(self) -> None:
        try:
            for file_url in self.file_urls:
                self._download_file(
                    file_url=file_url,
                    file_path=self.file_save_dir / Path(file_url).name,
                )
        finally:
            self.save_log()

    @staticmethod
    def _sort_dicts(info_dicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(info_dicts, key=operator.itemgetter("name"))

    @staticmethod
    def _info_chunk_to_dicts(
        info_chunk: list[EventInfo],
    ) -> list[dict[str, str]]:

        return [info._asdict() for info in info_chunk]

    @staticmethod
    def _sha256sum(file_path: Path) -> str:
        # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
        h = hashlib.sha256()
        b = bytearray(128 * 1024)
        mv = memoryview(b)
        with open(file_path, "rb", buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])

        return h.hexdigest()

    def save_log(self) -> None:
        log_dicts = self._sort_dicts(self._info_chunk_to_dicts(self.download_event_log))

        if not self.json_name:
            self.json_name = (
                "download_log_"
                + str(datetime.datetime.date(datetime.datetime.today()))
                + ".json"
            )

        json_file_path = self.json_dir / self.json_name

        with open(json_file_path, "w") as file:
            json.dump(log_dicts, file)
            self.logger.info("save raw data as", json_file_path=json_file_path)

    @abstractmethod
    def _shape_event_log(self, name, url) -> EventInfo:
        ...

    def run(self) -> None:
        self.collect_target_urls()
        self.download_files()


class OkinawaDataCollecter(DataCollecter):
    def __init__(self) -> None:
        self.OKINAWA_TOUKEI_FILE_CATALOG_URL: Final[
            HttpUrl
        ] = "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"

        super().__init__(self.OKINAWA_TOUKEI_FILE_CATALOG_URL)
        self.file_save_dir = RAW_DATA_DIR / str(
            datetime.datetime.date(datetime.datetime.today())
        )
        self.json_dir = RAW_DATA_DIR

    @staticmethod
    def _parse_catalog(res: Response) -> list[FileUrl]:
        def is_error_link_of_okinawa(link: str) -> bool:
            # remove this inactive link.

            return link != "2019/pop201904r  (2).xls"

        return [
            urljoin(res.url, link.get("href"))
            for link in BeautifulSoup(res.text, "html.parser").find_all("a")
            if isinstance(link.get("href"), str)
            and link.get("href").endswith(".xls")
            and is_error_link_of_okinawa(link)
        ]

    def _shape_event_log(self, name, url) -> EventInfo:
        file_path = Path(self.file_save_dir / name)
        try:
            path = str(file_path.relative_to(ROOT_DIR))
        except ValueError:
            path = str(file_path)

        return EventInfo(
            name=self._remove_catalog_file_name_noise(name),
            url=url,
            path=path,
            hash_value=self._sha256sum(file_path),
            download_date=datetime.datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
        )

    @staticmethod
    def _remove_catalog_file_name_noise(name: str) -> str:
        """_remove_catalog_file_name_noise.

        :param name:
        :type name: str
        :rtype: str

        the name of okinawa statistics data file contains many noise and errors.
        this function remove the noise.
        (error file is removed by func of is_error_link_of_okinawa)
        """

        braket_pattern: Pattern[str] = r"\(.*?\)"
        # re.compile is faster, but I don't use that for clean global scoope.
        # this braket_pattern transform 2010(1).xls into 2010.xls

        return (
            re.sub(pattern=braket_pattern, repl="", string=name)
            .replace(" ", "")
            .replace("r", "")
            .replace("_1", "")
            .replace("pop", "")
        )

    def download_files(self) -> None:
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_logger.setLevel(logging.CRITICAL)
        self.file_save_dir.mkdir(exist_ok=True)

        try:
            for file_url in tqdm(self.file_urls):
                file_name = Path(file_url).name
                self._download_file(
                    file_url=file_url,
                    file_path=Path(self.file_save_dir / file_name),
                )
                self.download_event_log.append(
                    self._shape_event_log(name=file_name, url=file_url)
                )

        except Exception as err:
            self.logger.info(
                "Stopped at files downloading.",
                trouble_file=file_name,
                file_dir=self.file_save_dir,
                message=err,
                download_event_log=self.download_event_log,
            )

        finally:
            self.save_log()


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
