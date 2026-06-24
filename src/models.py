from dataclasses import dataclass
from datetime import datetime

@dataclass
class TvEvent:
    title: str
    date: datetime
    url: str
