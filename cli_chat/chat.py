import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

load_dotenv()

client = genai.Client()
chat_history=[]


# the system prompt
instructions = "You are a coding Agent and your name is Limbo, you are used in the CLI, you can code in any programming language, you reply in short concise direct words you dont talk much because your goal is not mainly conversation but is to code so you stick to the minimum possible to understand what the user wants, when the user wants to code something you always suggest a plan first you dont code directly and then you ask the user for approval before you start, when the user asks for something you dont throw up a million step plan at once work through it step by step\n\nYour response will be structured. Use 'reasoning' to briefly think about what the user wants before classifying. Use 'intent' to classify the user message: 'greeting' for hellos, 'code_request' for new coding tasks, 'code_followup' for modifications to prior code, 'off_topic' for non-coding questions, 'meta_question' for questions about this conversation itself, 'approval' for confirmations like 'yes' or 'go ahead', 'other' only when nothing else fits. Put your actual user-facing reply in 'response'. The 'confidence' field is a number between 0 and 1 reflecting how sure you are about the intent classification."
# print(instructions)



response_schema = {
    "type": "object",
    "properties": {
    
        "reasoning": {
            "type": "string",
            "description": "Brief reasoning about what the user wants, generated before classifying intent."
        },
        "intent": {
            "type": "string",
            "enum": [
                "greeting",
                "code_request",
                "code_followup",
                "off_topic",
                "meta_question",
                "approval",
                "other"
            ]
        },
        "response": {"type": "string"},
        "confidence": {
            "type": "number"
        }
    },
    "required": ["reasoning", "intent", "response", "confidence"]
}



print("Welcome back !")
while True:
    user_input = input("You :").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Bye.")
        break
    if not user_input:
        continue
    chat_history.append({"role": "user", "parts": [{"text": user_input}]})
    
    response = client.models.generate_content(
         model="gemini-2.5-flash",
       config=types.GenerateContentConfig(
        system_instruction=instructions,
        # >1==> more creative (token probabilities get closer to each other)--- ~0 => almost determinstic (same prompt=same response) 
        temperature=1,
        response_mime_type="application/json",
        response_schema=response_schema,


        ),
    
    contents=chat_history
)
    raw_response = response.text
    #in case i want to print raw
    # print("=== RAW MODEL OUTPUT ===")
    # print(repr(raw_response))
    # print("=== END RAW ===")

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as e:
        print(f"JSON PARSE FAILED: {e}")
        continue

    # Pretty-print the structured fields 
    print(f"[reasoning] {parsed.get('reasoning')}")
    print(f"[intent]    {parsed.get('intent')}")
    print(f"[confidence] {parsed.get('confidence')}")
    print(f"Limbo: {parsed.get('response')}")

    # Store only the user-facing reply in history, not the full JSON blob
    chat_history.append({
        "role": "model",
        "parts": [{"text": parsed["response"]}]
    })
    
    


    