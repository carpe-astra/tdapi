from tdapi import get_client

client = get_client()

# ps = client.get_price_history("GME", "5minute", "2021-06-04", "2021-06-05")
r = client.get_market_hours("EQUITY", "2021-06-07")
print(r)
