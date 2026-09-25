from fail.core.memory_candidate import MemoryCandidate


def is_memory_eligible(candidate: MemoryCandidate) -> bool:
    """
    Decide whether a memory candidate may be presented for human consent.

    Eligibility and detector certainty are not human approval and never authorize
    persistence by themselves.
    """

    if not candidate.should_remember:
        return False

    if not candidate.memory.strip():
        return False

    if candidate.certainty == "unknown":
        return False

    return True


def normalize_memory(
    candidate: MemoryCandidate,
    creator_name: str = "Fatima",
) -> dict:
    """
    Convert an eligible, consented memory candidate into FAiL's
    persistent memory format.
    """

    memory_text = candidate.memory.strip()

    replacements = {
        "The user": creator_name,
        "the user": creator_name,
        "User": creator_name,
        "user": creator_name,
        "The creator": creator_name,
        "the creator": creator_name,
        "Creator": creator_name,
    }

    for old_text, new_text in replacements.items():
        memory_text = memory_text.replace(old_text, new_text)

    return {
        "memory": memory_text,
        "type": candidate.memory_type,
        "certainty": candidate.certainty,
    }
