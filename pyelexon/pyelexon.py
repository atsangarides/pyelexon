import logging
import xml.etree.ElementTree as ET
from datetime import date
from typing import Optional

import requests

from .configure_logging import setup_logger
from .exceptions import InvalidApiKey, UnsuccessfulRequest
from .kwargs_mapping import kwargs_mapping

logger = setup_logger(logging.getLogger("PyElexon"))


class Elexon:
    """
    Main object for interacting with the Elexon BMRS API and fetching the raw, xml
    response for individual settlement periods for the specified report.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._register_get_methods()

    def _register_get_methods(self) -> None:
        """Register implemented reports and their corresponding methods with docs"""
        method_names = [attr for attr in dir(self) if attr.startswith("get_")]
        self.reports = [report.replace("get_", "").upper() for report in method_names]
        method_docs = [getattr(self, method).__doc__ for method in method_names]
        self.methods = dict(zip(method_names, method_docs))

    def fetch_data(self, report: str, params: Optional[dict] = None) -> bytes:
        """Retrieves the raw xml response from Elexon BMRS for the requested report"""
        if report not in self.reports:
            logger.warning(f"Provided report ({report}) not guaranteed to work")
        r = self._fetch_from_elexon(report, params)

        self._check_for_errors(r)
        self._missing_data(r, "./responseBody/responseList/item/[id]")
        return r.content

    def _fetch_from_elexon(
        self, report: str, params: Optional[dict] = None
    ) -> requests.Response:
        """Base get request"""
        if params is None:
            logger.warning("No params provided: defaults defined in BMRS User Guide")
            params = {}
        else:
            params = self._map_param_names(params)

        url = f"https://api.bmreports.com/BMRS/{report}/V1/"
        params.update(
            {
                "APIKey": self.api_key,
                "ServiceType": "xml",
            }
        )
        response = requests.get(url, params=params)
        self._check_for_errors(response)
        return response

    def get_detsysprices(self, settlement_date: date, settlement_period: int) -> bytes:
        """Method for fetching DETSYSPRICES data for the specified settlement period"""
        report = "DETSYSPRICES"
        params = {
            "settlement_date": self._date_fmt(settlement_date),
            "settlement_period": settlement_period,
        }
        r = self._fetch_from_elexon(report, params)
        self._missing_data(r, xpath="./responseBody/responseList/item/[id]")
        return r.content

    def get_dynbmdata(
        self,
        settlement_date: date,
        settlement_period: int,
        bm_unit_id: Optional[str] = None,
        bm_unit_type: Optional[str] = None,
        lead_party_name: Optional[str] = None,
        ngc_bm_unit_name: Optional[str] = None,
    ) -> bytes:
        """Method for fetching DYNBMDATA data for the specified settlement period"""
        report = "DYNBMDATA"
        params = {
            "settlement_date": self._date_fmt(settlement_date),
            "settlement_period": settlement_period,
            "bm_unit_id": bm_unit_id,
            "bm_unit_type": bm_unit_type,
            "lead_party_name": lead_party_name,
            "ngc_bm_unit_name": ngc_bm_unit_name,
        }
        r = self._fetch_from_elexon(report, params)
        return r.content

    def _check_for_errors(self, r: requests.Response) -> None:
        """Inspect the request response and the metadata in xml"""
        # http response errors
        status_code = r.status_code
        if status_code != 200 or r.content is None:
            raise UnsuccessfulRequest(f"status_code={status_code}:{r.content}")

        # inspect xml response
        tree = ET.fromstring(r.content)
        response_meta = tree.find("./responseMetadata")
        http_code = int(response_meta.find("httpCode").text)

        if http_code != 200:
            error_type = response_meta.find("errorType").text
            error_desc = response_meta.find("description").text
            query = response_meta.find("queryString").text
            if http_code == 204:
                logger.warning(
                    f"{query}: Data request was successful but no content was returned"
                )
            if http_code == 403 and error_desc == "An invalid API key has been passed":
                raise InvalidApiKey(f"{self.api_key} is not a valid API key")
            else:
                logger.error(f"{query}: failed: type={error_type}, desc:{error_desc}")
                raise UnsuccessfulRequest(
                    f"{query}: status_code={status_code}:{r.content}"
                )

    @staticmethod
    def _missing_data(r: requests.Response, xpath: str) -> None:
        """
        The Elexon API does not always report for missing data. An xpath can be used to
        try and return the items from the response and log if none were found
        """
        tree = ET.fromstring(r.content)
        query = tree.find("./responseMetadata/queryString").text
        if not tree.find(xpath):
            logger.warning(f"{query}: No data found")

    @staticmethod
    def _date_fmt(date_: date) -> str:
        return date_.strftime("%Y-%m-%d")

    @staticmethod
    def _map_param_names(params: dict) -> dict:
        return {kwargs_mapping.get(k): v for k, v in params.items() if v is not None}
