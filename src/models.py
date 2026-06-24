from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TvEvent:
    title: str
    event_date: date
    source: str
    url: str
    description: str = ""
