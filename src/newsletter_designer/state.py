import operator
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from langchain_core.messages import BaseMessage


@dataclass(kw_only=True)
class InputState:
    topic: str 
    draft_structure: List[Dict[str, str]]
    audience_type: Optional[str] = None
    theme: Optional[str] = None

@dataclass(kw_only=True)
class State(InputState):
    messages: List[BaseMessage] = field(default_factory=list)
    final_email_template: Optional[str] = None
    meta_info: Optional[Dict[str, str]] = None

@dataclass(kw_only=True)
class OutputState:
    final_email_template: str
    meta_info: Dict[str, str]

