import requests

URL = "https://www.tvmovie.de/news/trash-tv-kalender-sendetermine-start-reality-tv-rtl-joyn-151130"

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
