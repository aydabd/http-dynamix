"""Copyright (c) 2024, Aydin A.

This module is the entry point for the http_dynamix package. It imports the
version number and the logger from the log module. It also imports the
HttpClientFactory class from the client_factory module.
"""
from http_dynamix.factory import ClientFactory
from http_dynamix.enums import SegmentFormat, ClientType
from http_dynamix._version import version
from http_dynamix.auth import BearerAuth, ApiKeyAuth
from http_dynamix.log import log as logger, LogMaster
from http_dynamix.core import SegmentFormatter
from http_dynamix.clients import SyncClient, AsyncClient, AsyncDynamicClient, SyncDynamicClient


__all__ = [
    "ClientFactory",
    "ClientType",
    "SegmentFormat",
    "logger",
    "LogMaster",
    "version",
    "BearerAuth",
    "ApiKeyAuth"
    "SegmentFormatter",
    "BaseClient",
    "BaseDynamicClient",
    "SyncClient",
    "AsyncClient",
    "AsyncDynamicClient",
    "SyncDynamicClient"
]


__author__ = "Aydin Abdi"
__version__ = version
__license__ = "MIT"

