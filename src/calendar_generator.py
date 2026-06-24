from icalendar import Calendar

def generate(events):

    cal = Calendar()

    cal.add("prodid","Trash TV Kalender")

    cal.add("version","2.0")

    return cal
