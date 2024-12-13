from typing import Any, Dict

import pytest
# from langsmith import unit

from enrichment_agent import graph


@pytest.fixture(scope="function")
def extraction_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "founder": {
                "type": "string",
                "description": "The name of the company founder.",
            },
            "websiteUrl": {
                "type": "string",
                "description": "Website URL of the company, e.g.: https://openai.com/, or https://microsoft.com",
            },
            "products_sold": {
                "type": "array",
                "items": {"type": "string"},
                "description": "A list of products sold by the company.",
            },
        },
        "required": ["founder", "websiteUrl", "products_sold"],
    }


@pytest.mark.asyncio
async def test_researcher_simple_runthrough(extraction_schema: Dict[str, Any]) -> None:
    res = await graph.ainvoke(
        {
            "topic": "LangChain",
            "extraction_schema": extraction_schema,
        }
    )

    assert res["info"] is not None
    assert "harrison" in res["info"]["founder"].lower()
