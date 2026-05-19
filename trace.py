import json
import os
import uuid
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(os.environ.get("TRACE_LOG_PATH",
    f"traces/trace-{datetime.now():%Y%m%d-%H%M%S}.jsonl"))

LOG_PATH.parent.mkdir(exist_ok=True)

# A turn = one user input and everything that happens because of it.
_current_turn_id: str | None = None


def new_turn() -> str:
    """Call at the start of each user input. Returns the turn id."""
    global _current_turn_id
    _current_turn_id = uuid.uuid4().hex[:8]
    return _current_turn_id


def log(event: str, **payload) -> None:
    """Append one event to the trace file."""
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "turn_id": _current_turn_id,
        "event": event,
        **payload,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")