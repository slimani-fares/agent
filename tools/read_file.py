from pathlib import Path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Reads a UTF-8 text file from the workspace and returns its contents. The path must be relative to the workspace root (e.g., 'notes.txt', 'data/sales.csv'). Returns an error string if the file doesn't exist, isn't a text file, is too large (>50KB), or escapes the workspace directory ."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "the file path relative to the wrokspace",
                },
            },
            "required": ["path"],
        },
    },
}

WORKSPACE = Path("workspace").resolve()
MAX_READ_BYTES = 50_000


def read_file(path: str) -> str:
    try:
        target = (WORKSPACE / path).resolve()
        if not target.is_relative_to(WORKSPACE):
            return f"Error: path {path!r} escapes the workspace directory."

        if not target.exists():
            return f"Error: file {path!r} not found."
        if not target.is_file():
            return f"Error: {path!r} is not a file."

        with target.open("r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_READ_BYTES + 1)

        if len(content) > MAX_READ_BYTES:
            return content[:MAX_READ_BYTES] + f"\n\n[truncated: file exceeds {MAX_READ_BYTES} bytes]"
        return content

    except Exception as e:
        return f"Error reading {path!r}: {type(e).__name__}: {e}"
