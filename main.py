import json
from pathlib import Path

from src.scraper import download
from src.parser import parse
from src.calendar_generator import generate

DATA_DIR = Path("data")
EVENTS_JSON = DATA_DIR / "events.json"
ICS_FILE = Path("calendar.ics")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    html = download()
    events = parse(html)
    calendar = generate(events)

    ICS_FILE.write_bytes(calendar.to_ical())

    EVENTS_JSON.write_text(
        json.dumps(
            [
                {
                    "title": event.title,
                    "date": event.event_date.isoformat(),
                    "source": event.source,
                    "url": event.url,
                    "description": event.description,
                }
                for event in sorted(events, key=lambda e: (e.event_date, e.title))
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Created {ICS_FILE} with {len(events)} events.")


if __name__ == "__main__":
    main()
