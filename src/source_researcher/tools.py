from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Any, Dict, Optional, cast

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from typing_extensions import Annotated
from langgraph.prebuilt import ToolNode

from langgraph.prebuilt import InjectedState
from source_researcher.state import State
from source_researcher.configuration import Configuration
from source_researcher.utils import init_model
from source_researcher import prompts
import json
from pydantic import BaseModel, Field

class FormattedResults(BaseModel):
    sources: list[Dict[str, Any]]  = Field(
        description="List of the results"
    )

@tool
async def search(
    query: str, 
    *,
    state: Annotated[State, InjectedState],
    config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[Dict[str, Any]]]:
    """Query a search engine.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    response = await wrapped.ainvoke({"query": query})
    search_result = cast(list[Dict[str, Any]], response)

    p = prompts.result_extraction_intructions.format(
        extraction_schema=json.dumps(configuration.extraction_schema, indent=2),
        search_results=json.dumps(search_result,indent=2),
    )
    raw_model = init_model(config).with_structured_output(FormattedResults)

    result = await raw_model.ainvoke(p)
    return result.sources


tools = [search]
tool_node = ToolNode(tools)