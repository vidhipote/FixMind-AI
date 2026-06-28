import json
import os
from datetime import datetime

MEMORY_FILE = "memory_store.json"


def load_memories():
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_memory(problem, solution):
    memories = load_memories()

    memory = {
        "problem": problem,
        "solution": solution,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
    }

    memories.append(memory)

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memories, file, indent=4)

    return memory


def search_memory(query):
    memories = load_memories()
    query_words = query.lower().split()

    results = []

    for memory in memories:
        text = (memory["problem"] + " " + memory["solution"]).lower()

        score = sum(1 for word in query_words if word in text)

        if score > 0:
            results.append(memory)

    return results[:3]