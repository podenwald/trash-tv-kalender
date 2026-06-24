import re
from datetime import date, timedelta
from bs4 import BeautifulSoup
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

WEEKDAYS = {
    "montag": 0,
    "montags": 0,
    "dienstag": 1,
    "dienstags": 1,
    "mittwoch": 2,
    "mittwochs": 2,
    "donnerstag": 3,
    "donnerstags": 3,
    "freitag": 4,
    "freitags": 4,
    "samstag": 5,
    "samstags": 5,
    "sonntag": 6,
    "sonntags": 6,
}

DATE_RE = re.compile(
    r"(?:(?P<prefix>ab dem|ab|am|bis|seit|finale am|reunion am|start am|startet am)\s+)?"
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
    "beauty & the nerd", "couplechallenge", "make love, fake love", "are you the one",
]

DEFAULT_RECURRING_WEEKS = 12


def parse(html: str, default_year: int | None = None) -> list[TvEvent]:
    soup = BeautifulSoup(html, "lxml")
    text_items = extract_relevant_items(soup)
    year = default_year or detect_year(soup) or date.today().year

    events: list[TvEvent] = []
    for item in text_items:
        if not looks_like_reality_item(item):
            continue

        title = extract_title(item)
        explicit_dates = extract_dates_with_prefix(item, year)
        weekday = extract_weekday(item)

        # 1) Konkrete Datumsangaben behalten wir immer.
        for event_date, prefix in explicit_dates:
            events.append(build_event(title, event_date, item, prefix or "Termin"))

        # 2) Laufende/wöchentliche Formate ergänzen.
        # Beispiel: "immer montags", "wöchentlich dienstags", "ab 15. Juli immer mittwochs".
        if weekday is not None and looks_recurring(item):
            start = determine_recurring_start(explicit_dates, weekday)
            end = determine_recurring_end(explicit_dates)
            recurring_dates = build_weekly_dates(start, weekday, end=end, weeks=DEFAULT_RECURRING_WEEKS)

            for event_date in recurring_dates:
                events.append(build_event(title, event_date, item, "Wöchentlicher Termin / laufende Sendung"))

    return deduplicate(events)


def build_event(title: str, event_date: date, description: str, note: str) -> TvEvent:
    return TvEvent(
        title=title,
        event_date=event_date,
        source=SOURCE,
        url=SOURCE_URL,
        description=f"{note}: {description}",
    )


def extract_relevant_items(soup: BeautifulSoup) -> list[str]:
    items = []

    for li in soup.find_all("li"):
        text = " ".join(li.get_text(" ", strip=True).split())
        if text:
            items.append(text)

    # Fallback: kurze Artikelabsätze verwenden, falls keine Listenstruktur vorhanden ist.
    if not items:
        for p in soup.find_all(["p", "div"]):
            text = " ".join(p.get_text(" ", strip=True).split())
            if 25 <= len(text) <= 300:
                items.append(text)

    return items


def looks_like_reality_item(text: str) -> bool:
    lower = text.lower()
    has_keyword = any(keyword in lower for keyword in TRASH_KEYWORDS)
    has_date = bool(DATE_RE.search(text))
    has_schedule_word = any(
        word in lower
        for word in ["immer", "wöchentlich", "woechentlich", "folge", "finale", "reunion", "startet", "ab dem", "seit"]
    )
    return has_keyword and (has_date or has_schedule_word)


def extract_title(text: str) -> str:
    # Titel in deutschen oder normalen Anführungszeichen bevorzugen.
    quote_match = re.search(r"[„\"]([^“\"]+)[”\"]", text)
    if quote_match:
        return clean_title(quote_match.group(1))

    # Häufiges Muster: "Temptation Island: immer dienstags ..."
    parts = re.split(r"\s*:\s*", text, maxsplit=1)
    if len(parts) > 1 and len(parts[0]) <= 90:
        return clean_title(parts[0])

    # Fallback: bis zum ersten Terminmarker.
    marker_match = re.split(
        r"\s+(immer|ab|am|bis|seit|Finale|Reunion|Start|startet)\s+",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )
    return clean_title(marker_match[0][:90])


def clean_title(title: str) -> str:
    title = title.replace(" :", ":").strip(" -–—:.,")
    return " ".join(title.split())


def extract_dates_with_prefix(text: str, default_year: int) -> list[tuple[date, str | None]]:
    dates = []
    for match in DATE_RE.finditer(text):
        day = int(match.group("day"))
        month_name = match.group("month").lower().replace("ä", "ae")
        month = MONTHS[month_name]
        year = int(match.group("year") or default_year)
        prefix = match.group("prefix")
        try:
            dates.append((date(year, month, day), prefix.lower() if prefix else None))
        except ValueError:
            continue

    return dates


def extract_weekday(text: str) -> int | None:
    lower = text.lower()
    for name, value in WEEKDAYS.items():
        if re.search(rf"\b{name}\b", lower):
            return value
    return None


def looks_recurring(text: str) -> bool:
    lower = text.lower()
    return any(word in lower for word in ["immer", "wöchentlich", "woechentlich", "jeden", "jede", "neue folgen"])


def determine_recurring_start(explicit_dates: list[tuple[date, str | None]], weekday: int) -> date:
    today = date.today()

    # Bei "ab", "seit", "start" nehmen wir das Datum als Serienstart.
    start_prefixes = ["ab", "ab dem", "seit", "start am", "startet am"]
    start_dates = [d for d, prefix in explicit_dates if prefix in start_prefixes]
    if start_dates:
        start = min(start_dates)
    else:
        # Wenn kein Startdatum vorhanden ist, ab heute planen.
        start = today

    # Bereits laufende Sendungen nicht rückwirkend vollspammen: ab heute fortsetzen.
    if start < today:
        start = today

    return next_weekday_on_or_after(start, weekday)


def determine_recurring_end(explicit_dates: list[tuple[date, str | None]]) -> date | None:
    end_prefixes = ["bis", "finale am", "reunion am"]
    end_dates = [d for d, prefix in explicit_dates if prefix in end_prefixes]
    if end_dates:
        return max(end_dates)
    return None


def build_weekly_dates(start: date, weekday: int, end: date | None, weeks: int) -> list[date]:
    result = []
    current = next_weekday_on_or_after(start, weekday)
    hard_end = start + timedelta(weeks=weeks)

    while current <= hard_end:
        if end is not None and current > end:
            break
        result.append(current)
        current += timedelta(days=7)

    return result


def next_weekday_on_or_after(start: date, weekday: int) -> date:
    days_ahead = (weekday - start.weekday()) % 7
    return start + timedelta(days=days_ahead)


def detect_year(soup: BeautifulSoup) -> int | None:
    candidates = re.findall(r"20\d{2}", soup.get_text(" ", strip=True))
    if not candidates:
        return None
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
