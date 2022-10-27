#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: downlaod_data.py
# First Edit: 2022-10-13
# Last Change: 2022-10-13

import hashlib
import logging
import pickle
import re
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
from structlog.stdlib import BoundLogger
from tqdm.auto import tqdm

from data_type import FileInfo, LocalFileInfo

structlog.stdlib.recreate_defaults()
logger = structlog.stdlib.get_logger()

OKINAWA_TOUKEI_LIST_URL: Final[
    HttpUrl
] = "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"

RAW_DATA_PATH: Final[Path] = Path("./../data/raw/")


def requests_data_catalog(url: HttpUrl, logger: BoundLogger = logger):
    try:
        response = requests.get(url, timeout=3)
    except RequestException as err:
        response.raise_for_status()
        logger.exception("request failed.", error=err.response.text)
    finally:
        logger.info("data catalog download success!!")

    return response


def parse_xls_file_url(res: Response, logger: BoundLogger = logger) -> list[FileUrl]:
    return [
        urljoin(res.url, link.get("href"))
        for link in BeautifulSoup(res.text, "html.parser").find_all("a")
        if isinstance(link.get("href"), str)
        and link.get("href").endswith(".xls")
        and link != "2019/pop201904r  (2).xls"
    ]
    # > link != "2019/pop201904r  (2).xls"
    # this file is broken. But "pop201904r  (3).xl" works. Fuck.


def normalize_target_file_name(xls_file_urls):
    braket_pattern: Pattern = re.compile(r"\(.*?\)")
    # transform 2010(1).xls and 2010(2).xls into double 2020.xls. (both contents are identical)

    return [
        FileInfo(
            name=Path(
                braket_pattern.sub("", url)
                .replace(" ", "")
                .replace("r", "")
                .replace("_1", "")
                .replace("pop", "")
            ).name,
            url=url,
        )
        for url in xls_file_urls
    ]


#  "201904" files are many. But only "2019/pop201904r  (3).xls" is collect. I select (3) by hand. so this function become useless.
# def deduplicate_info(duplicated_info: list[FileInfo], logger: BoundLogger = logger):
#     return  [
#         next(unique) for _, unique in groupby(duplicated_info, key=lambda x: x.name)
#     ]


def sha256sum(file_name) -> str:
    # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(file_name, "rb", buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])

    return h.hexdigest()


def download_file(url: str, file_name: str, chunk_size=1024):
    response = requests.get(url, stream=True)
    with tqdm.wrapattr(
        open(file_name, "wb"),
        "write",
        desc=file_name.replace("/", " ").split()[-1],
        dynamic_ncols=True,
        leave=False,
        miniters=1,
        total=int(response.headers.get("content-length", 0)),
        unit="B",
        unit_divisor=1024,
        unit_scale=True,
    ) as fout:
        for chunk in response.iter_content(chunk_size=4096):
            fout.write(chunk)


def downlaod_all_data(chunk_of_file_info):
    urllib3_logger = logging.getLogger("urllib3")
    urllib3_logger.setLevel(logging.CRITICAL)
    today = datetime.date(datetime.today())
    save_dir = RAW_DATA_PATH / str(today)
    save_dir.mkdir(exist_ok=True)

    chunk_of_local_file_info: list[LocalFileInfo] = []

    for file_info in tqdm(chunk_of_file_info):
        file_name = str(save_dir / file_info.name)
        download_file(file_info.url, file_name)
        chunk_of_local_file_info.append(
            LocalFileInfo(
                info=file_info, hash_value=sha256sum(file_name), download_date=today
            )
        )

    return chunk_of_local_file_info


def save_downloaded_log(
    chunk_of_local_file_info: list[LocalFileInfo], logger: BoundLogger = logger
) -> None:
    pickle_name = str(
        Path(
            RAW_DATA_PATH
            / ("file_log_" + str(datetime.date(datetime.today())) + ".pickle")
        )
    )
    chunk_of_local_file_info = sorted(
        chunk_of_local_file_info, key=lambda x: x.info.name
    )
    with open(pickle_name, "wb") as fp:  # Pickling
        pickle.dump(chunk_of_local_file_info, fp)
        logger.info("save raw data as", file_name=pickle_name)


data_catalog_response = requests_data_catalog(OKINAWA_TOUKEI_LIST_URL)
xls_file_urls = parse_xls_file_url(data_catalog_response)
chunk_of_file_info = normalize_target_file_name(xls_file_urls)
chunk_of_local_file_info = downlaod_all_data(chunk_of_file_info)
save_downloaded_log(chunk_of_local_file_info)
