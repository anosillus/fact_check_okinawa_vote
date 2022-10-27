#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: read_data.py
# First Edit: 2022-10-16
# Last Change: 2022-10-16

@dataclass
def main_info():
    TITLE_CITIES = "市町村名"
    TITLE_HOUSEHOLDS = "世帯数"
    TITLE_POPULATION = "現在人口"
    TITLE_ALL = "総数"
    TITLE_MALE = "男"
    TITLE_FEMALE = "女"
    TITLE_NET_CHANGE = "人口増減"
    TITLE_POPULATIO_DATA_TITLE = '市町村別人口総数及び世帯数'
    TITLE_POPULATION_CHANGE_TOTAL = "人口増減"
    TITLE_POPULATION_CHANGE = "人口増減"

    POPULATION_DATA = {TITLE_POPULATIO_DATA: [CITIES, POPULATION,NET_CHANGE]

    POPULATION_CHANGE = {TITLE_POPULATION_CHANGE: [NET_CHANGE, NATURAL,

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
