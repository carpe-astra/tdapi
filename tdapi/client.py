"""Client for accessing the TD Ameritrade API"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

import requests
from loguru import logger

import tdapi.constants as constants
import tdapi.models as models
from tdapi.config import UserConfig, user_config
from tdapi.models.auth import EASObject
from tdapi.utils import (
    MODULE_DIR,
    date_to_millis,
    load_json,
    parse_frequency_str,
    remove_null_values,
    save_json,
)

# Globals
# ========================================================
VALID_FREQUENCY_TYPES = ("minute", "daily", "weekly", "monthly")
TD_CLIENT = None


# Helper Functions
# ========================================================
def get_client(auth_filepath: Path = None):
    global TD_CLIENT

    if auth_filepath is None:
        auth_filepath = MODULE_DIR / "auth.json"

    if TD_CLIENT is None:
        TD_CLIENT = TDClient(auth_filepath)

    return TD_CLIENT


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
    eas_object: EASObject = EASObject()
    auth_filepath: Path

    def __init__(self, auth_filepath: Path):
        super().__init__()

        self.auth_filepath = auth_filepath
        self.user_config: UserConfig = user_config
        eas_dict = load_json(self.auth_filepath)
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
        save_json(self.eas_object, self.auth_filepath, indent=2)

    def authenticate(self):
        logger.debug("Authenticating session...")

        if self.eas_object is None:
            try:
                eas_dict = load_json(self.auth_filepath)
                eas_object = EASObject(**eas_dict)

            except FileNotFoundError as e:
                logger.critical(f"{self.auth_filepath} not found.")
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

    def _get_instrument(self, cusip: str, apikey: str = None):
        route = self.base_url + f"/v1/instruments/{cusip}"

        params = {"apikey": apikey}
        params = remove_null_values(params)

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)
        data = resp.json()

        return data

    def _search_instruments(self, symbol: str, projection: str, apikey: str=None):
        route = self.base_url + "/v1/instruments"

        params = {"symbol": symbol, "projection": projection}

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)
        data = resp.json()

        return data

    """Market Hours"""

    def _get_market_hours(self, markets: List[str], date: str = None):
        route = self.base_url + "/v1/marketdata/hours"

        params = {"markets": ",".join(markets), "date": date}

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)

        return resp.json()

    """Movers"""

    """Option Chains"""

    def _get_option_chain(
        self,
        symbol: str,
        contract_type: str = constants.options.ContractType.ALL,
        strike_count: int = None,
        include_quotes: bool = constants.options.IncludeQuotes.FALSE,
        strategy: str = constants.options.Strategy.SINGLE,
        interval: str = None,
        strike: float = None,
        strike_range: str = constants.options.Range.ALL,
        from_date: str = None,
        to_date: str = None,
        volatility: float = None,
        underlying_price: float = None,
        interest_rate: float = None,
        days_to_expiration: int = None,
        exp_month: str = None,
        option_type: str = constants.options.Type.ALL,
    ) -> List[models.options.Option]:
        route = self.base_url + "/v1/marketdata/chains"

        params = {
            "symbol": symbol,
            "contractType": contract_type,
            "strikeCount": strike_count,
            "includeQuotes": include_quotes,
            "strategy": strategy,
            "interval": interval,
            "strike": strike,
            "range": strike_range,
            "fromDate": from_date,
            "toDate": to_date,
            "volatility": volatility,
            "underlyingPrice": underlying_price,
            "interestRate": interest_rate,
            "daysToExpiration": days_to_expiration,
            "expMonth": exp_month,
            "optionType": option_type,
        }

        params = remove_null_values(params)

        resp = self._get(route, params=params)
        self.validate_status(resp, 200)
        data = resp.json()

        options_list = []
        for option_type_map in ("putExpDateMap", "callExpDateMap"):
            for key, strike_option_dict in data[option_type_map].items():
                for strike, option_list in strike_option_dict.items():
                    options_list.append(models.options.Option(**option_list[0]))

        return options_list

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

    def get_market_hours(self, market: str, date: str = None):
        markets = self._get_market_hours([market], date)
        markets_hours = markets[market.lower()]
        first_market = list(markets_hours.keys())[0]
        hours = markets_hours[first_market]

        if hours["isOpen"] is False:
            return False, None, None

        else:
            start = hours["sessionHours"]["regularMarket"][0]["start"]
            end = hours["sessionHours"]["regularMarket"][0]["end"]
            return True, start, end
