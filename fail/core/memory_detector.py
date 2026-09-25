from ollama import chat

from fail.core.memory_candidate import MemoryCandidate

MEMORY_DETECTOR_PROMPT = """
You are FAiL's memory evaluation system.

Your job is NOT to respond to the user.

Your job is to decide whether the user's latest message contains
information worth storing as long-term memory about the creator.

Remember long-term information such as:
- stable identity facts
- persistent preferences
- ongoing projects
- recurring workflows
- explicit goals
- useful long-term facts

Do NOT remember:
- greetings
- temporary moods
- casual conversation
- one-time requests
- temporary circumstances
- ordinary questions
- information about other people unless it is clearly relevant to
  the creator's long-term context

Rules:
1. Only mark should_remember=true when the information has meaningful
   long-term value.
2. Use certainty="confirmed" when the creator explicitly stated it.
3. Use certainty="learned" only when the pattern is supported by repeated
   behaviour.
4. Use certainty="inferred" for a reasonable but unconfirmed conclusion.
5. Never invent memories.
6. If should_remember=false, use an empty memory string.
7. Return only data matching the requested schema.
"""


def detect_memory_candidate(
    user_message: str,
) -> MemoryCandidate:
    response = chat(
        model="qwen3:1.7b",
        messages=[
            {
                "role": "system",
                "content": MEMORY_DETECTOR_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        format=MemoryCandidate.model_json_schema(),
        think=False,
        options={"temperature": 0},
    )

    return MemoryCandidate.model_validate_json(
        response.message.content
    )