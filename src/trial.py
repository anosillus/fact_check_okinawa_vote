#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File name: trial.py
# First Edit: 2022-10-11
# Last Change: 2022-10-11

from typing import NamedTuple
from pandas_estat import read_statslist
from dotenv import load_dotenv
from collections import namedtuple
from pydantic import HttpUrl

load_dotenv()

Stats = namedtuple('Stats', ['name', 'code', 'cycle'])

class StatsInfo(NamedTuple):
    name: str
    code: str
    cycle: str
    url: Optional[HttpUrl] = None

Internal_Migration_Stats = Stats("住民基本台帳人口移動報告", "00200523", "月次")
read_statslist(Internal_Migration_Stats.code)

df[[TABLE_INF','TABULATION_SUB_CATEGORY1',
       'TABULATION_SUB_CATEGORY2', 'TABULATION_SUB_CATEGORY3',
       'TABULATION_SUB_CATEGORY4', 'TABULATION_SUB_CATEGORY5',
       'TABULATION_CATEGORY_EXPLANATION',
       'TABULATION_SUB_CATEGORY_EXPLANATION1',
       'TABULATION_SUB_CATEGORY_EXPLANATION2',
       'TABULATION_SUB_CATEGORY_EXPLANATION3',
       'TABULATION_SUB_CATEGORY_EXPLANATION4',
       'TABULATION_SUB_CATEGORY_EXPLANATION5', 'NO', 'TITLE',
       'TABLE_EXPLANATION', 'TABLE_CATEGORY', 'TABLE_SUB_CATEGORY1',
       'TABLE_SUB_CATEGORY2', 'TABLE_SUB_CATEGORY3', 'CYCLE', 'SURVEY_DATE',
       'OPEN_DATE', 'SMALL_AREA', 'COLLECT_AREA', 'OVERALL_TOTAL_NUMBER',
       'UPDATED_DATE', 'MAIN_CATEGORY_CODE', 'MAIN_CATEGORY',
       'SUB_CATEGORY_CODE', 'SUB_CATEGORY']

# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:

