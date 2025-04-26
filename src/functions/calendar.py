import datetime
from restack_ai.function import function, log

@function.defn()
async def get_calendar_events() -> list:
    try:
        # For demo purposes, returning static events
        # Later you could connect to Google Calendar API
        log.info("running get_calendar_events")
        events = [
            {
                "title": "Coffee with Alice",
                "start_time": "2025-04-26T10:00:00Z",
                "location": "La Maison, Berlin",
                "latitude": 52.493326,
                "longitude": 13.431178,
            },
            {
                "title": "Hackathon",
                "start_time": "2025-04-26T15:00:00Z",
                "location": "CIC Berlin",
                "latitude": 52.494036,
                "longitude": 13.446270,
            },
        ]
        log.info("calendar events", events=events)
        return events
    except Exception as e:
        error_message = f"Error: {e}"
        raise NonRetryableError(error_message) from e
    
