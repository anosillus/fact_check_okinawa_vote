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

from .util import default_data_dir
from .util import time_for_record
from .util import today
from .util import write_json_file


class FileListCollecter:
    def __init__(self):
        self.catalog_url: Final[
            HttpUrl
        ] = "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.res: Response
        self.url_list: list[FileUrl]
        self.data_dict: dict[str, str | list[FileUrl]]

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

            return link != "2019/pop201904r  (2).xls"

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

    def write_url_data(self, file_name: str = "", list_save_dir: Optional[Path] = None):
        if not list_save_dir:
            list_save_dir = default_data_dir()

        if not file_name:
            file_name = "url_list_at_" + today() + ".json"
        json_path = Path(list_save_dir) / file_name
        write_json_file(
            json_path=json_path, data_dict=self.data_dict, logger=self.logger
        )
