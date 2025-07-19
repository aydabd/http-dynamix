# -*- coding: utf-8 -*-
"""Configuration file for the Sphinx documentation builder for html or confluence.

This file only contains a selection of the most common options.

We need to have some environment variables set in the .env file to publish
the documentation to the Confluence server.

The environment variables that need to be set are:
- CONFLUENCE_SPACE_KEY: The space key where the documentation will be published
- CONFLUENCE_PARENT_PAGE: The name of the parent page where the documentation
                          will be published as a sub-page
- CONFLUENCE_SERVER_URL: The URL of the Confluence server
- CONFLUENCE_SERVER_USER: The user name to access the Confluence server
- CONFLUENCE_API_TOKEN: The API token to access the Confluence server

The environment variables can be set in the .env file or in the system environment.
The .env file should be in the root directory of the project.

The .env file should have the following content:
# Space key where the documentation will be published
# Space key can be found in the URL of the space in Confluence dashboard
CONFLUENCE_SPACE_KEY="<SPACE-KEY>" # e.g., "MYSPACE"
# Parent page where the documentation will be published as sub-page
# Parent page can be found in the URL of the page in Confluence dashboard
CONFLUENCE_PARENT_PAGE="<PARENT-PAGE-ID>" # e.g., "Documentations" or the unique page id
# Confluence server URL
CONFLUENCE_SERVER_URL="https://<CORPORATE-NAME>.atlassian.net/wiki/"
# Confluence server user name
CONFLUENCE_SERVER_USER="<user-name>"
# Confluence server API token
CONFLUENCE_API_TOKEN="generated-api-token-from-confluence-server"
"""
import inspect
import logging
import os
import sys
from pathlib import Path
import shutil
import sphinx

from dotenv import load_dotenv

# -- Logging configuration ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -- Load environment variables from .env file --------------------------------
load_dotenv()

# -- Environment variables ---------------------------------------------------
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "<SPACE-KEY>")
CONFLUENCE_PARENT_PAGE = os.getenv("CONFLUENCE_PARENT_PAGE", "<PARENT-PAGE-ID>")
CONFLUENCE_SERVER_URL = os.getenv(
    "CONFLUENCE_SERVER_URL", "https://<CORPORATE-NAME>.atlassian.net/wiki/"
)
CONFLUENCE_SERVER_USER = os.getenv("CONFLUENCE_SERVER_USER")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
# By default, the documentation is not published to Confluence
CONFLUENCE_PUBLISH = os.getenv("CONFLUENCE_PUBLISH", False)

# -- Add the project to the system path --------------------------------------
__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)
sys.path.insert(0, os.path.abspath(os.path.join(__location__, "src")))


# -- Project information -----------------------------------------------------
project = "Http Dynamix"
author = "Aydin Abdi"
copyright = "(c) 2025, Aydin Abdi"
author = "Aydin Abdi"
release = ""
version = ""

try:
    from http_dynamix import version
except ImportError:
    pass
else:
    release = version

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.confluencebuilder",
    "sphinx_rtd_theme",
    "sphinx.ext.autosectionlabel",
]

autosectionlabel_prefix_document = True
templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "_static/header.rst",
    "src/http_dynamix/__main__.py"
]
master_doc = "index"
source_suffix = {'.rst': 'restructuredtext'}
always_document_param_types = True
typehints_defaults = "braces-after"
autodoc_mock_imports = [""]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
pygments_style = "sphinx"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "canonical_url": "",
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "style_nav_header_background": "#2980b9",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
    # Custom sidebar templates, must be a dictionary that maps document names
    # to template names.
    "style_nav_header_background": "#2980b9",
}
html_show_sphinx = False
html_static_path = ["_static"]

# -- Options for Confluence output -------------------------------------------
confluence_publish = CONFLUENCE_PUBLISH
confluence_space_key = CONFLUENCE_SPACE_KEY
confluence_parent_page = CONFLUENCE_PARENT_PAGE
confluence_server_url = CONFLUENCE_SERVER_URL
confluence_api_token = CONFLUENCE_API_TOKEN
confluence_server_user = CONFLUENCE_SERVER_USER
confluence_root_homepage = False

# -- additional options conflunce output -------------------------------------
# confluence_page_generation_notice = True
confluence_publish_prefix = "[HTTP-DYNAMIX]-"
confluence_prev_next_buttons_location = "top"
confluence_global_labels = [
    "http-dynamix",
    "documentation",
    "python",
    "api-tests",
    "security",
    "confluence",
    "http-client",
    "httpx",
]
confluence_header_file = "_static/header.rst"
confluence_page_hierarchy = True
confluence_disable_autogen_title = True
confluence_version_comment = "Automatically generated."

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

def find_project_root() -> Path | None:
    """Find the project root directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return None


def convert_readme_to_markdown(force: bool = False) -> None:
    """Convert README.rst to README.md.

    This function is used to generate the README.md file from the README.rst file.
    The README.md file is generated in the root directory of the project.
    The README.md file is generated using the pandoc command.

    Args:
        force: The force flag
    """
    docs_dir = Path(__file__).resolve().parent
    project_root = find_project_root()

    # Add create_markdown.py to the python path
    if project_root:
        create_markdown_path = str(docs_dir)
        if create_markdown_path not in sys.path:
            sys.path.insert(0, create_markdown_path)

    try:
        from create_markdown import generate_readme

    except ImportError as e:
        error_message = f"Error during generating README.md: {e}"
        logger.error(error_message)
        return

    try:
        generate_readme(force=force)
    except Exception as e:
        error_message = f"Error during generating README.md: {e}"
        logger.error(error_message)


def run_apidoc(_) -> None:
    """Generate API documentation using Sphinx.

    This function is used to generate the API documentation using the Sphinx apidoc module. The API documentation is
    generated from the source code in the src directory. The generated API documentation is saved in the api directory.

    Args:
        _: The Sphinx application object.
    """
    from sphinx.ext import apidoc

    output_dir = os.path.abspath(os.path.join(__location__, "api"))
    module_dir = os.path.abspath(os.path.join(__location__, "..", "src", "http_dynamix"))

    try:
        shutil.rmtree(output_dir)
    except (FileNotFoundError, OSError):
        pass

    # Generate Api docs
    try:

        for module_dir in [module_dir]:
            cmd_line_template = f"sphinx-apidoc --implicit-namespaces --force --no-toc -o {output_dir} {module_dir}"
            args = cmd_line_template.split(" ")[1:]
            apidoc.main(args)
    except Exception as e:
        error_message = f"Error during generating API documentation: {e}"
        logger.error(error_message)

    convert_readme_to_markdown(force=True)


def skip_member(app, what, name, obj, skip, options) -> bool:
    """Skip members from the API documentation.

    This function is used to skip members from the some external libraries that are not needed in the documentation.
    Marshmallow library is used to serialize and deserialize data. The fields, load_fields, dump_fields, and exclude
    members are not needed in the documentation and are skipped.

    Args:
        app: The Sphinx application object.
        what: The type of the object.
        name: The name of the object.
        obj: The object.
        skip: The skip flag.
        options: The options.

    Returns:
        The skip flag.
    """
    if name in ("fields", "load_fields", "dump_fields", "exclude"):
        return True
    return skip


def setup(app) -> None:
    """Setup Sphinx extension.

    This function is used to setup the Sphinx extension. The function connects the builder-inited event to the
    run_apidoc function and the autodoc-skip-member event to the skip_member function.

    Args:
        app: The Sphinx application object.
    """
    app.connect("builder-inited", run_apidoc)
    app.connect("autodoc-skip-member", skip_member)

