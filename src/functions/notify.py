from restack_ai.function import function, log

@function.defn()
async def notify(message):
    try:
        # TODO send sms notification
        log.info("notify", message=message)
    except Exception as e:
        error_message = f"Error: {e}"
        raise NonRetryableError(error_message) from e