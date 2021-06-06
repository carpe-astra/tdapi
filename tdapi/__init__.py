__version__ = "0.1.0"

from tdapi.client import TDClient

TD_CLIENT = None


def get_client():
    global TD_CLIENT
    if TD_CLIENT is None:
        TD_CLIENT = TDClient()
    return TD_CLIENT
