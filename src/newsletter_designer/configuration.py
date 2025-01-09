from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

from newsletter_designer import prompts

@dataclass(kw_only=True)
class Configuration:
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The name of the language model to use for the agent. "
            "Should be in the form: provider/model-name."
        },
    )
    prompt: str = field(
        default=prompts.MAIN_PROMPT,
        metadata={
            "description": "The main prompt template to use for the agent's interactions. "
            "Expects an f-string arguments: {topic}."
        },
    )
    max_info_tool_calls: int = field(
        default=3,
        metadata={
            "description": "The maximum number of times the Info tool can be called during a single interaction."
        },
    )
    max_loops: int = field(
        default=6,
        metadata={
            "description": "The maximum number of interaction loops allowed before the agent terminates."
        },
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})