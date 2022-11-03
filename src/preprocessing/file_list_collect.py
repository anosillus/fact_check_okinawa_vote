"""set up file url list for downlaod xls files."""
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
from structlog import BoundLogger

from src.preprocessing.util import default_data_dir
from src.preprocessing.util import time_for_record
from src.preprocessing.util import today
from src.preprocessing.util import write_json_file


class FileListCollecter:
    def __init__(self, result_path: Path = None):
        self.catalog_url: Final[
            HttpUrl
        ] = "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.res: Response
        self.url_list: list[FileUrl]
        self.data_dict: dict[str, str | list[FileUrl]]

        if not result_path:
            result_path = default_data_dir() / ("url_list_at_" + today() + ".json")

        self.result_path = result_path

    def run(self) -> None:
        self.request_catalog_data()
        self.collect_url_from_catalog()
        self.make_readable_dict()
        self.write_url_data()

    def request_catalog_data(self) -> Response:
        try:
            self.res = requests.get(self.catalog_url, timeout=5)

        except RequestException as err:
            self.logger.exception("catalog request failed with :%s", err.response.text)

    def collect_url_from_catalog(self):
        """collect_url_from_catalog.

        :param self:

        parse catalog page response and collect xls file locations.
        this prosess also get rid of the inactive link included in okinawa data catalog.
        """

        def is_active_link_of_okinawa(link: str) -> bool:
            # "2019/pop201904r  (2).xls" is a dead link.

            return "(2).xls" not in link

        self.url_list: list[FileUrl] = [
            urljoin(self.res.url, link.get("href"))
            for link in BeautifulSoup(self.res.text, "html.parser").find_all("a")
            if isinstance(link.get("href"), str)
            and link.get("href").endswith(".xls")
            and is_active_link_of_okinawa(link)
        ]

    def make_readable_dict(self) -> None:
        self.data_dict: dict[str, str | list[FileUrl]] = {
            "date": time_for_record(),
            "urls": sorted(self.url_list),
        }

    def write_url_data(self):
        Path(self.result_path.parent).mkdir(exist_ok=True)

        write_json_file(
            json_path=self.result_path, data=self.data_dict, logger=self.logger
        )
