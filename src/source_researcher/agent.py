from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from source_researcher.nodes import call_agent_model, reflect, route_after_agent, route_after_checker, finalize_results
from source_researcher.state import State, InputState, OutputState
from source_researcher.tools import tools
from source_researcher.configuration import Configuration

workflow = StateGraph(
    State, input=InputState, output=OutputState, config_schema=Configuration
)

workflow.add_edge(START, "agent")

workflow.add_node("agent", call_agent_model)
workflow.add_node("action", reflect)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("finalize", finalize_results)

workflow.add_conditional_edges("agent", route_after_agent)
workflow.add_edge("tools", "agent")
workflow.add_conditional_edges("action", route_after_checker)



graph = workflow.compile()
