#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: hoge.py
# First Edit: 2022-10-25
# Last Change: 2022-10-25

import requests
import wget

response = requests.get("https://www.pref.okinawa.jp/toukeika/estimates/estidata.html")
with open("./mock_data/response_mock_at_2022_10_25.txt", "w") as f:
    f.write(response.text)

file_url = "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls"
wget.download(file_url, out="./mock_data")

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
