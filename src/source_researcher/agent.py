from langgraph.graph import StateGraph, START, END

from source_researcher.nodes import research_agent, route_after_search, generate_query, finalize_research
from source_researcher.state import State, InputState, OutputState
from source_researcher.tools import tool_node
from source_researcher.configuration import Configuration

workflow = StateGraph(
    State, input=InputState, output=OutputState, config_schema=Configuration
)

workflow.add_edge(START, "query_writer")
workflow.add_node('query_writer', generate_query)
workflow.add_node("research_agent", research_agent)
workflow.add_node("tavily_search", tool_node)
workflow.add_node("finalize_research", finalize_research)

workflow.add_edge('query_writer', 'research_agent')
workflow.add_conditional_edges("research_agent", route_after_search)
workflow.add_edge("tavily_search", "research_agent")
workflow.add_edge('finalize_research', END)


graph = workflow.compile()
