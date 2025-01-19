import json
from typing import Dict, Any, Optional, cast, List, Literal
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from newsletter_designer.utils import init_model
from newsletter_designer.state import State

from langchain_core.runnables import RunnableConfig
from newsletter_designer.state import State
from typing import Dict, Any, cast
from langchain_core.messages import HumanMessage
from utils.utils import init_model
from pydantic import BaseModel, Field
from newsletter_designer.prompts import email_designer_prompt
import json

class NewsletterDesignOutput(BaseModel):
    html_template: str = Field(
        description="The HTML template for the newsletter."
    )

async def call_agent_model(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:

    if not state.draft_structure:
        raise ValueError("No sections available to generate the newsletter.")

    p = email_designer_prompt.format(
        sections=json.dumps(state.draft_structure, indent=2),
        audience_type=state.audience_type or "General Public",
        theme=state.theme or "Modern"
    )
    state.messages.append(HumanMessage(content=p))

    raw_model = init_model(config)
    model = raw_model.with_structured_output(NewsletterDesignOutput)
    response = cast(NewsletterDesignOutput, await model.ainvoke(state.messages))

    if response:
        state.final_email_template = response.html_template
    return state