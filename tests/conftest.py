import os

import pytest
from dotenv import load_dotenv

from pyelexon import Elexon


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "cassette_library_dir": "tests/cassettes",
        "serializer": "json",
        "filter_query_parameters": ["APIKey"],
    }


@pytest.fixture
def api_key() -> str:
    """Load api key from .env file"""
    load_dotenv()
    return os.getenv("elexon_api_key")


@pytest.fixture
def client(api_key) -> Elexon:
    e = Elexon(api_key=api_key)
    return e
