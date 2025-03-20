import asyncio
from agents import Agent, GuardrailFunctionOutput, HandoffOutputItem, ItemHelpers, MessageOutputItem, RunContextWrapper, Runner, TResponseInputItem, ToolCallItem, ToolCallOutputItem, WebSearchTool, function_tool, input_guardrail
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from pydantic import BaseModel
import agents.exceptions

class UserInfoContext(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None

class TripPlanningGuardrailOutput(BaseModel):
    is_trip_planning: bool
    reasoning: str

class CityInfoGuardrailOutput(BaseModel):
    is_city_related: bool
    reasoning: str

# ==========================
# GUARDRAIL FOR FLIGHT FINDER
# ==========================
@input_guardrail
async def trip_planning_guardrail( 
    ctx: RunContextWrapper[UserInfoContext], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    if not isinstance(result.final_output, TripPlanningGuardrailOutput):
        return GuardrailFunctionOutput(
            output_info="Error: Guardrail response is not formatted correctly.",
            tripwire_triggered=True,
        )

    if not result.final_output.is_trip_planning:
        return GuardrailFunctionOutput(
            output_info="I'm sorry, I can only assist with flight planning requests.",
            tripwire_triggered=False,  # Prevents an exception
        )

    return GuardrailFunctionOutput(
        output_info=result.final_output.reasoning, 
        tripwire_triggered=False,
    )


# ==========================
# GUARDRAIL FOR CITY INFO AGENT
# ==========================
@input_guardrail
async def city_info_guardrail( 
    ctx: RunContextWrapper[UserInfoContext], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(city_guardrail_agent, input, context=ctx.context)

    if not isinstance(result.final_output, CityInfoGuardrailOutput):
        return GuardrailFunctionOutput(
            output_info="Error: Guardrail response is not formatted correctly.",
            tripwire_triggered=True,
        )

    if not result.final_output.is_city_related:
        return GuardrailFunctionOutput(
            output_info="I'm sorry, I can only assist with city-related information.",
            tripwire_triggered=False,  # Prevents an exception
        )

    return GuardrailFunctionOutput(
        output_info=result.final_output.reasoning, 
        tripwire_triggered=False,
    )


# ==========================
# GUARDRAIL FOR ROUTER AGENT
# ==========================
@input_guardrail
async def router_guardrail(
    ctx: RunContextWrapper[UserInfoContext], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Guardrail for the Router Agent to ensure only flight-related and city-related queries are processed.
    """
    flight_result = await Runner.run(guardrail_agent, input, context=ctx.context)
    city_result = await Runner.run(city_guardrail_agent, input, context=ctx.context)

    # Ensure responses are correctly formatted
    is_flight_related = isinstance(flight_result.final_output, TripPlanningGuardrailOutput) and flight_result.final_output.is_trip_planning
    is_city_related = isinstance(city_result.final_output, CityInfoGuardrailOutput) and city_result.final_output.is_city_related

    if not is_flight_related and not is_city_related:
        return GuardrailFunctionOutput(
            output_info="I'm sorry, I can only assist with flight planning and city-related questions.",
            tripwire_triggered=True,  # Prevents an error
        )

    return GuardrailFunctionOutput(
        output_info="Proceed",
        tripwire_triggered=False,
    )


# ==========================
# TOOL: GET CITY WEATHER
# ==========================
@function_tool
async def get_city_weather(contextWrapper: RunContextWrapper[UserInfoContext], city: str) -> str:
    """Get the weather in a city.
    Args:
        city: The city to get the weather for.
    Returns:
        The weather in the city.
    """

    contextWrapper.context.city = city
    return f"The weather in {city} is sunny, {contextWrapper.context.first_name}."

# ==========================
# GUARDRAIL AGENTS
# ==========================
guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="Check if the user is asking a request related to trip planning.",
    output_type=TripPlanningGuardrailOutput,
)

city_guardrail_agent = Agent(
    name="City Guardrail Check",
    instructions="Check if the user is asking about city-related information (e.g., weather, restaurants, landmarks).",
    output_type=CityInfoGuardrailOutput,
)

# ==========================
# MAIN AGENTS
# ==========================
city_info_agent = Agent[UserInfoContext](
    name="City Info Agent",
    input_guardrails=[city_info_guardrail],  # Guardrail for city-related queries only
    handoff_description="A helpful agent that can answer questions about a city.",
    instructions=f"""
    {RECOMMENDED_PROMPT_PREFIX}
    You are a city info agent. If you are speaking to a customer, you were likely transferred from the triage agent.
    Use the following routine to support the customer.
    # Routine
    1. Ask for the city name if not clear from the context.
    2. Use the web search tool to get information about restaurants in the city.
    3. Use the weather tool to get the live weather in the city, use your knowledge for climate questions.
    4. If the customer asks a question that is not related to the routine, transfer back to the triage agent.
    """,
    model="gpt-4o",
    tools=[WebSearchTool(), get_city_weather]
)

flight_finder_agent = Agent[UserInfoContext](
    name="Flight Finder Agent",
    input_guardrails=[trip_planning_guardrail],  # Guardrail for flight-related queries only
    handoff_description="A helpful agent that can find flights for a customer.",
    instructions=f"""
    {RECOMMENDED_PROMPT_PREFIX}
    You are a flight finder agent. If you are speaking to a customer, you were likely transferred from the triage agent.
    Use the following routine to support the customer.
    # Routine
    1. Ask for the city name if not clear.
    2. Use the web search tool to get information about flights to the city.
    3. If the customer asks a question that is not related to the routine, transfer back to the triage agent.
    """,
    model="gpt-4o-mini",
    tools=[WebSearchTool()],
)

# ==========================
# ROUTER AGENT 
# ==========================
router_agent = Agent[UserInfoContext](
    name="Router Agent",
    input_guardrails=[router_guardrail],  # Guardrail to block unrelated queries
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "You are a helpful routing agent. You can use your tools to delegate questions to other appropriate agents."
    ),
    handoffs=[
        city_info_agent,
        flight_finder_agent,
    ],
)

city_info_agent.handoffs.append(router_agent)
flight_finder_agent.handoffs.append(router_agent)

# ==========================
# MAIN EXECUTION LOOP
# ==========================
async def main():
    current_agent: Agent[UserInfoContext] = router_agent
    input_items: list[TResponseInputItem] = []
    context = UserInfoContext(first_name="James")

    while True:
        user_input = input("Enter message: ")
        input_items.append({"content": user_input, "role": "user"})
        
        try:
            result = await Runner.run(current_agent, input_items, context=context)

            # Block execution if the Router Guardrail rejects input
            if isinstance(result.final_output, str) and "I'm sorry" in result.final_output:
                print(f"\033[91mRouter Agent\033[0m: {result.final_output}")
                continue  # Prevents further processing

            for new_item in result.new_items:
                agent_name = new_item.agent.name
                if isinstance(new_item, MessageOutputItem):
                    print(f"\033[94m{agent_name}\033[0m: {ItemHelpers.text_message_output(new_item)}")
                elif isinstance(new_item, HandoffOutputItem):
                    print(f"Handed off from \033[92m{new_item.source_agent.name}\033[0m to \033[93m{new_item.target_agent.name}\033[0m")
                elif isinstance(new_item, ToolCallItem):
                    print(f"\033[95m{agent_name}\033[0m: Calling a tool")
                elif isinstance(new_item, ToolCallOutputItem):
                    print(f"\033[96m{agent_name}\033[0m: Tool call output: {new_item.output}")
                else:
                    print(f"\033[91m{agent_name}\033[0m: Skipping item: {new_item.__class__.__name__}")

            input_items = result.to_input_list()
            current_agent = result.last_agent
        except agents.exceptions.InputGuardrailTripwireTriggered as e:
            # Catch the guardrail exception and return a message instead
            print(f"\033[91mRouter Agent\033[0m: I'm sorry, I can only assist with flight planning and city-related questions.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user.")