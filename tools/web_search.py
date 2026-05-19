import os
from tavily import TavilyClient

SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "used to search the web we then user wants information you dont know or its past you latest date of information"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "the search query",
                },
            },
            "required": ["query"],
        },
    },
}

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def web_search(query: str) -> str:
    try:
        results = tavily.search(query=query, max_results=5)
    except Exception as e:
        return f"Error searching {query!r}: {type(e).__name__}: {e}"

    items = results.get("results", [])
    if not items:
        return f"No results for {query!r}."

    formatted = []
    for i, item in enumerate(items, start=1):
        formatted.append(
            f"[{i}] {item.get('title', 'No title')}\n"
            f"URL: {item.get('url', '')}\n"
            f"{item.get('content', '')}"
        )
    return "\n\n".join(formatted)
