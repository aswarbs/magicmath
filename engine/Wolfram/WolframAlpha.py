from pprint import pprint
from Keys import WOLFRAM_ALPHA_APPID
import requests
import urllib.parse


def get_answer(latex_str: str) -> str:
    # Your query
    appid = WOLFRAM_ALPHA_APPID
    query = urllib.parse.quote_plus("\\sum_{i=0}^{100} i")
    query_url = f"http://api.wolframalpha.com/v1/result?appid={appid}&input={query}&output=JSON"
    r = requests.get(query_url)
    pprint(r.json())
