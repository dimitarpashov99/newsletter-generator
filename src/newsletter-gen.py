from langgraph.graph import StateGraph, START, END

from source_researcher.agent import graph as source_researcher_agent
from enrichment_agent.agent import graph as enrichment_agent_agent
from compositor_agent.agent import graph as compositor
from newsletter_designer.agent import graph as newsletter_designer_agent
import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class InputState:
    topic: str
    extraction_schema: Optional[Dict[str, Any]] = field(default=None)
    info: Optional[Dict[str, Any]] = field(default=None)
    audience_type: Optional[str] = field(default=None)
    theme: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class State(InputState):
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)
    loop_step: Annotated[int, operator.add] = field(default=0)
    final_email_template: Optional[str] = field(default=None)
    meta_info: Optional[Dict[str, str]] = field(default=None)


@dataclass(kw_only=True)
class OutputState:
    info: Dict[str, Any]
    final_email_template: Optional[str] = field(default=None)
    meta_info: Optional[Dict[str, str]] = field(default=None)


workflow = StateGraph(State)

workflow.add_node("source_researching", source_researcher_agent)
workflow.add_node("data_enrichment", enrichment_agent_agent)
workflow.add_node("content_composition", compositor)
workflow.add_node("newsletter_designing", newsletter_designer_agent)


workflow.add_edge(START, "source_researching")
workflow.add_edge("source_researching", "data_enrichment")
workflow.add_edge("data_enrichment", "content_composition")
workflow.add_edge("content_composition", "newsletter_designing")
workflow.add_edge("newsletter_designing", END)

graph = workflow.compile()