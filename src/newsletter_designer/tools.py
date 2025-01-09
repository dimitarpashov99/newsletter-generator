from newsletter_designer.configuration import Configuration

from newsletter_designer.prompts import MAIN_PROMPT
from newsletter_designer.state import State
from typing import Dict, Any, cast
from langchain_core.messages import HumanMessage
from utils.utils import init_model
from pydantic import BaseModel, Field
import json

class NewsletterDesignOutput(BaseModel):
    html_template: str = Field(
        description="The HTML template for the newsletter."
    )
    meta_info: Dict[str, str] = Field(
        description="Meta information about the generated template, such as estimated reading time, sections count."
    )
    

async def design_newsletter(state: State, config) -> State:
    p = (
        "Using the following newsletter structure and audience information:\n"
        "Structure:\n{structure}\n"
        "Audience Type: {audience_type}\n"
        "Theme: {theme}\n\n"
        "Design a professional, visually appealing email newsletter template in HTML format. "
        "Include sections, call-to-action buttons, and a layout optimized for readability. "
        "Provide meta-information about the template, such as the estimated reading time and section count."
    ).format(
        structure=json.dumps(state.draft_structure, indent=2),
        audience_type=state.audience_type or "General Public",
        theme=state.theme or "Modern"
    )
    
    state.messages.append(HumanMessage(content=p))

    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(NewsletterDesignOutput)
    response = cast(NewsletterDesignOutput, await bound_model.ainvoke(state.messages))
    
    if response.html_template:
        state.final_email_template = response.html_template
        state.meta_info = response.meta_info
    return state
