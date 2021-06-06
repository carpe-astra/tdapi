"""Client for accessing the TD Ameritrade API"""

from datetime import date, datetime
from typing import Dict, List, Union

import requests
from loguru import logger

from tdapi.config import UserConfig, user_config
from tdapi.models.auth import EASObject
from tdapi.utils import (PACKAGE_DIR, date_to_millis, load_json,
                         parse_frequency_str, remove_null_values, save_json)

# Constants
# ========================================================
VALID_FREQUENCY_TYPES = ("minute", "daily", "weekly", "monthly")


# Helper Classes
# ========================================================
class BadStatusCode(Exception):
    def __init__(self, resp, expected_status_codes):
        self.resp = resp
        self.expected_status_codes = expected_status_codes
        try:
            resp_json = resp.json()
        except:
            resp_json = None
        super().__init__(
            f"Expected status codes: {expected_status_codes}. Received status code: {resp.status_code}.\nJSON: {resp_json}"
        )


# Base Client Object
# ========================================================
class TDClient(requests.Session):
    base_url = "https://api.tdameritrade.com"
    eas_json_filepath = PACKAGE_DIR / "eas.json"
    eas_object: EASObject = EASObject()

    def __init__(self):
        super().__init__()

        self.user_config: UserConfig = user_config
        eas_dict = load_json(self.eas_json_filepath)
        self.update_eas_object(eas_dict)

    def _get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def _post(self, url, **kwargs):
        return self._request("POST", url, **kwargs)

    def _put(self, url, **kwargs):
        return self._request("PUT", url, **kwargs)

    def _patch(self, url, **kwargs):
        return self._request("PATCH", url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._request("DELETE", url, **kwargs)

    def _request(self, method, url, **kwargs):
        try:
            resp = self.request(method, url, **kwargs)

            # handle re-auth
            if resp.status_code == 401:
                logger.debug("Received unauthenticated status. Reauthenticating...")
                self.authenticate()
                resp = self.request(method, url, **kwargs)

        except Exception as e:
            logger.exception("Error handling TD API request")
            raise e

        return resp

    # Helper functions
    # ========================================================
    @staticmethod
    def validate_status(
        resp: requests.Response, expected_status_codes: Union[List, int]
    ):
        if isinstance(expected_status_codes, int):
            expected_status_codes = [expected_status_codes]

        if resp.status_code not in expected_status_codes:
            raise BadStatusCode(resp, expected_status_codes)

    def update_eas_object(self, eas_dict):
        _eas_dict = self.eas_object.dict()
        _eas_dict.update(eas_dict)
        self.eas_object = EASObject(**_eas_dict)
        self.headers.update({"Authorization": f"Bearer {self.eas_object.access_token}"})
        save_json(self.eas_object, self.eas_json_filepath, indent=2)

    def authenticate(self):
        logger.debug("Authenticating session...")

        if self.eas_object is None:
            try:
                eas_dict = load_json(self.eas_json_filepath)
                eas_object = EASObject(**eas_dict)

            except FileNotFoundError as e:
                logger.critical(f"{self.eas_json_filepath} not found.")
                raise e

        else:
            eas_object = self.eas_object

        try:
            eas_dict = self._post_access_token(
                grant_type="refresh_token",
                refresh_token=eas_object.refresh_token,
                access_type=None,
                code=None,
                client_id=self.user_config.consumer_key,
                redirect_uri=None,
            )

        except Exception as e:
            logger.exception("Error while posting access token")
            raise e

        self.update_eas_object(eas_dict)

    # Low Level API
    # ========================================================
    """Accounts and Trading"""

    def _get_account(self, fields: List[str] = []):
        route = self.base_url + f"/v1/accounts/{self.user_config.account_id}"

        params = {"fields": ",".join(fields)}

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)

        return resp.json()

    """Authentication"""

    def _post_access_token(
        self,
        grant_type: str,
        refresh_token: str,
        access_type: str,
        code: str,
        client_id: int,
        redirect_uri: str,
    ):
        logger.debug("Posting access token")

        route = self.base_url + "/v1/oauth2/token"

        params = {
            "grant_type": grant_type,
            "refresh_token": refresh_token,
            "access_type": access_type,
            "code": code,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
        }
        params = remove_null_values(params)

        resp = requests.post(route, data=params)
        self.validate_status(resp, 200)

        return resp.json()

    """Instruments"""

    """Market Hours"""

    """Movers"""

    """Option Chains"""

    """Price History"""

    def _get_price_history(
        self,
        symbol: str,
        apikey: str = None,
        periodType: str = None,
        period: int = None,
        frequencyType: str = None,
        frequency: int = None,
        endDate: str = None,
        startDate: str = None,
        needExtendedHoursData: bool = True,
    ):
        route = self.base_url + f"/v1/marketdata/{symbol}/pricehistory"

        params = {
            "apikey": apikey,
            "periodType": periodType,
            "period": period,
            "frequencyType": frequencyType,
            "frequency": frequency,
            "endDate": endDate,
            "startDate": startDate,
            "needExtendedHoursData": needExtendedHoursData,
        }

        params = remove_null_values(params)

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)

        return resp.json()

    """Quotes"""

    def _get_quotes(self, symbols: List[str], apikey: str = None):
        route = self.base_url + "/v1/marketdata/quotes"

        params = {"apikey": apikey, "symbol": ",".join(symbols)}

        params = remove_null_values(params)

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)

        return resp.json()

    """Transaction History"""

    """User Info and Preferences"""

    """Watchlist"""

    # High Level API
    # ========================================================
    def get_price_history(
        self,
        symbol: str,
        frequency: str,
        start_date: Union[datetime, str],
        end_date: Union[datetime, str],
        include_extended_hours: bool = False,
    ):
        freq, freq_type = parse_frequency_str(frequency)
        start_date_millis = date_to_millis(start_date)
        end_date_millis = date_to_millis(end_date)

        if freq_type not in VALID_FREQUENCY_TYPES:
            raise ValueError(
                f"Frequency type: {freq_type} not valid. Must be one of: {', '.join(VALID_FREQUENCY_TYPES)}"
            )

        if freq_type == "minute":
            period_type = "day"
            period = None
        else:
            period_type = "year"
            period = 1

        data = self._get_price_history(
            symbol,
            period=period,
            periodType=period_type,
            frequency=freq,
            frequencyType=freq_type,
            startDate=start_date_millis,
            endDate=end_date_millis,
            needExtendedHoursData=include_extended_hours,
        )

        return data["candles"]
