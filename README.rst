========================================
HTTP Dynamix: A Dynamic HTTP Client Tool
========================================

A dynamic, intuitive HTTP client library for Python that provides a fluent interface 
for making HTTP requests.

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json
   :target: https://docs.astral.sh/ruff/
   :alt: Ruff Code Quality Badge

.. image:: https://img.shields.io/badge/Documentation-Built%20with%20Sphinx-blue?logo=read-the-docs&logoColor=white
   :target: https://www.sphinx-doc.org
   :alt: Documentation Built by Sphinx

.. image:: https://img.shields.io/badge/Project-Built%20with%20Hatchling-green?logo=python
   :target: https://hatch.pypa.io/latest/
   :alt: Project Built by Hatchling

.. image:: https://img.shields.io/pypi/v/http-dynamix.svg
   :target: https://pypi.org/project/http-dynamix
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/http-dynamix.svg
   :target: https://pypi.org/project/http-dynamix
   :alt: Python versions


Overview
--------
HTTP Dynamix is a modern HTTP client library built on top of HTTPX, offering a dynamic and intuitive API for making HTTP requests.
It provides both synchronous and asynchronous clients with a fluent interface that makes building and sending HTTP requests more natural and readable.

Features
--------
- **Dynamic Path Building**: Create URLs dynamically using attribute-style access
- **Multiple URL Formats**: Support for various URL segment formats (camel, kebab, snake case, etc.)
- **Type Safety**: Full type annotations and runtime type checking
- **Sync & Async Support**: Both synchronous and asynchronous clients
- **Logging**: Built-in structured logging with Loguru
- **Auth Support**: Built-in support for various authentication methods
- **Extensible**: Easy to extend and customize
- **Modern Python**: Built for Python 3.12+ with latest features
- **HTTPX Foundation**: Built on top of HTTPX for reliable HTTP operations
