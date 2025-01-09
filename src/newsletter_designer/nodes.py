import json
from typing import Dict, Any, Optional, cast, List, Literal
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from newsletter_designer.tools import design_newsletter
from newsletter_designer.utils import init_model
from newsletter_designer.state import State
from newsletter_designer.prompts import MAIN_PROMPT

async def call_agent_model(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:

    prompt = MAIN_PROMPT.format(
        draft_structure=json.dumps(state.draft_structure, indent=2),
        topic=state.topic,
        audience_type=state.audience_type or "General Public",
        theme=state.theme or "Default"
    )
    messages = [HumanMessage(content=prompt)] + state.messages

    raw_model = init_model(config)
    model = raw_model.bind_tools([design_newsletter], tool_choice="any")

    response = await model.ainvoke(messages)

    final_template = None
    if isinstance(response, AIMessage) and response.content:
        final_template = response.content

    return {
        "messages": [response],
        "final_email_template": final_template,
        "loop_step": state.loop_step + 1,
    }

class TemplateQualityCheck(BaseModel):
    reasons: List[str] = Field(
        description="Reasons why the result is good or bad."
    )
    is_satisfactory: bool = Field(
        description="Whether the template is satisfactory."
    )
    improvement_instructions: Optional[str] = Field(
        description="Instructions for improvement if necessary.",
        default=None
    )

async def reflect(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    checker_prompt = (
        f"Analyze the email template:\n{state.final_email_template}\n"
        "Provide feedback on whether this is satisfactory."
    )
    messages = [HumanMessage(content=checker_prompt)] + state.messages

    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(TemplateQualityCheck)
    response = cast(TemplateQualityCheck, await bound_model.ainvoke(messages))

    if response.is_satisfactory:
        return {
            "messages": [ToolMessage(content="Design approved.")],
        }
    else:
        return {
            "messages": [
                ToolMessage(
                    content=f"Improvements needed:\n{response.improvement_instructions}",
                    status="error"
                )
            ],
        }

def route_after_agent(state: State) -> Literal["reflect", "call_agent_model"]:
    if state.final_email_template:
        return "reflect"
    return "call_agent_model"

def route_after_checker(state: State, config: RunnableConfig) -> Literal["__end__", "call_agent_model"]:
    if state.loop_step >= config.max_loops:
        return "__end__"
    last_message = state.messages[-1]
    if isinstance(last_message, ToolMessage) and last_message.status == "error":
        return "call_agent_model"
    return "__end__"