import os
import json
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError

load_dotenv()


# ---------- System prompt ----------
instructions = "You are an Agent and your name is Limbo"


# ---------- Tool: calculator ----------
calculator_declaration = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Evaluates a Python mathematical expression and returns the result as a string. "
            "Use Python operators: + - * / for basic ops, ** for exponentiation (NOT ^), "
            "// for integer division, % for modulo. Use parentheses for grouping. "
            "Examples: '5 ** 2' for 5 squared, '(10 + 2) * 3', '2 ** 0.5' for square root."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A string representing the mathematical expression to evaluate.",
                },
            },
            "required": ["expression"],
        },
    },
}


def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression {expression!r}: {type(e).__name__}: {e}"


# ---------- LLM setup ----------
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.3-70b-versatile"

tools = [calculator_declaration]


# ---------- Chat loop ----------
chat_history = [{"role": "system", "content": instructions}]

print("Welcome back !")
while True:
    user_input = input("You :").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Bye.")
        break
    if not user_input:
        continue

    chat_history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=chat_history,
            temperature=0,
            tools=tools,
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls

        if tool_calls:
            # 1. Record the model's tool_call turn (must include tool_calls).
            chat_history.append({
                "role": "assistant",
                "content": message.content,  # often None when there are tool_calls
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

            # 2. Dispatch each tool call.
            for tc in tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)

                if name == "calculator":
                    result = calculator(**args)
                else:
                    result = f"Error: unknown tool {name}"

                # 3. Append the tool result.
                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            # 4. Second API call: model produces the user-facing reply.
            response = client.chat.completions.create(
                model=MODEL,
                messages=chat_history,
                temperature=0,
                tools=tools,
            )
            final_text = response.choices[0].message.content
            print(final_text)
            chat_history.append({"role": "assistant", "content": final_text})

        else:
            print(message.content)
            chat_history.append({"role": "assistant", "content": message.content})

    except (APIError, RateLimitError) as e:
        print(f"API error: {e}")
        chat_history.pop()
        continue