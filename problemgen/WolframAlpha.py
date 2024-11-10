from pprint import pprint
from preprocessing.Key import WOLFRAM_ALPHA_APPID
import requests
import urllib.parse


def get_answer(query_str: str) -> str:
    # Wolfram Alpha API app ID and plain text query
    appid = WOLFRAM_ALPHA_APPID
    query = urllib.parse.quote_plus(query_str)
    # Use the 'query' endpoint for plain text input and structured response
    print(f"WOLFRAM >> {query}")
    query_url = f"http://api.wolframalpha.com/v2/result?" \
                f"appid={appid}" \
                f"&input={query}" \
                f"&includepodid=Result" \
                f"&output=json"

    r = requests.get(query_url)

    # Check if the request was successful and return the response
    if r.status_code == 200:
        print(r)
        result_data = r.json()

        # Check if 'queryresult' and 'pods' exist in the response
        if 'queryresult' not in result_data:
            pprint(r.json())
            return "Error: No 'queryresult' in response"

        queryresult = result_data['queryresult']

        if 'pods' not in queryresult:
            pprint(r.json())
            return "Error: No 'pods' in 'queryresult'"

        # Now try to process the pods
        for pod in queryresult['pods']:
            # Look for the Solution pod
            if pod['title'] == 'Solution':
                return pod['subpods'][0]['plaintext']

        # If no Solution pod, look for any pod with plaintext
        for pod in queryresult['pods']:
            for subpod in pod['subpods']:
                if 'plaintext' in subpod:
                    return subpod['plaintext']

        return "No result found."
    else:
        pprint(r)
        return f"Error: {r.status_code} - {r.text}"



if __name__ == '__main__':
    print(get_answer("Solve for x 3x + 5 = 20"))