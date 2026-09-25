"""Machine-readable description of FAiL's currently implemented architecture."""

ARCHITECTURE = {
    "project": "FAiL",
    "scope": "Currently implemented code only",
    "subsystems": {
        "cli_agent_loop": {
            "implemented": True,
            "description": (
                "A synchronous terminal chat loop in fail.main. It loads identity "
                "and memories at startup, keeps an in-memory message list, routes "
                "each user message, and makes up to three Ollama tool-call rounds."
            ),
        },
        "identity": {
            "implemented": True,
            "description": (
                "Loads a named Markdown profile from fail/memory/identity and uses "
                "its text in the system prompt."
            ),
        },
        "model_router": {
            "implemented": True,
            "description": (
                "Selects llama3.2:1b for ordinary messages and qwen3:1.7b when "
                "configured complexity phrases occur or the message exceeds 300 "
                "characters."
            ),
        },
        "ollama_model_calls": {
            "implemented": True,
            "description": (
                "Uses ollama.chat for chat responses and for structured memory "
                "candidate detection."
            ),
        },
        "memory_persistence": {
            "implemented": True,
            "description": (
                "Loads and appends memory records in a local JSON file. Records "
                "contain memory text, type, and certainty."
            ),
        },
        "memory_detection_and_policy": {
            "implemented": True,
            "description": (
                "A phrase prefilter may invoke a qwen3:1.7b structured-output "
                "detector. Approved non-empty candidates are normalized and saved."
            ),
        },
        "tool_registry": {
            "implemented": True,
            "description": (
                "An in-memory registry stores named Tool objects and exposes their "
                "descriptions. The current startup registers only create_note."
            ),
        },
        "tool_manager": {
            "implemented": True,
            "description": (
                "Validates tool existence and required parameters, applies a folder "
                "allowlist when a folder argument is supplied, then executes the tool."
            ),
        },
        "tool_capability_gating": {
            "implemented": True,
            "description": (
                "The create_note schema is sent to Ollama only when the user input "
                "contains one of the configured note-request phrases."
            ),
        },
        "obsidian_note_writing": {
            "implemented": True,
            "description": (
                "create_note writes supplied Markdown content to a title-based .md "
                "path beneath the configured Obsidian vault path."
            ),
        },
        "obsidian_note_reading": {
            "implemented": False,
            "description": (
                "Reading, accessing, searching, or listing existing Obsidian notes "
                "is not implemented."
            ),
        },
        "rbac": {
            "implemented": False,
            "description": "Role-based access control is not implemented.",
        },
        "audit_logging": {
            "implemented": False,
            "description": "Audit logging is not implemented.",
        },
        "knowledge_graphs": {
            "implemented": False,
            "description": "Knowledge graph storage or processing is not implemented.",
        },
        "autonomous_planning": {
            "implemented": False,
            "description": (
                "Autonomous planning or background task execution is not implemented."
            ),
        },
        "memory_retrieval_or_ranking": {
            "implemented": False,
            "description": (
                "Memory retrieval, ranking, search, and deduplication are not implemented."
            ),
        },
        "general_policy_enforcement": {
            "implemented": False,
            "description": (
                "A general policy engine is not implemented; the only code-level "
                "permission check is the tool manager's folder allowlist."
            ),
        },
    },
}


def format_architecture() -> str:
    """Return the authoritative architecture as concise prompt-ready text."""

    implemented = []
    unimplemented = []

    for name, subsystem in ARCHITECTURE["subsystems"].items():
        item = f"- {name}: {subsystem['description']}"

        if subsystem["implemented"]:
            implemented.append(item)
        else:
            unimplemented.append(item)

    return "\n".join(
        [
            "Implemented capabilities:",
            *implemented,
            "Not implemented:",
            *unimplemented,
        ]
    )


def get_capability_status(capability: str):
    """Return the authoritative architecture entry matching a capability."""

    normalized = capability.lower().strip()

    for name, subsystem in ARCHITECTURE["subsystems"].items():
        if name.lower() == normalized:
            return {
                "implemented": subsystem["implemented"],
                "subsystem": name,
                "description": subsystem["description"],
            }

    return None


CAPABILITY_ALIASES = {
    "create obsidian notes": "obsidian_note_writing",
    "write obsidian notes": "obsidian_note_writing",
    "make obsidian notes": "obsidian_note_writing",
    "edit existing obsidian notes": "obsidian_note_reading",
    "edit obsidian notes": "obsidian_note_reading",
    "read obsidian notes": "obsidian_note_reading",
    "read existing obsidian notes": "obsidian_note_reading",
    "access existing obsidian notes": "obsidian_note_reading",
    "search obsidian notes": "obsidian_note_reading",
    "list obsidian notes": "obsidian_note_reading",
    "knowledge graphs": "knowledge_graphs",
    "autonomous planning": "autonomous_planning",
    "rbac": "rbac",
    "role based access control": "rbac",
    "audit logging": "audit_logging",
    "memory retrieval": "memory_retrieval_or_ranking",
    "memory ranking": "memory_retrieval_or_ranking",
}


def resolve_capability_alias(capability: str):
    """Resolve a human-readable capability to an architecture subsystem."""

    normalized = capability.lower().strip()

    subsystem_name = CAPABILITY_ALIASES.get(normalized)

    if subsystem_name is None:
        return None

    return get_capability_status(subsystem_name)


def find_capability_for_question(question: str):
    """Find an explicitly known capability relevant to a user question."""

    normalized = question.lower().strip()

    for alias, subsystem_name in CAPABILITY_ALIASES.items():
        if alias in normalized:
            return get_capability_status(subsystem_name)

    return None


__all__ = [
    "ARCHITECTURE",
    "format_architecture",
    "get_capability_status",
    "CAPABILITY_ALIASES",
    "resolve_capability_alias",
    "find_capability_for_question",
]