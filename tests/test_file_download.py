import filecmp
import json
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from requests_file import FileAdapter

from src.preprocessing.file_download import FileDownloader


def test_downloaded_file_contents():
    trial_url = "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls"
    with tempfile.NamedTemporaryFile() as tf:
        FileDownloader()._download_file(file_url=trial_url, file_path=Path(tf.name))
        assert filecmp.cmp(tf.name, Path("./tests/mock_data/pop202209.xls"))


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
            Path(Path(td) / "pop202209.xls"), Path("./tests/mock_data/pop202209.xls")
        )
        assert filecmp.cmp(
            Path(Path(td) / "199601r.xls"), Path("./tests/mock_data/199601r.xls")
        )


# def test_sha256sum():
#     hash_local_202209 = (
#         "b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac"
#     )
#     assert hash_local_202209 == DataDownlaoder()._sha256sum(
#         Path("./tests/mock_data/pop202209.xls")
#     )


# def test_event_log():
#     dc = DataDownlaoder()
#     dc.file_save_dir = Path("./tests/mock_data").absolute()

#     a = {
#         "name": "pop202209.xls",
#         "url": "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
#     }
#     expect = EventInfo(
#         name="202209.xls",
#         url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
#         path=str(Path("./tests/mock_data/pop202209.xls")),
#         hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
#         download_date="2022-10-26T02:18:51.375694+09:00",
#     )

#     assert expect.name == dc._shape_event_log(**a).name
#     assert expect.url == dc._shape_event_log(**a).url
#     assert expect.hash_value == dc._shape_event_log(**a).hash_value
#     assert expect.path == dc._shape_event_log(**a).path
#     assert expect.download_date != dc._shape_event_log(**a).download_date
#     assert datetime.date(
#         datetime.fromisoformat(dc._shape_event_log(**a).download_date)
#     ) == datetime.date(datetime.today())


# def test_save_download_log():
#     dc = DataDownlaoder()
#     local_info = EventInfo(
#         name="202209.xls",
#         url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
#         path=str(Path("./tests/mock_data/pop202209.xls")),
#         hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
#         download_date="2022-10-26T02:18:51.375694+09:00",
#     )
#     with tempfile.TemporaryDirectory() as td:
#         dc.json_dir = Path(td)
#         dc.download_event_log = [local_info]
#         dc.json_name = "data.json"
#         dc.save_log()
#         with open(Path(td) / "data.json") as data_file:
#             assert json.load(data_file) == [local_info._asdict()]
