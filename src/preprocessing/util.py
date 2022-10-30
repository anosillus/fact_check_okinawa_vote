"""This module is for util functions for preprocessing."""
from datetime import datetime
from pathlib import Path

from .data_path import RAW_DATA_DIR
from .data_path import ROOT_DIR


def today():
    return str(datetime.date(datetime.today()))


def default_save_dir() -> Path:
    return RAW_DATA_DIR / today()


# vim: ft=python ts=4 sw=4 sts=4 tw=88 fenc=utf-8 ff=unix si et:
