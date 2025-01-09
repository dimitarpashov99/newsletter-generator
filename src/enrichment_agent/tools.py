import json
from typing import Any, Optional, cast

import aiohttp
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated

from enrichment_agent.configuration import Configuration
from enrichment_agent.state import State
from enrichment_agent.utils import init_model
from enrichment_agent import prompts

async def search(
    query: str, *,
    config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Query a search engine.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)


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

    p = prompts.INFO_PROMPT.format(
        info=json.dumps(state.extraction_schema, indent=2),
        url=url,
        content=content[:40_000],
    )
    raw_model = init_model(config)
    result = await raw_model.ainvoke(p)
    return str(result.content)


# async def research(
#     *,
#     state: Annotated[State, InjectedState],
#     config: Annotated[RunnableConfig, InjectedToolArg]
#     ) -> tuple:
#         """
#         This function extracts content from a specified link using the Tavily Python SDK, the title and
#         images from the link are extracted using the functions from `gpt_researcher/scraper/utils.py`.

#         Returns:
#           The `scrape` method returns a tuple containing the extracted content, a list of image URLs, and
#         the title of the webpage specified by the `self.link` attribute. It uses the Tavily Python SDK to
#         extract and clean content from the webpage. If any exception occurs during the process, an error
#         message is printed and an empty result is returned.
#         """

#         try:
#             response = tavily_client.extract(urls=[])
#             if response['failed_results']:
#                 return "", [], ""

#             # Parse the HTML content of the response to create a BeautifulSoup object for the utility functions
#             response_bs = self.session.get(self.link, timeout=4)
#             soup = BeautifulSoup(
#                 response_bs.content, "lxml", from_encoding=response_bs.encoding
#             )

#             # Since only a single link is provided to tavily_client, the results will contain only one entry.
#             content = response['results'][0]['raw_content']

#             # Get relevant images using the utility function
#             image_urls = get_relevant_images(soup, self.link)

#             # Extract the title using the utility function
#             title = extract_title(soup)

#             return content, image_urls, title

#         except Exception as e:
#             print("Error! : " + str(e))
#             return "", [], ""
#     return ''
