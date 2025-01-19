from newsletter_designer.configuration import Configuration
from langchain_core.tools import InjectedToolArg
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from langchain_core.runnables import RunnableConfig
from newsletter_designer.prompts import email_designer_prompt
from newsletter_designer.state import State
from typing import Dict, Any, cast
from langchain_core.messages import HumanMessage
from utils.utils import init_model
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import json

class NewsletterDesignOutput(BaseModel):
    html_template: str = Field(
        description="The HTML template for the newsletter."
    )
    meta_info: Dict[str, str] = Field(
        description="Meta information about the generated template, such as estimated reading time, sections count."
    )

@tool
async def design_newsletter(
    *, 
    state: Annotated[State, InjectedState],
    config: Annotated[RunnableConfig, InjectedToolArg],) -> State:
    """
    Generate an HTML template for the newsletter with visually appealing colors for each section.

    Args:
        state: The state containing sections and CTAs.
        config: Configuration for the model or tools.

    Returns:
        Updated state with the generated HTML template and meta information.
    """
    if not state.draft_structure:
        raise ValueError("No sections available to generate the newsletter.")

    prompt = (
        "You are an expert HTML email designer. Using the following structured sections, "
        "create a professional, visually appealing email newsletter in HTML format. "
        "Each section includes a heading, description, and optional CTA. "
        "Ensure the template is responsive, readable, and visually engaging.\n\n"
        "Sections:\n"
        f"{json.dumps(state.draft_structure, indent=2)}\n"
        "Include:\n"
        "- A main title for the newsletter.\n"
        "- Appropriate section styling (e.g., headings, paragraphs).\n"
        "- Use a background color or gradient for each section to make them visually distinct. The color should be related to the topic.\n"
        "- Highlight CTAs as buttons with contrasting colors.\n"
        "- Ensure all colors are harmonious and fit a modern design theme."
    )

    state.messages.append(HumanMessage(content=prompt))

    raw_model = init_model(config)
    model = raw_model.with_structured_output(NewsletterDesignOutput)
    response = cast(NewsletterDesignOutput, await model.ainvoke(state.messages))

    if response:
        state.final_email_template = response.html_template
        state.meta_info = response.meta_info
    return state