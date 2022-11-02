"""set up file url list for download xls files."""
import logging
import operator
import re
from pathlib import Path
from re import Pattern

import requests
import structlog
from pydantic import FileUrl
from requests import RequestException
from structlog import BoundLogger
from tqdm.auto import tqdm

from .data_path import ROOT_DIR
from .util import default_data_dir
from .util import DownloadLog
from .util import read_json_file
from .util import sha256sum
from .util import time_for_record
from .util import today
from .util import write_json_file


class FileDownloader:
    def __init__(self, urls_dict_path: Path = None):
        self.urls_dict_path = urls_dict_path
        self.file_place: Path = default_data_dir()
        self.logger: BoundLogger = structlog.stdlib.get_logger()
        self.file_urls: list[FileUrl] = []
        self.download_logs: list[DownloadLog] = []
        self.download_log_path = Path(
            default_data_dir() / ("download_log_" + today() + ".json")
        )

    @staticmethod
    def _remove_file_name_noise(name: str) -> str:
        # This function remove the noise in name of okinawa statistics data files.
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

    @staticmethod
    def _download_file(file_url: FileUrl, file_path: Path) -> None:
        res = requests.get(file_url, stream=True, timeout=20)
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

    @staticmethod
    def _shape_log(name, url, path) -> DownloadLog:
        try:
            relpath = path.relative_to(ROOT_DIR)
        except ValueError:
            relpath = path

        return DownloadLog(
            name=name,
            url=url,
            path=str(relpath),
            hash_value=sha256sum(path),
            download_date=time_for_record(),
        )

    def run(self) -> None:
        self.read_target_urls()
        self.download_files()

    def read_target_urls(self) -> None:
        urls_json_data = read_json_file(self.urls_dict_path)

        self.file_urls = urls_json_data.get("urls")
        self.logger.info(
            "result of json data read",
            json_path=self.urls_dict_path,
            file_downloaded_date=urls_json_data.get("date"),
            urls_amount=len(self.file_urls),
        )

    def download_files(self, is_write_log=True) -> None:
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_logger.setLevel(logging.CRITICAL)
        self.file_place.mkdir(exist_ok=True)

        try:
            for file_url in tqdm(self.file_urls):
                file_name = Path(file_url).name
                file_path = Path(self.file_place / file_name)

                self._download_file(file_url=file_url, file_path=file_path)

                if is_write_log:
                    name = self._remove_file_name_noise(file_name)

                    self.download_logs.append(
                        self._shape_log(name=name, url=file_url, path=file_path)
                    )

        except RequestException as err:
            self.logger.info(
                "Stopped at files downloading.",
                trouble_file=file_name,
                file_place=self.file_place,
                message=err,
                download_logs=self.download_logs,
            )

        finally:
            if is_write_log:
                self._write_log()

    def _write_log(self):
        data_dicts: list[dict[str, str]] = [
            info._asdict() for info in self.download_logs
        ]
        data_dicts = sorted(data_dicts, key=operator.itemgetter("name"))

        write_json_file(
            json_path=self.download_log_path, data_dict=data_dicts, logger=self.logger
        )
