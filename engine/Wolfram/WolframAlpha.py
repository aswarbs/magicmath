from pprint import pprint
from Keys import WOLFRAM_ALPHA_APPID
import requests
import urllib.parse

appid = WOLFRAM_ALPHA_APPID

# Your query
query = urllib.parse.quote_plus("5 + 6 + 7^2 =")

# Construct the query URL with the dynamic query
query_url = f"http://api.wolframalpha.com/v2/query?appid={appid}&input={query}&output=JSON"

# Send the request to the Wolfram Alpha API
r = requests.get(query_url)

# Parse the JSON response
response = r.json()

# Extract the result from the response
result_pod = next(pod for pod in response['queryresult']['pods'] if pod['id'] == 'Result')

# Get the result (plaintext value)
result = result_pod['subpods'][0]['plaintext']

# Print the result
print(f"Result: {result}")