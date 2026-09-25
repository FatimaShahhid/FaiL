from typing import Literal

from pydantic import BaseModel


class MemoryCandidate(BaseModel):
    """A model proposal; certainty is a detector assessment, not human consent."""

    should_remember: bool
    memory: str
    memory_type: Literal[
        "identity",
        "preference",
        "project",
        "workflow",
        "goal",
        "fact",
        "other",
    ]
    certainty: Literal[
        "confirmed",
        "learned",
        "inferred",
    ]
    reason: str
