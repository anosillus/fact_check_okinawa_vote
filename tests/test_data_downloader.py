#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: test_data_downloader.py
# First Edit: 2022-10-19
# Last Change: 2022-10-19
import requests
from requests_file import FileAdapter
from pathlib import Path
from src.preprocessing.data_collecter import OkinawaDataCollecter
import tempfile
import filecmp
from datetime import datetime
import json
from src.preprocessing.data_type import FileInfo, LocalFileInfo


def test_initial_catalog_url():
    assert (
        OkinawaDataCollecter().catalog_url
        == "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"
    )


def test_requests_data_catalog_response():
    assert OkinawaDataCollecter()._requests_data_catalog_response().ok


def test_data_catalog_response_contents():
    # when data catalog is updated, this test will fail.
    import codecs

    with codecs.open(
        Path("./tests/mock_data/response_mock_at_2022_10_25.txt"), "r", encoding="utf-8"
    ) as response_text:

        assert (
            OkinawaDataCollecter()._requests_data_catalog_response().text
            == response_text.read()
        )


def test_parse_xls_file_url_with_mock():
    s = requests.Session()
    s.mount("", FileAdapter())
    with s.get(
        Path("./tests/mock_data/response_mock_at_2022_10_25.txt").absolute().as_uri()
    ) as mock_response:
        assert 323 == len(
            OkinawaDataCollecter._parse_catalog_and_get_xls_file_urls(mock_response)
        )
    del s


def test_parse_xls_file_url_with_latest():
    latest_response = OkinawaDataCollecter()._requests_data_catalog_response()
    assert 323 == OkinawaDataCollecter._parse_catalog_and_get_xls_file_urls(
        latest_response
    )


def test_download_file():
    trial_url = "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls"
    with tempfile.NamedTemporaryFile() as ntf:
        OkinawaDataCollecter()._download_file(
            file_url=trial_url, local_file=Path(ntf.name)
        )
        filecmp.cmp(ntf.name, Path("./tests/mock_data/pop202209.xls"))


def test_download_files_tqdm():
    test_file_urls = [
        "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        "https://www.pref.okinawa.jp/toukeika/estimates/1996/199601r.xls",
    ]
    dc = OkinawaDataCollecter()
    dc.file_urls = test_file_urls
    with tempfile.TemporaryDirectory() as td:
        # with Path("./tests/mock_data/foo").absolute() as td:
        dc.save_file_dir = Path(td)
        dc.RAW_DATA_PATH = Path(td)
        dc.download_files()
        assert filecmp.cmp(
            Path(Path(td) / "202209.xls"), Path("./tests/mock_data/pop202209.xls")
        )
        assert filecmp.cmp(
            Path(Path(td) / "199601.xls"), Path("./tests/mock_data/199601r.xls")
        )


def test_save_download_log():
    dc = OkinawaDataCollecter()
    local_info = LocalFileInfo(
        name="pop202209.xls",
        url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        path=str(Path("./tests/mock_data/pop202209.xls")),
        hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
        download_date="2022-10-26T02:18:51.375694+09:00",
    )
    with tempfile.TemporaryDirectory() as td:
        dc.save_file_dir = Path(td)
        info_chunk = [local_info]
        dc._save_download_log(info_chunk, "data.json")
        with open(td + "/data.json") as data_file:
            assert json.load(data_file) == [local_info._asdict()]


def test_collect_local_file_info():
    dc = OkinawaDataCollecter()
    dc.save_file_dir = Path("./tests/mock_data")

    a = FileInfo(
        name="pop202209.xls",
        url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
    )
    expect = LocalFileInfo(
        name="pop202209.xls",
        url="https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls",
        path=str(Path("./tests/mock_data/pop202209.xls")),
        hash_value="b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac",
        download_date="2022-10-26T02:18:51.375694+09:00",
    )

    assert expect.name == dc._make_local_info(a).name
    assert expect.url == dc._make_local_info(a).url
    assert expect.hash_value == dc._make_local_info(a).hash_value
    assert expect.path == dc._make_local_info(a).path
    assert expect.download_date != dc._make_local_info(a).download_date
    assert datetime.date(
        datetime.fromisoformat(dc._make_local_info(a).download_date)
    ) == datetime.date(datetime.today())


def test_sha256sum():
    hash_local_202209 = (
        "b7b9fb4f75270c73bd3186ccce05877dd48ada3c4711c5bb34f46023a816bcac"
    )
    assert hash_local_202209 == OkinawaDataCollecter()._sha256sum(
        Path("./tests/mock_data/pop202209.xls")
    )


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
