from typing import Any, Dict, Literal, Optional, cast
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from source_researcher import prompts
from source_researcher.configuration import Configuration
from source_researcher.state import State
from source_researcher.tools import tools
from source_researcher.utils import init_model

from pydantic import BaseModel

class ResearchQuery(BaseModel):
    query: str

async def generate_query(state: State, *, config: Optional[RunnableConfig] = None):
    """ Generate a query for web search """
    query_writer_instructions_formatted = prompts.query_writer.format(topic=state.topic)
    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(ResearchQuery)
    messages = [SystemMessage(content=query_writer_instructions_formatted),
        HumanMessage(content=f"Generate a query for web search:")]
    response = cast(ResearchQuery, await bound_model.ainvoke(messages))
    
    return {"research_query": response.query}

async def research_agent(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    if state.messages and len(state.messages) > 0:
        last_message = state.messages[-1]
        if last_message.type == 'tool':
            return {
                'sources_gathered': [last_message.content],
                "loop_step": state.loop_step + 1
            }
    query = state.research_query
    raw_model = init_model(config)
    model = raw_model.bind_tools(tools, tool_choice="any")
    messages = [HumanMessage(content=f"Search for information on: {query}")]
    response = await model.ainvoke(messages)
    state.messages.append(response)

    return {
        "messages": state.messages,
        "loop_step": state.loop_step + 1
    }

async def finalize_research(
    state: State, 
    *, 
    config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    
    return state

def route_after_search(
    state: State, config: RunnableConfig
) -> Literal['tavily_search', "finalize_research"]:
    configuration = Configuration.from_runnable_config(config)
    if state.loop_step <= configuration.max_loops:
        return "tavily_search"
    else:
        return "finalize_research"