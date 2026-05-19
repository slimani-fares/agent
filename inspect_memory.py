from memory.store import collection

print(f"Total items: {collection.count()}\n")

# get() with no filter returns everything
data = collection.get(include=["documents", "metadatas", "embeddings"])

for i, (doc, meta) in enumerate(zip(data["ids"], data["documents"])):
    print(f"[{i}] id={data['ids'][i]}")
    print(f"    text: {data['documents'][i]}")
    print(f"    meta: {data['metadatas'][i]}")
    print(f"    vector: {data['embeddings'][i][:5]}... (dim {len(data['embeddings'][i])})")
    print()