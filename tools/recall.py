from memory.store import search

SCHEMA = {
    "type": "function",
    "function": {
        "name": "recall",
        "description": (
            "Recalls information that has been previously remembered. The text can be any string of information that the agent may want to recall in the future. Returns the recalled information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The information to recall.",
                },
            },
            "required": ["text"],
        },
    },
}

def recall(text: str) -> str:
    result = search(text)
    return str(result)

