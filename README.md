# Limbo

A small AI agent built from scratch to learn how agents actually work: a chat loop,
tool calling, tracing, and vector memory. No agent framework, just the OpenAI SDK
pointed at Groq plus a few libraries.

## Structure

```
main.py             CLI chat loop (type "exit" to quit)
agent.py            the turn loop: call the model, run any tools, feed results back
config.py           model name, tool iteration cap, system prompt
trace.py            JSONL event logger, one file per run in traces/
view_trace.py       renders a trace file as a readable timeline
inspect_memory.py   dumps everything currently stored in the vector db

tools/
  __init__.py       registry mapping tool names to functions and schemas
  calculator.py     evaluates a python math expression
  web_search.py     Tavily search
  read_file.py      reads text files, sandboxed to workspace/
  remember.py       writes a fact to the vector store
  recall.py         semantic search over the vector store

memory/
  store.py          Gemini embeddings + persistent ChromaDB collection
  chunker.py        markdown chunker, splits on headers with header path kept
  ingest.py         walks a folder, chunks files, adds them to the store

workspace/          the only directory read_file can reach
traces/             run logs (gitignored)
chroma_store/       persisted vectors (gitignored)
notes.md            learning journal, phase by phase
```

## How a turn works

`run_turn` appends the user message, calls the model with the full tool schema list,
and loops while the response contains tool calls: execute each one, append the results
as `tool` messages, call again. Capped at `MAX_TOOL_ITERATIONS`. Every step is logged
to the trace file. On an API error the history is rolled back to its state before the
turn, so a failed call does not leave a half finished exchange behind.

## Work done so far

**Phase 2, prompt engineering.** System prompt, structured outputs, reasoning
prompts. Found that asking the model for a confidence score does not give a real
signal since it has no introspective access to its own certainty.

**Phase 3, tool use.** Five tools wired through a schema registry, sequential and
parallel tool calls handled, JSONL tracing with a viewer that supports `--latest`,
`--turn`, `--errors` and `--tool` filters.

**Phase 4, memory and RAG.** Gemini embeddings into a persistent Chroma collection,
`remember` and `recall` exposed as tools, a header aware markdown chunker with a
paragraph fallback for oversized sections, and a folder ingester.

Known rough edge: tools tend to stay unused unless the user asks for them explicitly.
Tool descriptions and the system prompt need work so the model reaches for them on its own.

## Setup

```bash
pip install openai google-genai chromadb tavily-python python-dotenv
cp .env.example .env    # fill in GROQ_API_KEY, GEMINI_API_KEY, TAVILY_API_KEY
python main.py
```

Inspect a run:

```bash
python view_trace.py --latest
python inspect_memory.py
```
