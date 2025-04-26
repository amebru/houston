import aiohttp
from restack_ai.function import NonRetryableError, function, log

HTTP_OK = 200


def raise_exception(message: str) -> None:
    log.error(message)
    raise Exception(message)


@function.defn()
async def weather() -> str:
    url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    try:
        log.info("running weather")
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            log.info("response", response=response)
            if response.status == HTTP_OK:
                data = await response.json()
                log.info("weather data", data=data)
                return str(data)
            error_message = f"Error: {response.status}"
            raise_exception(error_message)
    except Exception as e:
        error_message = f"Error: {e}"
        raise NonRetryableError(error_message) from e


@function.defn()
async def get_weather_for_location(latitude: float, longitude: float) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    try:
        timeout = aiohttp.ClientTimeout(total=10, connect=5, sock_read=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                log.info("weather response", response=response)
                if response.status == HTTP_OK:
                    data = await response.json()
                    log.info("weather data", data=data)
                    return data
                raise_exception(f"Error fetching weather: {response.status}")
    except aiohttp.ClientError as e:
        error_message = f"Weather API connection error: {e}"
        raise NonRetryableError(error_message) from e
    except Exception as e:
        error_message = f"Weather fetch error: {e}"
        raise NonRetryableError(error_message) from e
