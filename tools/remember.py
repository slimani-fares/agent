from memory.store import add

SCHEMA = {
    "type": "function",
    "function": {
        "name": "remember",
        "description": (
            "Remembers the provided information for later retrieval. The text can be any string of information that the agent may want to recall in the future. Returns a confirmation message after remembering the information u should also include metadata it is required."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The information to remember.",
                },
                "metadata": {
                    "type": "object",   
                    "description": "Required metadata to associate with the remembered information. This can include any relevant details that may help in retrieving the information later, such as tags, categories, or timestamps.",
                }
            },
            "required": ["text", "metadata"],
        },
    },
}


def remember(text: str, metadata: dict) -> str:
    add(text, metadata )
    return f"Remembered: {text!r}"  
    