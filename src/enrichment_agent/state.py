import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, List, Optional, Dict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class InputState:
    topic: str
    sources_gathered: Optional[list] = None

@dataclass(kw_only=True)
class State(InputState):
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)
    enriched_sources: List[Dict[str, Any]] = field(default_factory=list)
    loop_step: Annotated[int, operator.add] = field(default=0)


@dataclass(kw_only=True)
class OutputState:
    enriched_sources: List[dict[str, Any]] = field(default_factory=list)
