import pytest

from pyelexon import Elexon
from pyelexon.exceptions import InvalidApiKey


@pytest.mark.vcr
def test_invalid_api_key():
    e = Elexon("haha")
    with pytest.raises(InvalidApiKey) as exc_info:
        params = {"settlement_date": "2021-01-01", "settlement_period": 1}
        _ = e.fetch_data("DETSYSPRICES", params)
    assert "is not a valid API key" in str(exc_info.value)
