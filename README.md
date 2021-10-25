# pyelexon

Simple python wrapper for the Elexon BMRS API.

[![](https://img.shields.io/badge/python-3.8-blue.svg)](https://github.com/pyenv/pyenv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Getting started

* Register on the Elexon BMRS [data portal](https://www.elexonportal.co.uk/news/latest?cachebust=q3pzb5uiac)
and retrieve your `api_key`

* Example usage
```python
from datetime import date
from pyelexon import Elexon

api_key = "123456"
report = "DETSYSPRICES"
params = {
    "settlement_date": "2021-01-01",
    "settlement_period": 1
}

elexon = Elexon(api_key)
# returns content of response
r: bytes = elexon.fetch_data(report, params)
```
Example with report specific method
```python
from datetime import date
from pyelexon import Elexon

api_key = "123456"
report = "DETSYSPRICES"


elexon = Elexon(api_key)
# returns content of response
r: bytes = elexon.get_detsysprices(
    report,
    settlement_date=date(2021, 1, 1),
    settlement_period=1
)
```

## Tested reports

* `DETSYSPRICES`
* `DYNBMDATA`
