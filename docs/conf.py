"""Sphinx configuration."""
project = "Fact Check Okinawa Vote Cheating"
author = "fact_check_usa"
copyright = "2022, fact_check_usa"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
