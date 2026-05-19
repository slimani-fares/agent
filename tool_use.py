import os
import json
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError
from tavily import TavilyClient
from trace import new_turn, log

load_dotenv()


# ---------- System prompt ----------
instructions = "You are an Agent and your name is Limbo, you have access to tools and you can use them when needed or when user demands so"


# ---------- Tools declaration ----------
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

web_search_declaration = {
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




# ---------- Tools----------


#a simple calculator tool for learning 
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression {expression!r}: {type(e).__name__}: {e}"
    

#Tavily web search client 
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

# ---------- LLM setup ----------
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "openai/gpt-oss-120b"

tools = [calculator_declaration,web_search_declaration]


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


    #Checkpoint
    history_checkpoint = len(chat_history) 


    #appending the user input to hisotry
    chat_history.append({"role": "user", "content": user_input})

    #logging the user input 
    new_turn()
    log("user_input", text=user_input)

    #logging of the api call 
    log("api_request", model=MODEL, messages=chat_history, tools=[t["function"]["name"] for t in tools])

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=chat_history,
            temperature=0,
            tools=tools,
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls


        #logging response 
        log("api_response",
        content=message.content,
        tool_calls=[{"name": tc.function.name, "args": tc.function.arguments} for tc in (message.tool_calls or [])],
        finish_reason=response.choices[0].finish_reason,
        usage=response.usage.model_dump() if response.usage else None)

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

                log("tool_call", name=name, args=args)

                if name == "calculator":
                    result = calculator(**args)
                elif name== "web_search":
                    result=web_search(**args)
                else:
                    result = f"Error: unknown tool {name}"

                # 3. Append and log the tool result.
                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

                log("tool_result", name=name, result=result)

            # 4. Second API call: model produces the user-facing reply.

            log("api_request", model=MODEL, messages=chat_history, tools=[t["function"]["name"] for t in tools])

            response = client.chat.completions.create(
                model=MODEL,
                messages=chat_history,
                temperature=0,
                tools=tools,
            )
            message = response.choices[0].message
            #logging the response 
            log("api_response",
            content=message.content,
            tool_calls=[{"name": tc.function.name, "args": tc.function.arguments} for tc in (message.tool_calls or [])],
            finish_reason=response.choices[0].finish_reason,
            usage=response.usage.model_dump() if response.usage else None)
            final_text = message.content
            print(final_text)
            chat_history.append({"role": "assistant", "content": final_text})
            log("final_reply", text=final_text)
            

        else:
            print(message.content)
            chat_history.append({"role": "assistant", "content": message.content})
            log("final_reply", text=message.content)

    except (APIError, RateLimitError) as e:
        print(f"API error: {e}")
        log("error", message=str(e), type=type(e).__name__)
        #rollback history to the latest checkpoint in case of an error
        chat_history = chat_history[:history_checkpoint] 
        continue