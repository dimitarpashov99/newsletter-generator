from dataclasses import dataclass, field
from typing import List, Dict
from langchain_core.messages import HumanMessage

@dataclass
class InputState:
    topic: str
    sources: List[str]

@dataclass
class State(InputState):
    classified_sources: List[Dict[str, str]] = field(default_factory=list)
    key_topics: List[str] = field(default_factory=list)
    draft_structure: str = ""
    messages: List[HumanMessage] = field(default_factory=list)

@dataclass
class OutputState:
    draft_structure: str

