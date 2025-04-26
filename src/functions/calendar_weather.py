from restack_ai.function import function, log
from .calendar import get_calendar_events
from .weather import get_weather_for_location

@function.defn()
async def calendar_weather() -> list:
    try:
        log.info("running calendar_weather")
        events = await get_calendar_events()
        calendar_weather = []
        for event in events:
            weather = await get_weather_for_location(event["latitude"], event["longitude"])
            calendar_weather.append({
                "event": event,
                "weather": weather,
            })
        log.info("calendar_weather completed", calendar_weather=calendar_weather)
        return calendar_weather
    except Exception as e:
        error_message = f"Error: {e}"
        raise NonRetryableError(error_message) from e
