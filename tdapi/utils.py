"""Utility functions"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Union

from pydantic import BaseModel

# Constants
# ========================================================
PACKAGE_DIR = Path(__file__).parent.parent
SHORT_DATE_FORMAT = "%Y-%m-%d"
FREQUENCY_PATTERN = re.compile(r"(?P<frequency>\d*)(?P<frequency_unit>.*)")

# Helper Functions
# ========================================================
def load_json(filepath):
    with open(filepath) as f:
        obj = json.load(f)
    return obj


def save_json(obj, filepath, **kwargs):
    with open(filepath, "w") as f:
        if isinstance(obj, BaseModel):
            obj = obj.dict()
        json.dump(obj, f, **kwargs)


def remove_null_values(params):
    filtered_params = {}
    for key, value in params.items():
        if isinstance(value, dict):
            value = remove_null_values(value)

        if value is not None:
            filtered_params[key] = value

    return filtered_params


def parse_frequency_str(frequency_str):
    """
    Parses frequency string into frequency and frequency type.
    E.g. "5minute" returns ("5", "minute")
    "daily" returns ("1", "daily")
    """
    frequency_match = FREQUENCY_PATTERN.match(frequency_str)
    frequency = frequency_match.group("frequency") or "1"
    frequency_unit = frequency_match.group("frequency_unit")
    return frequency, frequency_unit


def date_to_millis(date: Union[datetime, str]):
    if isinstance(date, str):
        _date = short_date_to_datetime(date)
    else:
        _date = date
    return int(_date.timestamp() * 1000)


def short_date_to_datetime(short_date_str: str):
    return datetime.strptime(short_date_str, SHORT_DATE_FORMAT)


def millis_to_datetime(millis: int) -> datetime:
    return datetime.fromtimestamp(millis / 1000)
    

def millis_to_short_date(millis: int) -> str:
    dt = millis_to_datetime(millis)
    return datetime.strftime(dt, SHORT_DATE_FORMAT)
