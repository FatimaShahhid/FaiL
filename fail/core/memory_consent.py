"""Explicit human consent for persisting memory candidates."""


def request_memory_consent(
    memory: str,
    input_fn=None,
    output_fn=print,
) -> bool:
    """Present one eligible memory candidate and return explicit consent only."""

    if input_fn is None:
        input_fn = input

    output_fn(f"\nFAiL memory candidate: {memory}")
    response = input_fn("Save this memory? [y/N]: ")

    return response.strip().lower() in {"y", "yes"}
