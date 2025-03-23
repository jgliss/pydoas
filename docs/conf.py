import os
import sys
import matplotlib
from importlib.metadata import version as get_version

# Ensure matplotlib works in headless mode
if os.getenv("SPHINX_BUILD"):
    matplotlib.use('agg')

# Project information
project = "pydoas"
author = "Jonas Gliss"
copyright = "2016, Jonas Gliss"

# Versioning
try:
    version = get_version("pydoas")
except Exception as e:
    print(f"FAILED TO RETRIEVE PYDOAS VERSION. Reason: {e}")
    version = "0.0.0"

release = version

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.graphviz",
    "sphinx.ext.napoleon",  # Standard Napoleon
    "sphinx_autodoc_typehints",  # Improved type hints
]

# Paths
templates_path = ["_templates"]
exclude_patterns = ["_build"]

# Language
language = "en"

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": False,
    "special-members": "__init__",
    "show-inheritance": True,
}

# HTML output settings
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Intersphinx mappings
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}

# Custom function to handle skipping __init__
def skip(app, what, name, obj, skip, options):
    if name in {"__init__", "__call__"}:
        return False
    return skip

def setup(app):
    app.connect("autodoc-skip-member", skip)
