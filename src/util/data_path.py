"""This module manage data directory paths"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(os.environ.get("ROOT_DIR"))
DATA_DIR = Path(os.environ.get("DATA_DIR"))

RAW_DATA_DIR: Path = Path(os.environ.get("RAW_DATA_DIR"))
INTERIM_DATA_DIR: Path = Path(os.environ.get("INTERIM_DATA_DIR"))
