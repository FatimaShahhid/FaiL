from dataclasses import dataclass


@dataclass(frozen=True)
class ModelChoice:
    model: str
    reason: str


FAST_MODEL = "llama3.2:1b"
STRONG_MODEL = "qwen3:1.7b"


COMPLEXITY_WORDS = (
    "analyze",
    "analyse",
    "compare",
    "explain",
    "design",
    "debug",
    "troubleshoot",
    "architecture",
    "implement",
    "build",
    "develop",
    "reason",
    "plan",
    "research",
    "why",
    "how does",
)


def choose_model(user_message: str) -> ModelChoice:
    """Choose an appropriate local model for a user request."""

    text = user_message.lower().strip()

    if any(word in text for word in COMPLEXITY_WORDS):
        return ModelChoice(
            model=STRONG_MODEL,
            reason="The request appears to require deeper reasoning or technical analysis.",
        )

    if len(text) > 300:
        return ModelChoice(
            model=STRONG_MODEL,
            reason="The request is relatively long and may require more context handling.",
        )

    return ModelChoice(
        model=FAST_MODEL,
        reason="The request appears suitable for fast conversational processing.",
    )