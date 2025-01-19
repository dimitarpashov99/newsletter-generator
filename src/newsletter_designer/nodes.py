import json
from typing import Dict, Any, Optional, cast, List, Literal
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_core.runnables import RunnableConfig

from newsletter_designer.utils import init_model
from newsletter_designer.state import State
from newsletter_designer.prompts import MAIN_PROMPT
    
# async def call_agent_model(
#     state: State, *, config: Optional[RunnableConfig] = None
# ) -> Dict[str, Any]:

#     prompt = MAIN_PROMPT.format(
#         draft_structure=json.dumps(state.draft_structure, indent=2),
#         topic=state.topic,
#         audience_type=state.audience_type or "General Public",
#         theme=state.theme or "Default"
#     )
#     messages = [HumanMessage(content=prompt)] + state.messages

#     raw_model = init_model(config)
#     model = raw_model.bind_tools([design_newsletter], tool_choice="any")

#     response = await model.ainvoke(messages)

#     response = cast(AIMessage, await model.ainvoke(messages))
#     response_messages: List[BaseMessage] = [response]

#     return {
#         "messages": response_messages,
#     }


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

# @tool    
# async def design_newsletter(state: State, config) -> State:
#     """
#     Generate a newsletter design based on the given title and content.
    
#     Args:
#         title (str): The title of the newsletter.
#         content (str): The main content of the newsletter.

#     Returns:
#         State: A state representation of the designed newsletter.
#     """
#     p = email_designer_prompt.format(
#         structure=json.dumps(state.draft_structure, indent=2),
#         audience_type=state.audience_type or "General Public",
#         theme=state.theme or "Modern"
#     )
    
#     state.messages.append(HumanMessage(content=p))

#     raw_model = init_model(config)
#     bound_model = raw_model.with_structured_output(NewsletterDesignOutput)
#     response = cast(NewsletterDesignOutput, await bound_model.ainvoke(state.messages))
    
#     if response.html_template:
#         state.final_email_template = response.html_template
#         state.meta_info = response.meta_info
#     return state

async def call_agent_model(
    state: State, *, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:

    if not state.draft_structure:
        raise ValueError("No sections available to generate the newsletter.")

    # prompt = (
    #     "You are an expert HTML email designer. Using the following structured sections, "
    #     "create a professional, visually appealing email newsletter in HTML format. "
    #     "Each section includes a heading, description, and optional CTA. "
    #     "Ensure the template is responsive, readable, and visually engaging.\n\n"
    #     "Sections:\n"
    #     f"{json.dumps(state.draft_structure, indent=2)}\n"
    #     "Include:\n"
    #     "- A main title for the newsletter.\n"
    #     "- Appropriate section styling (e.g., headings, paragraphs).\n"
    #     "- Use a background color or gradient for each section to make them visually distinct. The color should be related to the topic.\n"
    #     "- Highlight CTAs as buttons with contrasting colors.\n"
    #     "- Ensure all colors are harmonious and fit a modern design theme."
    # )

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