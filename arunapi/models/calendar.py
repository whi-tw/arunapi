from datetime import date

from fastapi.responses import PlainTextResponse

from .. import __version__


class CalendarResponse(PlainTextResponse):
    media_type = "text/calendar"
    today = date.today()
    example = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:arunapi_v{__version__} - http://arunapi/
BEGIN:VEVENT
DTSTART;VALUE=DATE:{today.strftime("%Y%m%d")}
SUMMARY:Rubbish Collection
TRANSP:TRANSPARENT
UID:f0e4c2f76c58916ec258f246851bea091d14d4247a2fc3e18694461b1816e13b
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:{today.strftime("%Y%m%d")}
SUMMARY:Recycling Collection
TRANSP:TRANSPARENT
UID:139cd5119d398d06f6535f42d775986a683a90e16ce129a5fb7f48870613a1a5
END:VEVENT
END:VCALENDAR
    """
