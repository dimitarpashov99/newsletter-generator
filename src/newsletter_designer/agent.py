from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode

from newsletter_designer.configuration import Configuration
from newsletter_designer.state import InputState, OutputState, State
from newsletter_designer.nodes import call_agent_model

workflow = StateGraph(
    State, input=InputState, output=OutputState, config_schema=Configuration
)

workflow.add_node("designer_model", call_agent_model)

workflow.add_edge(START, "designer_model")
workflow.add_edge("designer_model", '__end__')

graph = workflow.compile()