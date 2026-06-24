from src.scraper import download
from src.parser import parse
from src.calendar_generator import generate

html = download()

events = parse(html)

calendar = generate(events)

with open("calendar.ics","wb") as f:
    f.write(calendar.to_ical())
