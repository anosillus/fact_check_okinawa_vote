from pathlib import Path
from typing import Final
from typing import Optional
from urllib.parse import urljoin

import requests
import structlog
from bs4 import BeautifulSoup
from pydantic import FileUrl
from pydantic import HttpUrl
from requests import RequestException
from requests import Response

from src.preprocessing import util


def test_time_for_record():
    assert len(util.time_for_record()) == 25


def test_sha256sum():
    hash_local_202209 = (
        "b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac"
    )
    assert hash_local_202209 == util.sha256sum(
        Path("./tests/mock_data_at_2022_11_02/pop202209.xls")
    )


def test_write_json_file():
    ...
