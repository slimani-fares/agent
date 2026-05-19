"""View a trace.jsonl file as a human-readable timeline.

Usage:
    python view_trace.py trace.jsonl
    python view_trace.py traces/trace-20260519-112147.jsonl
    python view_trace.py trace.jsonl --turn 9ca30ad5     # filter to one turn
    python view_trace.py trace.jsonl --errors            # only turns with errors
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


MAX_FIELD_LEN = 120  # truncate long strings in the compact view


def truncate(s, n=MAX_FIELD_LEN):
    if s is None:
        return ""
    s = str(s).replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def format_event(event: dict) -> str:
    """Return a one-line summary of a single event."""
    ts = event.get("ts", "")
    time = ts.split("T")[-1] if "T" in ts else ts
    kind = event.get("event", "?")

    # one rendering rule per event type — easy to extend
    if kind == "user_input":
        body = f'"{truncate(event.get("text"))}"'
    elif kind == "api_request":
        n = len(event.get("messages", []))
        tools = ",".join(event.get("tools", []))
        body = f"messages={n}  tools=[{tools}]"
    elif kind == "api_response":
        tcs = event.get("tool_calls") or []
        if tcs:
            calls = ", ".join(f'{tc["name"]}({truncate(tc.get("args"), 60)})' for tc in tcs)
            body = f"tool_calls=[{calls}]"
        else:
            body = f'"{truncate(event.get("content"))}"'
        usage = event.get("usage") or {}
        if usage.get("total_tokens"):
            body += f"  ({usage['total_tokens']} tok)"
    elif kind == "tool_call":
        body = f'{event.get("name")}({truncate(json.dumps(event.get("args", {})), 80)})'
    elif kind == "tool_result":
        body = f'{event.get("name")} → "{truncate(event.get("result"), 100)}"'
    elif kind == "final_reply":
        body = f'"{truncate(event.get("text"))}"'
    elif kind == "error":
        body = f'{event.get("type")}: {truncate(event.get("message"))}'
    else:
        body = truncate(json.dumps({k: v for k, v in event.items() if k not in ("ts", "turn_id", "event")}))

    return f"  {time}  {kind:<14} {body}"


def load_turns(path: Path) -> dict[str, list[dict]]:
    """Group events by turn_id, preserving order."""
    turns = defaultdict(list)
    order = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            tid = ev.get("turn_id", "no_turn")
            if tid not in turns:
                order.append(tid)
            turns[tid].append(ev)
    return {tid: turns[tid] for tid in order}


def turn_header(turn_id: str, events: list[dict]) -> str:
    user_ev = next((e for e in events if e["event"] == "user_input"), None)
    user_text = truncate(user_ev["text"], 80) if user_ev else "(no user_input)"
    has_error = any(e["event"] == "error" for e in events)
    n_tool_calls = sum(1 for e in events if e["event"] == "tool_call")
    flags = []
    if has_error: flags.append("ERROR")
    if n_tool_calls: flags.append(f"{n_tool_calls} tool call{'s' if n_tool_calls > 1 else ''}")
    suffix = f"  [{', '.join(flags)}]" if flags else ""
    return f'[turn {turn_id}] "{user_text}"{suffix}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, help="path to trace.jsonl")
    ap.add_argument("--turn", help="filter to a specific turn_id")
    ap.add_argument("--errors", action="store_true", help="only show turns with errors")
    ap.add_argument("--tool", help="only show turns where this tool was called")
    args = ap.parse_args()

    if not args.path.exists():
        sys.exit(f"file not found: {args.path}")

    turns = load_turns(args.path)

    for turn_id, events in turns.items():
        if args.turn and turn_id != args.turn:
            continue
        if args.errors and not any(e["event"] == "error" for e in events):
            continue
        if args.tool and not any(e["event"] == "tool_call" and e.get("name") == args.tool for e in events):
            continue

        print(turn_header(turn_id, events))
        for ev in events:
            print(format_event(ev))
        print()


if __name__ == "__main__":
    main()