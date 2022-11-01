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
