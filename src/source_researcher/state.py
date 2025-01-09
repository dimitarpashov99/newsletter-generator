import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class InputState:
    topic: str
    extraction_schema: Optional[Dict[str, Any]] = field(default=None)
    info: Optional[Dict[str, Any]] = field(default=None)

@dataclass(kw_only=True)
class State(InputState):
    messages: Annotated[List[BaseMessage], add_messages] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    loop_step: Annotated[int, operator.add] = field(default=0)


@dataclass(kw_only=True)
class OutputState:
    info: Dict[str, Any]
