from datetime import timedelta, datetime, timezone
import json
import asyncio

from pydantic import BaseModel, Field
from restack_ai.workflow import NonRetryableError, import_functions, log, workflow
with import_functions():
    from src.functions.llm import FunctionInputParams, llm
    from src.functions.calendar_weather import calendar_weather
    from src.functions.schedule_message import schedule_message

class WorkflowInputParams(BaseModel):
    name: str = Field(default="John Doe")


@workflow.defn()
class MultistepWorkflow:
    @workflow.run
    async def run(self, workflow_input: WorkflowInputParams) -> dict:
        log.info("MultistepWorkflow started", workflow_input=workflow_input)
        # await asyncio.sleep(10)
        # log.info("Slept for 10 seconds after scheduling message")
        user_content = f"Greet this person {workflow_input.name}"

        # Step 1 get calendar weather data
        try:
            calendar_weather_data = await workflow.step(
                function=calendar_weather, start_to_close_timeout=timedelta(seconds=120)
            )
        except Exception as e:
            error_message = f"Error during calendar_weather: {e}"
            raise NonRetryableError(error_message) from e
        else:
            # Step 2 Generate greeting with LLM  based on name and weather data
            try:
                llm_message = await workflow.step(
                    function=llm,
                    function_input=FunctionInputParams(
                        system_content=f"""You are my personal assitant and have access to my data of calendar events and weather information for each event {calendar_weather_data}. Prepare a daily briefing for me based on my calendar events and weather information for each event. In this briefind, tell me:
                        - when and where my events are
                        - if there is any bad weather that might affect my travel or my plans, please say so. if not, mention that the weather is ideal.
                        - if there are any conflicts between events, or if it is difficult to get from one event to another
                        - suggestions for when to leave, and how to get from one event to another for consecutive events""",
                        user_content=user_content,
                        model="gpt-4.1-mini",
                    ),
                    start_to_close_timeout=timedelta(seconds=120),
                )
            except Exception as e:
                error_message = f"Error during llm: {e}"
                raise NonRetryableError(error_message) from e
            else:
                # Step 3: Generate scheduler and send time-sensitive messages
                try:
                    leave_schedule = await workflow.step(
                        function=llm,
                        function_input=FunctionInputParams(
                            system_content=f"""Given my calendar events and weather info {calendar_weather_data}, create a JSON list of arrays where each object includes:
                            - 'event_title': event title
                            - 'leave_time': recommended departure time (in ISO 8601 UTC time)
                            - 'note': optional note about weather (like "bring umbrella" or "traffic is light")
                            """,
                            user_content="Plan my day with suggested leave times.",
                            model="gpt-4.1-mini",
                        ),
                        start_to_close_timeout=timedelta(seconds=120)
                    )
                    leave_schedule = json.loads(leave_schedule)

                    # Schedule notifications for each leave time
                    for item in leave_schedule:
                        leave_time = item["leave_time"]
                        event_title = item["event_title"]
                        note = item.get("note", "")

                        # Parse leave_time as a datetime object (assume UTC)
                        leave_time_dt = datetime.fromisoformat(leave_time.replace("Z", "+00:00"))
                        now = datetime.now(timezone.utc)
                        seconds_to_leave = (leave_time_dt - now).total_seconds()
                        
                        log.info("Computed seconds to leave", event_title=event_title, leave_time=leave_time, now=now.isoformat(), seconds_to_leave=seconds_to_leave)
                        
                        await asyncio.sleep(seconds_to_leave)
                        log.info(f"Slept for {seconds_to_leave} seconds after scheduling message")
                        await workflow.step(
                            function=notify, 
                            function_input=FunctionInputParams(
                                message=note
                            ),
                            start_to_close_timeout=timedelta(seconds=120),
                        )

                except Exception as e:
                    error_message = f"Error during llm: {e}"
                    raise NonRetryableError(error_message) from e
                else:
                    log.info("MultistepWorkflow completed", llm_message=llm_message, leave_schedule=leave_schedule)
                    return {"message": llm_message, "calendar_weather": calendar_weather_data, "leave_schedule": leave_schedule}