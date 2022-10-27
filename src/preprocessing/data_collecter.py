#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: data_setuper.py
# First Edit: 2022-10-16
# Last Change: 2022-10-16

from abc import ABCMeta, abstractmethod
from datetime import datetime
import hashlib
from itertools import groupby
import json
import logging
import operator
from pathlib import Path
import re
from re import Pattern
from typing import Final, NamedTuple, Optional, Any
from urllib.parse import urljoin
from zoneinfo import ZoneInfo
import statistics

from bs4 import BeautifulSoup
from pydantic import FileUrl, HttpUrl
import requests
from requests import RequestException, Response
import structlog
from structlog.processors import format_exc_info
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from .data_path import DATA_DIR, RAW_DATA_PATH, ROOT_DIR
from .data_type import FileInfo, LocalFileInfo

structlog.stdlib.recreate_defaults()


class DataCollecter(metaclass=ABCMeta):
    def __init__(self, catalog_url: HttpUrl):
        self.catalog_url = catalog_url
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.file_urls: list[HttpUrl] = []
        self.file_save_dir: Path

    def run(self) -> None:
        self.collect_target_urls()
        self.download_files()

    @abstractmethod
    def collect_target_urls(self) -> None:
        ...

    @staticmethod
    @abstractmethod
    def _download_file(file_url: HttpUrl, file_name: str) -> None:
        ...

    @abstractmethod
    def download_files(self) -> None:
        try:
            for file_info in list[FileInfo]:
                self._download_file(file_info.url, file_info.name)
        finally:
            self.save_log()

    @abstractmethod
    def save_log(self) -> None:
        ...


class OkinawaDataCollecter(DataCollecter):
    OKINAWA_TOUKEI_FILE_CATALOG_URL: Final[
        HttpUrl
    ] = "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"

    def __init__(self) -> None:
        super().__init__(self.OKINAWA_TOUKEI_FILE_CATALOG_URL)
        self.file_save_dir = RAW_DATA_PATH / str(datetime.date(datetime.today()))
        self.download_log: list[LocalFileInfo] = []

    def run(self) -> None:
        self.collect_target_urls()
        self.download_files()

    def collect_target_urls(self) -> None:
        response = self._requests_data_catalog_response()
        self.file_urls = self._parse_catalog_and_get_xls_file_urls(response)

    def _requests_data_catalog_response(self) -> Response:
        try:
            res = requests.get(self.catalog_url, timeout=5)
        except RequestException as err:
            self.logger.exception("catalog request failed with :%s", err.response.text)
        finally:
            self.logger.info("data catalog download finished!!")

        return res

    @staticmethod
    def _parse_catalog_and_get_xls_file_urls(res: Response) -> list[FileUrl]:
        def is_error_link_of_okinawa(link: str) -> bool:
            return link != "2019/pop201904r  (2).xls"

        return [
            urljoin(res.url, link.get("href"))
            for link in BeautifulSoup(res.text, "html.parser").find_all("a")
            if isinstance(link.get("href"), str)
            and link.get("href").endswith(".xls")
            and is_error_link_of_okinawa(link)
        ]

    def _download_file(self, file_url: HttpUrl, file_name: Path) -> None:
        response = requests.get(file_url, stream=True, timeout=10)
        with tqdm.wrapattr(
            open(str(self.file_save_dir / file_name), "wb"),
            "write",
            desc=file_name,
            dynamic_ncols=True,
            leave=False,
            miniters=1,
            total=int(response.headers.get("content-length", 0)),
            unit="B",
            unit_divisor=1024,
            unit_scale=True,
        ) as file:
            for chunk in response.iter_content(chunk_size=4096):
                file.write(chunk)

    def download_files(self) -> None:
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_logger.setLevel(logging.CRITICAL)
        self.file_save_dir.mkdir(exist_ok=True)
        file_info_chunk = self._make_file_info(self.file_urls)

        download_log: list[LocalFileInfo] = []

        try:
            for file_info in tqdm(file_info_chunk):
                self._download_file(file_url=file_info.url, file_name=file_info.name)
                download_log.append(self._make_local_info(file_info))

        except Exception as err:
            self.logger.info(
                "Stopped at files downloading.",
                trouble_file=file_info,
                file_dir=self.file_save_dir,
                message=err,
                download_log=download_log,
            )

        finally:
            self.save_log(download_log)

    def _make_local_info(self, file_info: FileInfo) -> LocalFileInfo:
        return LocalFileInfo(
            name=file_info.name,
            url=file_info.url,
            path=str(ROOT_DIR.relative_to(self.file_save_dir / file_info.name)),
            hash_value=self._sha256sum(self.file_save_dir / file_info.name),
            download_date=datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(),
        )

    @staticmethod
    def _sort_and_endict_info_chunk(
        info_chunk: list[LocalFileInfo],
    ) -> list[dict[str, Any]]:

        info_dicts = [i._asdict() for i in info_chunk]

        return sorted(info_dicts, key=operator.itemgetter("name"))

    def save_log(self, json_name="") -> None:
        if not json_name:
            json_name = "download_log_" + str(datetime.date(datetime.today())) + ".json"
        log_dicts = self._sort_and_endict_info_chunk(self.download_log)
        json_path = RAW_DATA_PATH / json_name

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(log_dicts, file)
            self.logger.info("save raw data as", file_path=json_path)

    @staticmethod
    def remove_file_name_noise(name: str) -> str:
        """remove_file_name_noise.

        :param name:
        :type name: str
        :rtype: str

        the name of okinawa statistics data file contains many noise and errors.
        this function remove the noise.
        (error file is removed by func of is_error_link_of_okinawa)
        """

        braket_pattern: Pattern = re.compile(r"\(.*?\)")
        # if "braket_pattern" not in globals():
        #     # pattern compiling takes time. To use again compilled data, globalize this value.
        #     # this braket_pattern transform 2010(1).xls into 2010.xls
        #     print('init')
        #     global braket_pattern
        #     braket_pattern: Pattern = re.compile(r"\(.*?\)")

        return (
            braket_pattern.sub("", name)
            .replace(" ", "")
            .replace("r", "")
            .replace("_1", "")
            .replace("pop", "")
        )

    def _make_file_info(self, xls_file_urls) -> list[FileInfo]:
        return [
            FileInfo(name=self.remove_file_name_noise(Path(url).name), url=url)
            for url in xls_file_urls
        ]

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


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
