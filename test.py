from memory.store import add, search

add("the user's favorite color is red", {"user_id": 1})
add("the user lives in Paris", {"user_id": 1})
add("the user is building an agent called Limbo", {"user_id": 1})

for r in search("where does the user live?"):
    print(f"{r['distance']:.3f}  {r['text']}")