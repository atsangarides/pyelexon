import logging
import xml.etree.ElementTree as ET
from datetime import date
from typing import Optional

import requests

from .configure_logging import setup_logger
from .errors import UnsuccessfulRequest
from .reports import Reports

logger = setup_logger(logging.getLogger("PyElexon"))


class Elexon:
    """
    Main object for interacting with the Elexon BMRS API and fetching the raw, xml
    response for individual settlement periods for the specified report.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_settlement(
        self,
        report: Reports,
        settlement_date: date,
        settlement_period: int,
        params: Optional[dict] = None,
    ) -> bytes:
        r = self._fetch_from_elexon(report, settlement_date, settlement_period, params)

        query = f"report={report},date={settlement_date},period={settlement_period}"

        self._check_errors(r, query)
        self._missing_data(r, query)
        return r.content

    def _fetch_from_elexon(
        self,
        report: Reports,
        settlement_date: date,
        settlement_period: int,
        params: Optional[dict] = None,
    ) -> requests.Response:

        if params is None:
            params = {}
        url = f"https://api.bmreports.com/BMRS/{report}/V1/"
        params.update(
            {
                "APIKey": self.api_key,
                "SettlementDate": settlement_date.strftime("%Y-%m-%d"),
                "SettlementPeriod": str(settlement_period),
                "ServiceType": "xml",
            }
        )
        response = requests.get(url, params=params)
        return response

    @staticmethod
    def _check_errors(r: requests.Response, query: str) -> None:
        # http response errors
        status_code = r.status_code
        if status_code != 200 or r.content is None:
            raise UnsuccessfulRequest(f"{query}: status_code={status_code}:{r.content}")

        # inspect xml response
        tree = ET.fromstring(r.content)
        response_meta = tree.find("./responseMetadata")
        http_code = int(response_meta.find("httpCode").text)

        if http_code != 200:
            error_type = response_meta.find("errorType").text
            error_desc = response_meta.find("description").text
            query = response_meta.find("queryString")
            logger.error(f"{query}: failed: type={error_type}, desc:{error_desc}")
            raise UnsuccessfulRequest(f"{query}: status_code={status_code}:{r.content}")

    @staticmethod
    def _missing_data(r: requests.Response, query: str):
        tree = ET.fromstring(r.content)
        if not tree.find("./responseBody/responseList/item/[id]"):
            logger.warning(f"{query}: No data found")
