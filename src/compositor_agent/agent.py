from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from compositor_agent.state import State , InputState, OutputState
from utils.utils import init_model
import json
from typing import List , cast
from pydantic import BaseModel, Field

class ClassifiedSource(BaseModel):
    source: str = Field(
        description="The URL or title of the source."
    )
    reliability: str = Field(
        description="The reliability of the source (e.g., High, Medium, Low)."
    )
    relevance: str = Field(
        description="The relevance of the source (e.g., High, Medium, Low)."
    )
    audience_focus: str = Field(
        description="The intended audience for the source (e.g., General Public, Experts)."
    )

class ClassifySourcesOutput(BaseModel):
    classified_sources: List[ClassifiedSource] = Field(
        description="A list of classified sources with their reliability, relevance, and audience focus."
    )

class KeyTopic(BaseModel):
    topic: str = Field(
        description="A key topic or trend identified in the sources."
    )

class ExtractKeyTopicsOutput(BaseModel):
    key_topics: List[KeyTopic] = Field(
        description="A list of key topics or trends extracted from the sources."
    )

class Section(BaseModel):
    heading: str = Field(
        description="The heading of the section."
    )
    description: str = Field(
        description="A brief description of the section's content."
    )

class ProposeStructureOutput(BaseModel):
    sections: List[Section] = Field(
        description="A list of sections and headings for the newsletter."
    )

async def classify_sources(state: State, config) -> State:
    p = (
        "Analyze the following sources:\n"
        "{sources}\n"
        "For each source, classify the reliability, relevance, and audience focus."
    ).format(sources="\n".join(state.sources))
    
    state.messages.append(HumanMessage(content=p))

    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(ClassifySourcesOutput)
    response = cast(ClassifySourcesOutput, await bound_model.ainvoke(state.messages))
    if response.classified_sources :
        state.classified_sources = [source.dict() for source in response.classified_sources]
    return state

async def extract_key_topics(state: State, config) -> State:
    p = (
        "Based on the classified sources:\n"
        "{classified_sources}\n"
        "Identify key topics and trends that should be highlighted in the newsletter."
    ).format(classified_sources=json.dumps(state.classified_sources, indent=2))
    
    state.messages.append(HumanMessage(content=p))

    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(ExtractKeyTopicsOutput)
    response = cast(ExtractKeyTopicsOutput, await bound_model.ainvoke(state.messages))
    if response.key_topics:
        state.key_topics = [topic.topic for topic in response.key_topics]
    return state

async def propose_structure(state: State, config) -> State:
    p = (
        "Given the key topics:\n"
        "{key_topics}\n"
        "Suggest a draft structure for the newsletter, including sections and headings."
    ).format(key_topics="\n".join(state.key_topics))
    
    state.messages.append(HumanMessage(content=p))

    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(ProposeStructureOutput)
    response = cast(ProposeStructureOutput, await bound_model.ainvoke(state.messages))
    if response.sections:
        state.draft_structure = [section.dict() for section in response.sections]
    return state

workflow = StateGraph(State, input=InputState, output=OutputState)

workflow.add_node("classify_sources", classify_sources)
workflow.add_node("extract_key_topics", extract_key_topics)
workflow.add_node("propose_structure", propose_structure)

workflow.add_edge(START, "classify_sources")
workflow.add_edge("classify_sources", "extract_key_topics")
workflow.add_edge("extract_key_topics", "propose_structure")
workflow.add_edge("propose_structure", END)

graph = workflow.compile()

