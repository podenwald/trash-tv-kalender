import requests

URL = "https://wannkommtwas.de"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def download():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text
