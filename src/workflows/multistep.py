from datetime import timedelta

from pydantic import BaseModel, Field
from restack_ai.workflow import NonRetryableError, import_functions, log, workflow

with import_functions():
    from src.functions.llm import FunctionInputParams, llm
    from src.functions.calendar_weather import calendar_weather


class WorkflowInputParams(BaseModel):
    name: str = Field(default="John Doe")


@workflow.defn()
class MultistepWorkflow:
    @workflow.run
    async def run(self, workflow_input: WorkflowInputParams) -> dict:
        log.info("MultistepWorkflow started", workflow_input=workflow_input)
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
                log.info("MultistepWorkflow completed", llm_message=llm_message)
                return {"message": llm_message, "calendar_weather": calendar_weather_data}

        # # Step 1 get weather data
        # try:
        #     weather_data = await workflow.step(
        #         function=weather, start_to_close_timeout=timedelta(seconds=120)
        #     )
        # except Exception as e:
        #     error_message = f"Error during weather: {e}"
        #     raise NonRetryableError(error_message) from e
        # else:
        #     # Step 2 Generate greeting with LLM  based on name and weather data
        #     try:
        #         llm_message = await workflow.step(
        #             function=llm,
        #             function_input=FunctionInputParams(
        #                 system_content=f"You are a personal assitant and have access to weather data {weather_data}. Always greet person with relevant info from weather data",
        #                 user_content=user_content,
        #                 model="gpt-4.1-mini",
        #             ),
        #             start_to_close_timeout=timedelta(seconds=120),
        #         )
        #     except Exception as e:
        #         error_message = f"Error during llm: {e}"
        #         raise NonRetryableError(error_message) from e
        #     else:
        #         log.info("MultistepWorkflow completed", llm_message=llm_message)
        #         return {"message": llm_message, "weather": weather_data}
