from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from newsletter_designer.configuration import Configuration
from newsletter_designer.state import InputState, OutputState, State
from newsletter_designer.nodes import call_agent_model, reflect, route_after_agent, route_after_checker
from newsletter_designer.tools import design_newsletter

# Create the agent graph
workflow = StateGraph(
    State, input=InputState, output=OutputState, config_schema=Configuration
)

workflow.add_node(call_agent_model)
workflow.add_node(reflect)
workflow.add_node("tools", ToolNode([design_newsletter]))

workflow.add_conditional_edges("call_agent_model", route_after_agent)
workflow.add_edge("tools", "call_agent_model")
workflow.add_conditional_edges("reflect", route_after_checker)

graph = workflow.compile()