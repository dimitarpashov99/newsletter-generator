from dataclasses import dataclass, field
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage

@dataclass
class InputState:
    topic: str
    enriched_sources: list

@dataclass
class State(InputState):
    classified_sources: List[Dict[str, str]] = field(default_factory=list)
    key_topics: List[str] = field(default_factory=list)
    draft_structure: List[Dict[str, Any]] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    ordered_sections: List[Dict[str, Any]] = field(default_factory=list)
    final_sections: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[HumanMessage] = field(default_factory=list)

@dataclass
class OutputState:
    topic: str
    final_sections: List[Dict[str, Any]]