from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Any, Dict, Optional, cast, List

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from typing_extensions import Annotated

from source_researcher.configuration import Configuration

@tool
async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[Dict[str, Any]]]:
    """Query a search engine.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[Dict[str, Any]], result)

tools = [search]