from fail.tools.tool import Tool
from fail.integrations.obsidian import create_note


def create_obsidian_note(folder: str, title: str, content: str) -> str:
    return create_note(
        folder=folder,
        title=title,
        content=content,
    )


create_note_tool = Tool(
    name="create_note",
    description="Create a Markdown note inside the AI-Lab Obsidian vault.",
    execute=create_obsidian_note,
    parameters={
        "folder": "The Obsidian folder where the note should be created.",
        "title": "The title of the note.",
        "content": "The Markdown content of the note.",
    },
)