import json
from typing import Any, Dict, List, Literal, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from pydantic import BaseModel, Field

from source_researcher import prompts
from source_researcher.configuration import Configuration
from source_researcher.state import State
from source_researcher.tools import search
from source_researcher.utils import init_model

async def call_agent_model(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:

    configuration = Configuration.from_runnable_config(config)

    info_tool = {
        "name": "Info",
        "description": "Call this when you have gathered all the relevant info",
        "parameters": state.extraction_schema,
    }

    p = configuration.prompt.format(
        info=json.dumps(state.extraction_schema, indent=2), topic=state.topic
    )

    messages = [HumanMessage(content=p)] + state.messages

    raw_model = init_model(config)
    model = raw_model.bind_tools([search, info_tool], tool_choice="any")
    response = cast(AIMessage, await model.ainvoke(messages))
    info = None

    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "Info":
                info = tool_call["args"]
                break
    if info is not None:
        response.tool_calls = [
            next(tc for tc in response.tool_calls if tc["name"] == "Info")
        ]

    response_messages: List[BaseMessage] = [response]
    if not response.tool_calls:
        response_messages.append(
            HumanMessage(content="Please respond by calling one of the provided tools.")
        )
    return {
        "messages": response_messages,
        "info": info,
        "loop_step": 1,
    }


class InfoIsSatisfactory(BaseModel):
    reason: List[str] = Field(
        description="First, provide reasoning for why this is either good or bad as a final result. Must include at least 3 reasons."
    )
    is_satisfactory: bool = Field(
        description="After providing your reasoning, provide a value indicating whether the result is satisfactory. If not, you will continue researching."
    )
    improvement_instructions: Optional[str] = Field(
        description="If the result is not satisfactory, provide clear and specific instructions on what needs to be improved or added to make the information satisfactory."
        " This should include details on missing information, areas that need more depth, or specific aspects to focus on in further research.",
        default=None,
    )


async def reflect(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    p = prompts.MAIN_PROMPT.format(
        info=json.dumps(state.extraction_schema, indent=2), topic=state.topic
    )
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"{reflect.__name__} expects the last message in the state to be an AI message with tool calls."
            f" Got: {type(last_message)}"
        )
    messages = [HumanMessage(content=p)] + state.messages[:-1]
    presumed_info = state.info
    checker_prompt = """I am thinking of calling the info tool with the info below. \
    Is this good? Give your reasoning as well. \
    You can encourage the Assistant to look at specific URLs if that seems relevant, or do more searches.
    If you don't think it is good, you should be very specific about what could be improved.
    {presumed_info}"""

    p1 = checker_prompt.format(presumed_info=json.dumps(presumed_info or {}, indent=2))
    messages.append(HumanMessage(content=p1))
    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(InfoIsSatisfactory)
    response = cast(InfoIsSatisfactory, await bound_model.ainvoke(messages))
    if response.is_satisfactory and presumed_info:
        return {
            "info": presumed_info,
            "messages": [
                ToolMessage(
                    tool_call_id=last_message.tool_calls[0]["id"],
                    content="\n".join(response.reason),
                    name="Info",
                    additional_kwargs={"artifact": response.model_dump()},
                    status="success",
                )
            ],
        }
    else:
        return {
            "messages": [
                ToolMessage(
                    tool_call_id=last_message.tool_calls[0]["id"],
                    content=f"Unsatisfactory response:\n{response.improvement_instructions}",
                    name="Info",
                    additional_kwargs={"artifact": response.model_dump()},
                    status="error",
                )
            ]
        }


def route_after_agent(
    state: State,
) -> Literal["action", "agent", "tools", "__end__"]:
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        return "agent"
    
    if last_message.tool_calls and last_message.tool_calls[0]["name"] == "Info":
        return "action"
    else:
        return "tools"


def route_after_checker(
    state: State, config: RunnableConfig
) -> Literal["__end__", "agent"]:
    configurable = Configuration.from_runnable_config(config)
    last_message = state.messages[-1]

    if state.loop_step < configurable.max_loops:
        if not state.info:
            return "agent"
        if not isinstance(last_message, ToolMessage):
            raise ValueError(
                f"{route_after_checker.__name__} expected a tool messages. Received: {type(last_message)}."
            )
        if last_message.status == "error":
            return "agent"
        return "__end__"
    else:
        return "__end__"
