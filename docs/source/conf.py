# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("."))
# Pro-tip to add the following line from
# https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/#fn-841-5
sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../.."))


# -- Project information -----------------------------------------------------

project = "PASEOS"
copyright = "2022"
author = "Pablo Gómez, Gabriele Meoni, Johan Östman, Vinutha Magal Shreenath"

# The full version, including alpha/beta/rc tags
release = "v0.1.3"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # for autodocs
    "sphinx.ext.napoleon",  # for numpy style documentation
    "myst_parser"  # for markdown support
    # "sphinx.ext.viewcode",
    # "sphinx.ext.imgmath",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"

# html_logo = "logo.jpg"

html_theme_options = {
    "logo_only": True,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_nav_header_background": "white",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
