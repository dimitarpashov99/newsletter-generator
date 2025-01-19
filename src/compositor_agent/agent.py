from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from compositor_agent.state import State , InputState, OutputState
from utils.utils import init_model
import json
from typing import List , cast , Dict , Any
from pydantic import BaseModel, Field

# class ClassifiedSource(BaseModel):
#     source: str = Field(
#         description="The URL or title of the source."
#     )
#     reliability: str = Field(
#         description="The reliability of the source (e.g., High, Medium, Low)."
#     )
#     relevance: str = Field(
#         description="The relevance of the source (e.g., High, Medium, Low)."
#     )
#     audience_focus: str = Field(
#         description="The intended audience for the source (e.g., General Public, Experts)."
#     )

# class ClassifySourcesOutput(BaseModel):
#     classified_sources: List[ClassifiedSource] = Field(
#         description="A list of classified sources with their reliability, relevance, and audience focus."
#     )

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

class PrioritizedSections(BaseModel): 
    ordered_sections: List[Dict[str, Any]] = Field(
        description="Ordered list for sections by priority"
    )

class ProposeStructureOutput(BaseModel):
    sections: List[Section] = Field(
        description="A list of sections and headings for the newsletter."
    )


# async def classify_sources(state: State, config) -> State:
#     p = (
#         "Analyze the following sources:\n"
#         "{sources}\n"
#         "For each source, classify the reliability, relevance, and audience focus."
#     ).format(sources="\n".join(state.sources))
    
#     state.messages.append(HumanMessage(content=p))

#     raw_model = init_model(config)
#     bound_model = raw_model.with_structured_output(ClassifySourcesOutput)
#     response = cast(ClassifySourcesOutput, await bound_model.ainvoke(state.messages))
#     if response.classified_sources :
#         state.classified_sources = [source.dict() for source in response.classified_sources]
#     return state

# async def extract_key_topics(state: State, config) -> State:
#     p = (
#         "Based on the classified sources:\n"
#         "{classified_sources}\n"
#         "Identify key topics and trends that should be highlighted in the newsletter."
#     ).format(classified_sources=json.dumps(state.classified_sources, indent=2))
    
#     state.messages.append(HumanMessage(content=p))

#     raw_model = init_model(config)
#     bound_model = raw_model.with_structured_output(ExtractKeyTopicsOutput)
#     response = cast(ExtractKeyTopicsOutput, await bound_model.ainvoke(state.messages))
#     if response.key_topics:
#         state.key_topics = [topic.topic for topic in response.key_topics]
#     return state

# async def propose_structure(state: State, config) -> State:
#     p = (
#         "Given the key topics:\n"
#         "{key_topics}\n"
#         "Suggest a draft structure for the newsletter, including sections and headings."
#     ).format(key_topics="\n".join(state.key_topics))
    
#     state.messages.append(HumanMessage(content=p))

#     raw_model = init_model(config)
#     bound_model = raw_model.with_structured_output(ProposeStructureOutput)
#     response = cast(ProposeStructureOutput, await bound_model.ainvoke(state.messages))
#     if response.sections:
#         state.draft_structure = [section.dict() for section in response.sections]
#     return state

# workflow = StateGraph(State, input=InputState, output=OutputState)

# workflow.add_node("classify_sources", classify_sources)
# workflow.add_node("extract_key_topics", extract_key_topics)
# workflow.add_node("propose_structure", propose_structure)

# workflow.add_edge("__start__", "classify_sources")
# workflow.add_edge("classify_sources", "extract_key_topics")
# workflow.add_edge("extract_key_topics", "propose_structure")
# workflow.add_edge("propose_structure", "__end__")

# graph = workflow.compile()

async def analyze_enriched_data(state: State, config) -> State:
    enriched_data = state.enriched_sources
    p = (
        "Analyze the following enriched data:\n"
        f"{json.dumps(enriched_data, indent=2)}\n\n"
        "Identify key topics and highlights that should be emphasized in the newsletter."
    )
    
    state.messages.append(HumanMessage(content=p))
    
    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(ExtractKeyTopicsOutput)
    response = cast(ExtractKeyTopicsOutput, await bound_model.ainvoke(state.messages))
    
    if response.key_topics:
        state.key_topics = [topic.topic for topic in response.key_topics]
    
    return state

async def create_sections(state: State, config) -> State:
    key_topics = state.key_topics
    p = (
        "Based on the identified key topics:\n"
        f"{key_topics}\n\n"
        "Create the main sections for a newsletter, including:\n"
        "- Introduction\n"
        "- Main News Highlights\n"
        "- Special Offers\n"
        "- Conclusion\n"
        "For each section, provide a title and a short description."
    )
    
    state.messages.append(HumanMessage(content=p))
    
    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(ProposeStructureOutput)
    response = cast(ProposeStructureOutput, await bound_model.ainvoke(state.messages))
    
    if response.sections:
        state.sections = [section.dict() for section in response.sections]
    
    return state

class CallToAction(BaseModel):
    title: str = Field(description="Call to action message to be introduced in the newsletter")
    action: str = Field(description="Contains HTTP link to the page of the source")

class SectionOutput(BaseModel):
    heading: str = Field(description="The heading of the section.")
    description: str = Field(description="The description of the section, including relevant details from the sources.")
    cta: CallToAction = Field(description="The call-to-action object, if applicable.")

class GenerateSectionsOutput(BaseModel):
    sections: List[SectionOutput] = Field(description="The list of sections with their headings, descriptions, and CTAs.")


async def generate_section_texts(state: State, config) -> State:
    ordered_sections = state.sections
    enriched_sources = state.enriched_sources

    p = (
        "Using the following enriched source data:\n"
        f"{json.dumps(enriched_sources, indent=2)}\n\n"
        "Generate short, engaging descriptions for each of the ordered newsletter sections:\n"
        f"{json.dumps(ordered_sections, indent=2)}\n\n"
        "Ensure that each section includes relevant details from the sources and adds a CTA if appropriate."
    )
    
    state.messages.append(HumanMessage(content=p))
    
    raw_model = init_model(config)
    bound_model = raw_model.with_structured_output(GenerateSectionsOutput)
    response = cast(GenerateSectionsOutput, await bound_model.ainvoke(state.messages))

    if response and response.sections:
        state.final_sections = [section.dict() for section in response.sections]

    return state


from langgraph.graph import StateGraph

workflow = StateGraph(State, input=InputState, output=OutputState)

workflow.add_node("analyze_enriched_data", analyze_enriched_data)
workflow.add_node("create_sections", create_sections)
workflow.add_node("generate_section_texts", generate_section_texts)

workflow.add_edge("__start__", "analyze_enriched_data")
workflow.add_edge("analyze_enriched_data", "create_sections")
workflow.add_edge("create_sections", "generate_section_texts")
workflow.add_edge("generate_section_texts", "__end__")

graph = workflow.compile()