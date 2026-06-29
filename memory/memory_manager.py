import json
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path("memory_store.json")


def load_memories():
    if not MEMORY_FILE.exists():
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_memory(problem, solution):
    memories = load_memories()

    for memory in memories:
        if memory["problem"].strip().lower() == problem.strip().lower():
            return False

    new_memory = {
        "problem": problem,
        "solution": solution,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
    }

    memories.append(new_memory)

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memories, file, indent=4, ensure_ascii=False)

    return True


def search_memory(query):
    memories = load_memories()
    query_words = query.lower().split()

    matches = []

    for memory in memories:
        problem = memory["problem"].lower()
        solution = memory["solution"].lower()

        if any(word in problem or word in solution for word in query_words):
            matches.append(memory)

    return matches


def delete_memory(index):
    memories = load_memories()

    if 0 <= index < len(memories):
        memories.pop(index)

        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memories, file, indent=4, ensure_ascii=False)

        return True

    return False