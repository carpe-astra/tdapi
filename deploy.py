from tdapi.client import get_client

client = get_client(r"C:\Users\Taylor\projects\Python\tdapi\auth.json")

# r = client.get_price_history("GME", "1minute", "2021-06-07", "2021-06-08")
r = client._get_option_chain(
    "GME", strike_count=1, from_date="2021-07-16", to_date="2021-07-16"
)
# r = client.get_market_hours("EQUITY", "2021-06-07")
print(r)
