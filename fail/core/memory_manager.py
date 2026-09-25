from datetime import datetime, timezone
from uuid import uuid4

from fail.core.memory import save_memory


def remember(
    memory: str,
    memory_type: str,
    certainty: str = "confirmed",
) -> None:
    """Persist a consented memory; certainty remains the detector assessment."""

    allowed_certainty = {
        "confirmed",
        "learned",
        "inferred",
        "unknown",
    }

    if certainty not in allowed_certainty:
        raise ValueError(
            f"Invalid certainty '{certainty}'. "
            f"Use one of: {', '.join(sorted(allowed_certainty))}"
        )

    timestamp = datetime.now(timezone.utc).isoformat()

    memory_record = {
        "id": str(uuid4()),
        "memory": memory,
        "type": memory_type,
        "certainty": certainty,
        "status": "active",
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    save_memory(memory_record)
