from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from .models import TvEvent


def generate(events: list[TvEvent]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//Trash TV Kalender//podenwald//DE")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Trash TV")
    cal.add("x-wr-timezone", "Europe/Berlin")

    for item in sorted(events, key=lambda e: (e.event_date, e.title)):
        event = Event()
        event.add("uid", f"{item.event_date.isoformat()}-{slugify(item.title)}@trash-tv-kalender")
        event.add("summary", f"📺 {item.title}")
        event.add("dtstart", item.event_date)
        event.add("dtend", item.event_date + timedelta(days=1))
        event.add("dtstamp", datetime.now(timezone.utc))
        event.add("description", f"{item.description}\n\nQuelle: {item.source}\n{item.url}".strip())
        event.add("url", item.url)
        cal.add_component(event)

    return cal


def slugify(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum():
            allowed.append(char)
        elif char in [" ", "-", "_", ":"]:
            allowed.append("-")
    return "".join(allowed).strip("-")[:80]
