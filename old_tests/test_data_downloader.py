# -*- coding: utf-8 -*-
# File name: test_data_downloader.py
# First Edit: 2022-10-19
# Last Change: 2022-10-19
import filecmp
import json
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from requests_file import FileAdapter
from src.preprocessing.data_collecter import OkinawaDataCollecter
from src.preprocessing.data_path import RAW_DATA_DIR
from src.preprocessing.data_type import EventInfo


# def test_initial_catalog_url():
#     assert (
#         OkinawaDataCollecter().catalog_url
#         == "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"
#     )


# def test_requests_data_catalog_response():
#     assert OkinawaDataCollecter()._requests_data_catalog().ok


# def test_is_same_as_data_catalog_response_and_mock():
#     # when data catalog is updated, mock become old and this test will fail.
#     import codecs

#     with codecs.open(
#         Path("./tests/mock_data/response_mock_at_2022_10_25.txt"), "r", encoding="utf-8"
#     ) as response_text:

#         assert (
#             OkinawaDataCollecter()._requests_data_catalog().text == response_text.read()
#         )


# def test_parse_catalog_func_with_mock():
#     s = requests.Session()
#     s.mount("", FileAdapter())
#     with s.get(
#         Path("./tests/mock_data/response_mock_at_2022_10_25.txt").absolute().as_uri()
#     ) as mock_response:
#         assert 323 == len(OkinawaDataCollecter()._parse_catalog(mock_response))


# def test_compare_amount_of_mock_xls_files_with_current():
#     latest_response = OkinawaDataCollecter()._requests_data_catalog()
#     current_xls_file_urls = OkinawaDataCollecter._parse_catalog(latest_response)
#     assert 323 == len(current_xls_file_urls)


def test_compare_mock_xls_file_and_current():
    # TODO
    assert True


# def test_downloaded_file_contents():
#     trial_url = "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls"
#     with tempfile.NamedTemporaryFile() as tf:
#         OkinawaDataCollecter()._download_file(
#             file_url=trial_url, file_path=Path(tf.name)
#         )
#         assert filecmp.cmp(tf.name, Path("./tests/mock_data/pop202209.xls"))


def test_download_multi_files():
    test_file_urls = [
        "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        "https://www.pref.okinawa.jp/toukeika/estimates/1996/199601r.xls",
    ]
    dc = OkinawaDataCollecter()
    dc.file_urls = test_file_urls
    with tempfile.TemporaryDirectory() as td:
        dc.file_save_dir = Path(td)
        dc.json_dir = Path(td)
        dc.download_files()
        assert filecmp.cmp(
            Path(Path(td) / "pop202209.xls"), Path("./tests/mock_data/pop202209.xls")
        )
        assert filecmp.cmp(
            Path(Path(td) / "199601r.xls"), Path("./tests/mock_data/199601r.xls")
        )


# def test_save_log():
#     with tempfile.TemporaryDirectory(dir=str(RAW_DATA_DIR/"trial")) as td
#         dc = OkinawaDataCollecter()
#         dc.
#         dc.file_save_dir = Path(td)


# def test_save_download_log():
#     dc = OkinawaDataCollecter()
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


def test_event_log():
    dc = OkinawaDataCollecter()
    dc.file_save_dir = Path("./tests/mock_data").absolute()

    a = {
        "name": "pop202209.xls",
        "url": "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
    }
    expect = EventInfo(
        name="202209.xls",
        url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        path=str(Path("./tests/mock_data/pop202209.xls")),
        hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
        download_date="2022-10-26T02:18:51.375694+09:00",
    )

    assert expect.name == dc._shape_event_log(**a).name
    assert expect.url == dc._shape_event_log(**a).url
    assert expect.hash_value == dc._shape_event_log(**a).hash_value
    assert expect.path == dc._shape_event_log(**a).path
    assert expect.download_date != dc._shape_event_log(**a).download_date
    assert datetime.date(
        datetime.fromisoformat(dc._shape_event_log(**a).download_date)
    ) == datetime.date(datetime.today())


# def test_sha256sum():
#     hash_local_202209 = (
#         "b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac"
#     )
#     assert hash_local_202209 == OkinawaDataCollecter()._sha256sum(
#         Path("./tests/mock_data/pop202209.xls")
#     )


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
