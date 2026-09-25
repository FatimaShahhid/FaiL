import json
from pathlib import Path


MEMORY_PATH = (
    Path(__file__).resolve().parent.parent
    / "memory"
    / "persistent"
    / "memories.json"
)


def load_memories() -> list:
    """Load FAiL's persistent memories without changing legacy records."""
    if not MEMORY_PATH.exists():
        return []

    with MEMORY_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("memories", [])


def save_memory(memory: dict) -> None:
    """Save one new memory to FAiL's persistent memory."""
    memories = load_memories()
    memories.append(memory)

    with MEMORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            {"memories": memories},
            file,
            indent=2,
            ensure_ascii=False,
        )
