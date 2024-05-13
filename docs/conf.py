"""This file is used to configure the Sphinx build of our documentation.
The documentation on setting this up is here: https://www.sphinx-doc.org/en/master/usage/configuration.html 
"""

# This is the standard readthedocs theme.
# import sphinx_rtd_theme
import sys, os

sys.path.insert(0, os.path.abspath("extensions"))

# What Sphinx extensions do we need
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx_markdown_tables",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "nbsphinx",
]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

html_theme = "sphinx_rtd_theme"

html_static_path = ["_build/html"]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

project = "SynSatiPy"

master_doc = "index"

# allow dropdowns
collapse_navigation = False


# # Include our custom CSS (currently for special table config)
# def setup(app):
#     app.add_css_file("theme_overrides.css")


# This should include all modules used in tobac. These are dummy imports,
# but should include both required and optional dependencies.
autodoc_mock_imports = [
    #    "numpy",
    "scipy",
    "pandas",
    "easygems",
    "healpy",
    "intake",
    "matplotlib",
    "xarray",
    "cartopy",
    "starter"
]

sys.path.insert(0, os.path.abspath("../"))

# Napoleon settings for configuring the Napoleon extension
# See documentation here:
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True
