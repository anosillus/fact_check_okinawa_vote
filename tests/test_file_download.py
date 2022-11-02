import filecmp
import json
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from preprocessing.util import DownloadLog
from requests_file import FileAdapter

from src.preprocessing.file_download import FileDownloader


def test_downloaded_file_contents():
    trial_url = "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls"
    with tempfile.NamedTemporaryFile() as tf:
        FileDownloader()._download_file(file_url=trial_url, file_path=Path(tf.name))
        assert filecmp.cmp(
            tf.name, Path("./tests/mock_data_at_2022_11_02/pop202209.xls")
        )


def test_download_multi_files():
    test_file_urls = [
        "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        "https://www.pref.okinawa.jp/toukeika/estimates/1996/199601r.xls",
    ]
    fd = FileDownloader()
    fd.file_urls = test_file_urls
    with tempfile.TemporaryDirectory() as td:
        fd.file_place = Path(td)
        fd.download_files(is_write_log=False)
        assert filecmp.cmp(
            Path(Path(td) / "pop202209.xls"),
            Path("./tests/mock_data_at_2022_11_02/pop202209.xls"),
        )
        assert filecmp.cmp(
            Path(Path(td) / "199601r.xls"),
            Path("./tests/mock_data_at_2022_11_02/199601r.xls"),
        )


def test_event_log():
    a = {
        "name": "202209.xls",
        "url": "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        "path": Path(Path("./tests/mock_data_at_2022_11_02/pop202209.xls").resolve()),
    }
    expect = DownloadLog(
        name="202209.xls",
        url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        path=str(Path("./tests/mock_data_at_2022_11_02/pop202209.xls")),
        hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
        download_date="2022-10-26T02:18:51.375694+09:00",
    )

    assert expect.name == FileDownloader()._shape_log(**a).name
    assert expect.url == FileDownloader()._shape_log(**a).url
    assert expect.hash_value == FileDownloader()._shape_log(**a).hash_value
    assert expect.path == FileDownloader()._shape_log(**a).path
    assert expect.download_date != FileDownloader()._shape_log(**a).download_date
    assert datetime.date(
        datetime.fromisoformat(FileDownloader()._shape_log(**a).download_date)
    ) == datetime.date(datetime.today())


def test_write_log():
    fc = FileDownloader()
    a_log = DownloadLog(
        name="202209.xls",
        url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        path=str(Path("./tests/mock_data_at_2022_11_02/pop202209.xls")),
        hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
        download_date="2022-10-26T02:18:51.375694+09:00",
    )
    with tempfile.NamedTemporaryFile(suffix=".json") as tf:
        fc.download_log_path = Path(tf.name)
        fc.download_logs = [a_log]
        fc._write_log()
        with open(tf.name) as name:
            assert json.load(name) == [a_log._asdict()]
