import codecs
import datetime as dt
import filecmp
import json
import tempfile
from pathlib import Path
from typing import Optional

import requests
from requests_file import FileAdapter

from preprocessing.file_list_collect import FileListCollecter


def test_target_url():
    preset_url = FileListCollecter().catalog_url
    assert preset_url == "https://www.pref.okinawa.jp/toukeika/estimates/estidata.html"


def test_network_connection():
    fc = FileListCollecter()
    stable_url = "https://www.google.com"
    fc.catalog_url = stable_url
    fc.request_catalog_data()
    assert fc.res.ok


def test_requests_catalog_data():
    fc = FileListCollecter()
    fc.request_catalog_data()
    assert fc.res.ok


def test_collect_url_from_cataglo():
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
    with tempfile.NamedTemporaryFile(suffix="json") as tf:
        fc.result_path = Path(tf.name)
        fc.make_readable_dict()
        fc.write_url_data()
        value = json.load(open(tf.name))
    time_at_write = dt.datetime.fromisoformat(value.get("date"))
    assert dt.datetime.date(time_at_write) == dt.datetime.date(dt.datetime.today())
    assert value.get("urls") == mock_urls
