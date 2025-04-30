import datetime
from restack_ai.function import function, log

@function.defn()
async def schedule_message(event_title: str, note: str, send_at: str) -> str:
    try:
        log.info("Scheduling message", event_title=event_title, note=note, send_at=send_at)
        # Parse send_at as a datetime object (assume UTC)
        send_at_dt = datetime.datetime.fromisoformat(send_at.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        seconds_to_wait = (send_at_dt - now).total_seconds()
        if seconds_to_wait > 0:
            log.info("Sleeping until send_at", seconds_to_wait=seconds_to_wait)
            await sleep(seconds_to_wait)
        # After waiting, send the message (for now, just log)
        log.info("Sending scheduled message", event_title=event_title, note=note, send_at=send_at)
        return f"Message scheduled for {send_at}"
    except Exception as e:
        error_message = f"Error scheduling message: {e}"
        raise NonRetryableError(error_message) from e

