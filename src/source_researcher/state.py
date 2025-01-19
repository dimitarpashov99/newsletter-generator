import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class InputState:
    topic: str

@dataclass(kw_only=True)
class State(InputState):
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)
    research_query: Annotated[str, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    continue_research: bool = field(default=0)
    loop_step: Annotated[int, operator.add] = field(default=0)


@dataclass(kw_only=True)
class OutputState:
    sources_gathered: Dict[str, Any]
