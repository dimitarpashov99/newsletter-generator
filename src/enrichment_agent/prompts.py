MAIN_PROMPT = """You are doing web research on behalf of a user. You are trying to figure out this information:

<info>
{info}
</info>

You have access to the following tools:

- `Search`: call a search tool and gather results using the web
- `ScrapeWebsite`: scrape a website and get relevant notes about the given request. This will update the notes above.
- `Info`: call this when you are done and have gathered all the relevant info

Here is the information you have about the topic you are researching:

Topic: {topic}"""

INFO_PROMPT = """You are doing web research on behalf of a user. You are trying to find out this information:

<info>
{info}
</info>

You just scraped the following website: {url}

Based on the website content below, write down some notes about the website.

<Website content>
{content}
</Website content>"""

CHECKER_PROMPT = """I am thinking of calling the info tool with the info below. \
    Is this good? Give your reasoning as well. \
    You can encourage the Assistant to look at specific URLs if that seems relevant, or do more searches.
    If you don't think it is good, you should be very specific about what could be improved.

{presumed_info}"""
