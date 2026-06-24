import re
from datetime import date
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from .models import TvEvent

SOURCE = "TVMovie Trash-TV-Kalender"
SOURCE_URL = "https://www.tvmovie.de/news/trash-tv-kalender-sendetermine-start-reality-tv-rtl-joyn-151130"

MONTHS = {
    "januar": 1,
    "februar": 2,
    "märz": 3,
    "maerz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
}

DATE_RE = re.compile(
    r"(?:(?:ab|am|bis|seit|Finale am|Reunion am|ab dem)\s+)?"
    r"(?P<day>\d{1,2})\.\s*"
    r"(?P<month>Januar|Februar|März|Maerz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)"
    r"(?:\s+(?P<year>20\d{2}))?",
    re.IGNORECASE,
)

TRASH_KEYWORDS = [
    "rtl+", "joyn", "reality", "trash", "temptation", "bachelor", "bachelors",
    "prominent getrennt", "ex on the beach", "villa der versuchung", "bad boyfriends",
    "sommerhaus", "kampf der realitystars", "love island", "promi big brother",
    "match my ex", "eden", "bauer sucht frau", "goodbye deutschland",
]


def parse(html: str, default_year: int | None = None) -> list[TvEvent]:
    soup = BeautifulSoup(html, "lxml")
    text_items = extract_relevant_items(soup)
    year = default_year or detect_year(soup) or date.today().year

    events: list[TvEvent] = []
    for item in text_items:
        if not looks_like_reality_item(item):
            continue

        title = extract_title(item)
        dates = extract_dates(item, year)

        for event_date in dates:
            events.append(
                TvEvent(
                    title=title,
                    event_date=event_date,
                    source=SOURCE,
                    url=SOURCE_URL,
                    description=item,
                )
            )

    return deduplicate(events)


def extract_relevant_items(soup: BeautifulSoup) -> list[str]:
    """Extract list items around the monthly Trash-TV calendar section.

    TVMovie publishes the dates as article text/bullets. The markup can change,
    so this function intentionally works text-first and tolerates different HTML.
    """
    items = []

    for li in soup.find_all("li"):
        text = " ".join(li.get_text(" ", strip=True).split())
        if text:
            items.append(text)

    # Fallback: use short paragraphs if no useful list items are available.
    if not items:
        for p in soup.find_all(["p", "div"]):
            text = " ".join(p.get_text(" ", strip=True).split())
            if 25 <= len(text) <= 250:
                items.append(text)

    return items


def looks_like_reality_item(text: str) -> bool:
    lower = text.lower()
    has_keyword = any(keyword in lower for keyword in TRASH_KEYWORDS)
    has_date = bool(DATE_RE.search(text))
    has_schedule_word = any(word in lower for word in ["immer", "wöchentlich", "folge", "finale", "reunion", "startet", "ab dem"])
    return has_keyword and (has_date or has_schedule_word)


def extract_title(text: str) -> str:
    # Prefer quoted titles.
    quote_match = re.search(r"[„\"]([^“\"]+)[”\"]", text)
    if quote_match:
        return clean_title(quote_match.group(1))

    # Many items look like: "Temptation Island : immer dienstags ..."
    parts = re.split(r"\s*:\s*", text, maxsplit=1)
    if len(parts) > 1 and len(parts[0]) <= 80:
        return clean_title(parts[0])

    # Fallback: until first schedule marker.
    marker_match = re.split(r"\s+(immer|ab|am|bis|Finale|Reunion)\s+", text, maxsplit=1, flags=re.IGNORECASE)
    return clean_title(marker_match[0][:80])


def clean_title(title: str) -> str:
    title = title.replace(" :", ":").strip(" -–—:.,")
    return " ".join(title.split())


def extract_dates(text: str, default_year: int) -> list[date]:
    dates = []
    for match in DATE_RE.finditer(text):
        day = int(match.group("day"))
        month_name = match.group("month").lower().replace("ä", "ae")
        month = MONTHS[month_name]
        year = int(match.group("year") or default_year)
        try:
            dates.append(date(year, month, day))
        except ValueError:
            continue

    return dates


def detect_year(soup: BeautifulSoup) -> int | None:
    candidates = re.findall(r"20\d{2}", soup.get_text(" ", strip=True))
    if not candidates:
        return None
    # Use the most frequent year in the article.
    return max(set(candidates), key=candidates.count)


def deduplicate(events: list[TvEvent]) -> list[TvEvent]:
    seen = set()
    result = []
    for event in events:
        key = (event.title.lower(), event.event_date.isoformat())
        if key not in seen:
            seen.add(key)
            result.append(event)
    return result
