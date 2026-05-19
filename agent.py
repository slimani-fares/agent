import os
import json
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError
from trace import new_turn, log
from tools import TOOLS, TOOL_SCHEMAS
from config import MODEL, MAX_TOOL_ITERATIONS

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)


def run_turn(chat_history, user_input):
    history_checkpoint = len(chat_history)

    chat_history.append({"role": "user", "content": user_input})

    new_turn()
    log("user_input", text=user_input)

    log("api_request", model=MODEL, messages=chat_history, tools=[t["function"]["name"] for t in TOOL_SCHEMAS])

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=chat_history,
            temperature=0,
            tools=TOOL_SCHEMAS,
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        log("api_response",
            content=message.content,
            tool_calls=[{"name": tc.function.name, "args": tc.function.arguments} for tc in (message.tool_calls or [])],
            finish_reason=response.choices[0].finish_reason,
            usage=response.usage.model_dump() if response.usage else None)

        iterations = 0

        while tool_calls:
            iterations += 1
            if iterations > MAX_TOOL_ITERATIONS:
                log("error", message=f"exceeded {MAX_TOOL_ITERATIONS} tool iterations")
                break

            chat_history.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            })

            for tc in tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)

                log("tool_call", name=name, args=args)

                fn = TOOLS.get(name)
                if fn is None:
                    result = f"Error: unknown tool {name}"
                else:
                    try:
                        result = fn(**args)
                    except Exception as e:
                        result = f"Error running {name}: {type(e).__name__}: {e}"

                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

                log("tool_result", name=name, result=result)

            log("api_request", model=MODEL, messages=chat_history, tools=[t["function"]["name"] for t in TOOL_SCHEMAS])

            response = client.chat.completions.create(
                model=MODEL,
                messages=chat_history,
                temperature=0,
                tools=TOOL_SCHEMAS,
            )
            message = response.choices[0].message
            tool_calls = message.tool_calls

            log("api_response",
                content=message.content,
                tool_calls=[{"name": tc.function.name, "args": tc.function.arguments} for tc in (message.tool_calls or [])],
                finish_reason=response.choices[0].finish_reason,
                usage=response.usage.model_dump() if response.usage else None)

        chat_history.append({"role": "assistant", "content": message.content})
        log("final_reply", text=message.content)
        return chat_history, message.content

    except (APIError, RateLimitError) as e:
        log("error", message=str(e), type=type(e).__name__)
        rolled_back = chat_history[:history_checkpoint]
        return rolled_back, f"API error: {e}"
