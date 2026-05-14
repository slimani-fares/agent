import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

load_dotenv()


# ---------- System prompt ----------
instructions = "You are an Agent and your name is Limbo"


# ---------- Tool: calculator ----------
calculator_declaration = {
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
}


def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression {expression!r}: {type(e).__name__}: {e}"


# ---------- LLM setup ----------
client = genai.Client()
MODEL = "gemini-2.5-flash-lite"

calculator_tool = types.Tool(function_declarations=[calculator_declaration])

config = types.GenerateContentConfig(
    system_instruction=instructions,
    # >1 => more creative; ~0 => near-deterministic
    temperature=1,
    tools=[calculator_tool],
)


# ---------- Chat loop ----------
chat_history = []

print("Welcome back !")
while True:
    user_input = input("You :").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Bye.")
        break
    if not user_input:
        continue

    chat_history.append({"role": "user", "parts": [{"text": user_input}]})

    try:
        response = client.models.generate_content(
            model=MODEL,
            config=config,
            contents=chat_history,
        )

        tool_call = response.candidates[0].content.parts[0].function_call

        if tool_call:
            # 1. Record the model's function_call turn.
            chat_history.append(response.candidates[0].content)

            # 2. Dispatch to the matching Python function.
            if tool_call.name == "calculator":
                result = calculator(**tool_call.args)

                # 3. Send the tool result back to the model.
                chat_history.append({
                    "role": "user",
                    "parts": [{
                        "function_response": {
                            "name": tool_call.name,
                            "response": {"result": result},
                        }
                    }],
                })

                # 4. Second API call: model produces the user-facing reply.
                response = client.models.generate_content(
                    model=MODEL,
                    config=config,
                    contents=chat_history,
                )
                print(response.text)
                chat_history.append({"role": "model", "parts": [{"text": response.text}]})
        else:
            print(response.text)
            chat_history.append({"role": "model", "parts": [{"text": response.text}]})

    except (ClientError, ServerError) as e:
        print(f" API error {e.code}: {e.message}")
        chat_history.pop()
        continue