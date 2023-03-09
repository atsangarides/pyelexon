import logging
from datetime import date

import pytest
import requests

from pyelexon.exceptions import UnsuccessfulRequest


@pytest.mark.vcr
def test_fetch_from_elexon(client):
    r = client._fetch_from_elexon("DETSYSPRICES")
    assert isinstance(r, requests.Response)


@pytest.mark.vcr
def test_fetch_data(client):
    params = {"settlement_date": "2021-01-01", "settlement_period": 1}
    r = client.fetch_data("DETSYSPRICES", params)
    assert isinstance(r, bytes)


@pytest.mark.vcr
def test_fetch_data_report_warning(caplog, client):
    report = "MKTDEPTHDATA"
    with caplog.at_level(logging.WARNING):
        _ = client.fetch_data(report)
    assert "not guaranteed to work" in caplog.text


@pytest.mark.vcr
def test_fetch_data_unsuccessful_request(caplog, client):
    with pytest.raises(UnsuccessfulRequest) as exc_info:
        params = {"settlement_date": "2021-01-01", "settlement_period": 1}
        _ = client.fetch_data("nosuchreport", params)
    assert "status_code=" in str(exc_info.value)


@pytest.mark.vcr
def test_get_detsysprices(client):
    r = client.get_detsysprices(settlement_date=date(2021, 1, 1), settlement_period=1)
    assert isinstance(r, bytes)


@pytest.mark.vcr
def test_detsysprices_missing_data_warning(caplog, client):
    with caplog.at_level(logging.WARNING):
        client.get_detsysprices(settlement_date=date(2031, 1, 1), settlement_period=1)
    assert "No data found" in caplog.text


@pytest.mark.vcr
def test_get_dersysdata(client):
    r = client.get_dersysdata(settlement_date=date(2021, 1, 1))
    assert isinstance(r, bytes)


@pytest.mark.vcr
def test_get_dersysdata_with_settlement_period(client):
    r = client.get_dersysdata(settlement_date=date(2021, 1, 1),
                              settlement_period=1)
    assert isinstance(r, bytes)


@pytest.mark.vcr
def test_get_lolpdrm(client):
    r = client.get_lolpdrm(settlement_date=date(2021, 1, 1))
    assert isinstance(r, bytes)


@pytest.mark.vcr
def test_get_dynbmdata(client):
    r = client.get_dynbmdata(settlement_date=date(2021, 1, 1), settlement_period=1)
    assert isinstance(r, bytes)


@pytest.mark.vcr
def test_get_phybmdata(client):
    r = client.get_phybmdata(settlement_date=date(2021, 1, 1), settlement_period=1)
    assert isinstance(r, bytes)
