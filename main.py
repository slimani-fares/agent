from dotenv import load_dotenv
load_dotenv()

from agent import run_turn
from config import INSTRUCTIONS

chat_history = [{"role": "system", "content": INSTRUCTIONS}]

print("Welcome back !")
while True:
    user_input = input("You :").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Bye.")
        break
    if not user_input:
        continue

    chat_history, reply = run_turn(chat_history, user_input)
    print(reply)
