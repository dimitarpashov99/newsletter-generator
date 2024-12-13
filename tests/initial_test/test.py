from langgraph.graph import StateGraph
from enrichment_agent.agent import graph  # Import your compiled graph
from enrichment_agent.state import InputState, OutputState

# Mock input state for testing
input_data = {
    "topic": "Test topic",
    "extraction_schema": {"example_field": "value"},
    "messages": [],
}

# Initialize input state
input_state = InputState(**input_data)

# Run the graph locally
result = graph.run(input_state)

# Print output state
print("Output State:")
print(result)