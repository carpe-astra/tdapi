from tdapi.client import get_client
from tdapi.constants.options import ContractType, Range

client = get_client(r"/home/taylor/projects/Python/ftd-checker/auth.json")

# # r = client.get_price_history("GME", "1minute", "2021-06-07", "2021-06-08")
# r = client._get_option_chain(
#     "UVXY",
#     contract_type=ContractType.CALL,
#     from_date="2021-12-17",
#     to_date="2021-12-17",
#     strike_range=Range.ALL,
# )
# # r = client.get_market_hours("EQUITY", "2021-06-07")
# print(r)

print(client._search_instruments("GOOG", "fundamental"))
