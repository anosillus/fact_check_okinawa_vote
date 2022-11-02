import codecs
import datetime as dt
import filecmp
import json
import tempfile
from pathlib import Path
from typing import Optional

import requests
from requests_file import FileAdapter
from src.preprocessing.file_list_collect import FileListCollecter


def test_target_url():
    preset_url = FileListCollecter().catalog_url
    assert preset_url == "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"


def test_network_connection():
    fc = FileListCollecter()
    stable_url = "https://www.google.com"
    fc.catalog_url = stable_url
    fc.request_catalog_data()
    assert fc.res.ok


def test_is_connectable_target():
    fc = FileListCollecter()
    fc.request_catalog_data()
    assert fc.res.ok


def test_parser_with_mock_data():
    s = requests.Session()
    s.mount("", FileAdapter())
    with s.get(
        Path("./tests/mock_data_at_2022_11_02/response_mock.txt").absolute().as_uri()
    ) as mock_response:
        fc = FileListCollecter()
        fc.res = mock_response
        fc.collect_url_from_catalog()
        assert len(fc.url_list) == 323


def test_target_data_parsing():
    fc = FileListCollecter()
    fc.request_catalog_data()
    fc.collect_url_from_catalog()
    assert 500 > len(fc.url_list) >= 323


def test_is_parse_results_contents_include_old_ones():
    # TODO
    ...


def test_write_parser_results():
    fc = FileListCollecter()
    mock_urls = ["https://www.amazon.com", "https://www.google.com"]

    fc.url_list = mock_urls
    with tempfile.TemporaryDirectory() as list_save_dir:
        file_name = "hoge.json"
        fc.make_readable_dict()
        fc.write_url_data(file_name=file_name, list_save_dir=list_save_dir)
        json_path = Path(list_save_dir) / file_name
        value = json.load(open(json_path))
    time_at_write = dt.datetime.fromisoformat(value.get("date"))
    assert dt.datetime.date(time_at_write) == dt.datetime.date(dt.datetime.today())
    assert value.get("urls") == mock_urls
