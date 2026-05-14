import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()


# the system prompt
instructions="You are a coding Agent and your name is Limbo, you are used in the CLI,you can code in anh programming language, you reply in short concise direct words you dont talk much because your goal is not mainly conversation but is to code so you stick to the minimum possible to understand what the user wants, when the user want to code something you always suggest a plan first you dont code directly and then you ask the user for approval before you start, when the user asks for something you dont throw up a milion step plan at once work through it step by step"
# print(instructions)
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

    
    


    