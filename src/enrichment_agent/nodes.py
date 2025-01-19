import json
from typing import Any, Dict, List, Literal, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from enrichment_agent import prompts
from enrichment_agent.configuration import Configuration
from enrichment_agent.state import State
from enrichment_agent.tools import scrape_website
from enrichment_agent.utils import init_model
from pydantic import BaseModel, Field

async def call_agent_model(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    if len(state.enriched_sources):
        messages =  state.messages + [HumanMessage(content="Data enriched!")]
        return {
            "messages":  state.messages 
        }

    configuration = Configuration.from_runnable_config(config)
    p = configuration.prompt.format(
        topic=state.topic,
        gathered_sources=json.dumps(state.sources_gathered, indent=2)
    )
    messages = [HumanMessage(content=p)] + state.messages
    raw_model = init_model(config)
    model = raw_model.bind_tools([scrape_website], tool_choice="any")
    response = cast(AIMessage, await model.ainvoke(messages))
    response_messages: List[BaseMessage] = [response]
    return {
        "messages": response_messages,
    }

def retrieve_sources(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    return state

async def combine_data(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    sources_gathered = state.sources_gathered
    enriched_sources_raw = state.enriched_sources
    enriched_sources_combined = []

    for source in sources_gathered:
        enriched_match = next(
            (item for item in enriched_sources_raw if item.get("source_url") == source.get("url")),
            None
        )
        combined_entry = {
            "source_data": source,
            "enriched_data": enriched_match.get("enriched_data", []) if enriched_match else []
        }
        enriched_sources_combined.append(combined_entry)

    return {"enriched_sources": enriched_sources_combined}

def route_after_agent(
    state: State,
) -> Literal[ "scrape_source", "combine_data"]:
    last_message = state.messages[-1]

    if not isinstance(last_message, AIMessage):
        return "combine_data"
    else:
        return "scrape_source"