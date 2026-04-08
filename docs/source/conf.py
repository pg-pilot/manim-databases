"""Sphinx configuration for manim-databases docs."""

from importlib.metadata import version as pkg_version

project = "manim-databases"
copyright = "2026, Breno Alberto"
author = "Breno Alberto"

try:
    release = pkg_version("manim-databases")
except Exception:
    release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "manim": ("https://docs.manim.community/en/stable/", None),
}

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
