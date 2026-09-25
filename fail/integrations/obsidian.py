import os
from pathlib import Path


VAULT_PATH = Path(
    os.environ.get(
        "FAIL_OBSIDIAN_VAULT",
        Path.home() / "Documents" / "AI-Lab" / "Obsidian" / "AI-Lab",
    )
)


def create_note(folder: str, title: str, content: str) -> str:
    note_folder = VAULT_PATH / folder
    note_folder.mkdir(parents=True, exist_ok=True)

    note_path = note_folder / f"{title}.md"

    note_path.write_text(
        content,
        encoding="utf-8",
    )

    return str(note_path)