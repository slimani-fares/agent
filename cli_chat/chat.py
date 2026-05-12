import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

instructions="You are an LLM for a coding Agent and your name is Limbo"
chat_history=[]


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
         model="gemini-3-flash-preview",
       config=types.GenerateContentConfig(
        system_instruction=instructions,
        # >1==> more creative (token probabilities get closer to each other)--- ~0 => almost determinstic (same prompt=same response) 
        temperature=1
        ),
    contents=chat_history
    # contents=user_input
)
    print(response.text)
    chat_history.append({"role": "model", "parts": [{"text": response.text}]})

    
    


    