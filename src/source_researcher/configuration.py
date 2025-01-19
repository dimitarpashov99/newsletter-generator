from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional, Any, Dict

from langchain_core.runnables import RunnableConfig, ensure_config

from source_researcher import prompts

@dataclass(kw_only=True)
class Configuration:
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4o-mini",
        metadata={
            "description": "The name of the language model to use for the agent. "
            "Should be in the form: provider/model-name."
        },
    )
    max_search_results: int = field(
        default=5,
        metadata={
            "description": "The maximum number of search results to return for each search query."
        },
    )
    max_loops: int = field(
        default=1,
        metadata={
            "description": "The maximum number of interaction loops allowed before the agent terminates."
        },
    )

    extraction_schema: Dict[str, Any] = field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_name": {
                                "type": "string",
                                "description": "Name of the source (e.g., website, blog, social media account, video channel)"
                            },
                            "url": {
                                "type": "string",
                                "description": "URL to the source or specific content"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content of the source"
                            },
                            "content_type": {
                                "type": "string",
                                "description": "Type of content provided by the source (e.g., blog post, video, social media, tutorial)"
                            },
                            "relevance": {
                                "type": "string",
                                "description": "How relevant the source is to the topic based on the provided information"
                            },
                            "authority": {
                                "type": "string",
                                "description": "A brief description of the source's authority or credibility on the topic"
                            },
                            "frequency_of_updates": {
                                "type": "string",
                                "description": "How often the source is updated with new information"
                            },
                            "focus_area": {
                                "type": "string",
                                "description": "A short summary of the specific focus area or niche covered by the source"
                            }
                        },
                        "required": [
                            "source_name",
                            "url",
                            "content",
                            "content_type",
                            "relevance",
                            "authority"
                        ]
                    },
                    "description": "List of identified information sources relevant to the topic"
                }
            },
            "required": ["sources"]
        },
        metadata={
            "description": "The JSON schema used for validating extracted information from sources."
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
