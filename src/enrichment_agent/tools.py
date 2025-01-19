import aiohttp
from langchain_core.tools import InjectedToolArg
from langgraph.prebuilt import InjectedState
from enrichment_agent.state import State
from typing_extensions import Annotated
from langchain_core.runnables import RunnableConfig

from enrichment_agent.utils import init_model
from enrichment_agent import prompts
from bs4 import BeautifulSoup

async def scrape_website(
    url: str,
    *,
    state: Annotated[State, InjectedState],
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    """Scrape and summarize content from a given URL.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()

    soup = BeautifulSoup(content, 'html.parser')
    text_content = soup.get_text()
    p = prompts.SCRAPER_PROMPT.format(
        url=url,
        content=text_content,
    )

    raw_model = init_model(config)
    result = await raw_model.ainvoke(p)

    state.enriched_sources.append({
        "source_url": url,
        "enriched_data": str(result.content)
    })
    return str(result.content)
