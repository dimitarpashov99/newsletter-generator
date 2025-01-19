from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from enrichment_agent.configuration import Configuration
from enrichment_agent.state import InputState, OutputState, State
from enrichment_agent.nodes import call_agent_model, route_after_agent, retrieve_sources, combine_data
from enrichment_agent.tools import scrape_website

workflow = StateGraph(
    State, input=InputState, output=OutputState, config_schema=Configuration
)

workflow.add_node("retrieve_sources", retrieve_sources)
workflow.add_node("enrich_data", call_agent_model)
workflow.add_node("scrape_source", ToolNode([scrape_website]))
workflow.add_node("combine_data", combine_data)

workflow.add_edge("__start__", "retrieve_sources")
workflow.add_edge("retrieve_sources", "enrich_data")
workflow.add_conditional_edges("enrich_data", route_after_agent)
workflow.add_edge("scrape_source", "enrich_data")
workflow.add_edge("combine_data","__end__")

graph = workflow.compile()