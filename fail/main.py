from fail.core.identity_loader import load_identity
from fail.core.architecture import (
    format_architecture,
    find_capability_for_question,
)
from fail.core.memory import load_memories
from fail.core.memory_consent import request_memory_consent
from fail.core.memory_detector import detect_memory_candidate
from fail.core.memory_manager import remember
from fail.core.memory_policy import is_memory_eligible, normalize_memory
from fail.core.model_router import choose_model

from fail.tools.registry import ToolRegistry
from fail.tools.manager import ToolManager
from fail.tools.obsidian_tools import create_note_tool

from ollama import chat


# ============================================================
# MEMORY DETECTION
# ============================================================

MEMORY_TRIGGER_PHRASES = (
    "my name is",
    "i am ",
    "i'm ",
    "i prefer",
    "i like",
    "i don't like",
    "i dislike",
    "i hate",
    "i always",
    "i usually",
    "i never",
    "i want",
    "i need",
    "my goal",
    "my project",
    "i work",
    "i'm working",
    "remember that",
    "don't forget",
)


def looks_like_memory_candidate(message: str) -> bool:
    """Determine whether the user's message may contain a memory."""

    text = message.lower().strip()

    return any(
        phrase in text
        for phrase in MEMORY_TRIGGER_PHRASES
    )


def persist_memory_candidate(
    candidate,
    input_fn=None,
    output_fn=print,
) -> bool:
    """Persist an eligible candidate only after explicit human consent."""

    if not is_memory_eligible(candidate):
        return False

    if not request_memory_consent(
        candidate.memory,
        input_fn=input_fn,
        output_fn=output_fn,
    ):
        return False

    normalized_memory = normalize_memory(candidate)

    remember(
        normalized_memory["memory"],
        normalized_memory["type"],
        normalized_memory["certainty"],
    )

    return True


# ============================================================
# TOOL REQUEST DETECTION
# ============================================================

NOTE_REQUEST_PHRASES = (
    "create a note",
    "create an architecture note",
    "create a research note",
    "create a project note",
    "create a decision note",
    "make a note",
    "make an architecture note",
    "make a research note",
    "make a project note",
    "make a decision note",
    "write a note",
    "write an architecture note",
    "write a research note",
    "write a project note",
    "write a decision note",
    "add a note",
    "save this as a note",
    "save this to obsidian",
    "save this in obsidian",
)


def looks_like_tool_request(message: str) -> bool:
    """Determine whether the user explicitly requested a note."""

    text = message.lower().strip()

    return any(
        phrase in text
        for phrase in NOTE_REQUEST_PHRASES
    )


# ============================================================
# SELF-KNOWLEDGE REQUEST DETECTION
# ============================================================

BROAD_SELF_KNOWLEDGE_PHRASES = (
    "what can you currently do",
    "what can you do",
    "what can't you do",
    "what cannot you do",
    "what are your capabilities",
    "what capabilities do you have",
    "your capabilities",
    "what is implemented",
    "what is not implemented",
    "what isn't implemented",
    "what can fail currently do",
    "what can fail do",
    "what does fail currently do",
    "what does fail do",
)

SPECIFIC_CAPABILITY_PHRASES = (
    "can fail ",
    "does fail ",
    "is fail able to ",
    "does fail support ",
    "do you support ",
    "can you support ",
    "are you able to ",
    "is it possible for you to ",
    "can you ",
    "could you ",
)

CONVERSATIONAL_REQUEST_PREFIXES = (
    "can you explain",
    "could you explain",
    "can you help",
    "could you help",
)

SELF_KNOWLEDGE_REQUEST_PHRASES = (
    *BROAD_SELF_KNOWLEDGE_PHRASES,
    *SPECIFIC_CAPABILITY_PHRASES,
)


def is_self_knowledge_request(message: str) -> bool:
    """Determine whether the user is asking about FAiL's capabilities."""

    text = message.lower().strip()

    if any(text.startswith(prefix) for prefix in CONVERSATIONAL_REQUEST_PREFIXES):
        if find_capability_for_question(message) is None:
            return False

    if find_capability_for_question(message) is not None:
        return True

    if is_broad_self_knowledge_request(message):
        return True

    return any(
        phrase in text
        for phrase in SPECIFIC_CAPABILITY_PHRASES
    )


def is_broad_self_knowledge_request(message: str) -> bool:
    """Determine whether the question is a broad inquiry about FAiL capabilities."""

    text = message.lower().strip()

    return any(
        phrase in text
        for phrase in BROAD_SELF_KNOWLEDGE_PHRASES
    )


# ============================================================
# SELF-KNOWLEDGE / CAPABILITY HANDLING
# ============================================================

def build_self_knowledge_prompt() -> str:
    """Build the restricted prompt for a capability-answering request."""

    return (
        "You are answering a question about FAiL's currently implemented software "
        "capabilities, not general facts. Produce only a natural-language rendering "
        "of the authoritative architecture information below. Do not use general "
        "model knowledge, conversation history, assumptions, or speculation to add "
        "capabilities. Treat entries marked implemented as available and entries "
        "marked not implemented as unavailable. If a capability is not listed as "
        "implemented, say it is not implemented.\n\n"
        "Authoritative architecture information:\n"
        + format_architecture()
    )


def handle_capability_question(user_input: str):
    """Return a deterministic answer for a FAiL capability question."""

    result = find_capability_for_question(user_input)

    if result is not None:
        if result["implemented"]:
            return (
                f"Yes. FAiL currently implements this capability through "
                f"{result['subsystem']}: {result['description']}"
            )

        return (
            f"No. This capability is not currently implemented. "
            f"FAiL's architecture records {result['subsystem']} as not implemented: "
            f"{result['description']}"
        )

    if not is_self_knowledge_request(user_input):
        return None

    if is_broad_self_knowledge_request(user_input):
        return format_architecture()

    return (
        "FAiL's current architecture does not define this capability, "
        "so it cannot be described as an implemented FAiL capability."
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt(
    identity: str,
    memories: list,
) -> str:
    """Build FAiL's system prompt."""

    memory_context = ""

    if memories:

        memory_context = (
            "\n\nKnown memories about the creator:\n"
        )

        for memory in memories:

            memory_context += (
                f"- {memory.get('memory', '')} "
                f"[{memory.get('certainty', 'unknown')}]\n"
            )

    capability_boundary = """

Capability boundary:

- FAiL may only be described as having capabilities that are explicitly implemented in its authoritative architecture or exposed through its available tools.
- Do not invent extensions, APIs, integrations, tools, commands, services, or implementation details for FAiL.
- Do not describe planned or hypothetical functionality as if it already exists.
- If asked whether FAiL can perform something that is not implemented, say that it is not currently implemented.
- The model does not define FAiL's capabilities; the FAiL architecture and runtime do.
"""

    tool_instructions = """

Tool-use rules:

- Answer normal questions directly.
- Only use a tool when the user explicitly requests an action
  that requires that tool.
- For Obsidian notes, only use create_note when the user explicitly
  asks to create, make, write, add, or save a note.
- Never create an Obsidian note merely because a conversation topic
  could be useful as a note.
- When calling create_note, provide these arguments directly:
  folder, title, content.
- Never place a JSON schema inside the tool arguments.
- Never invent additional tool arguments.
- Valid Obsidian folders are:

  00 - Dashboard
  01 - Ideas
  02 - Research
  03 - Projects
  04 - Architecture
  05 - Decisions
  06 - Documentation
  07 - Canvases
"""

    return (
        identity
        + memory_context
        + tool_instructions
        + capability_boundary
    )


# ============================================================
# OLLAMA TOOL SCHEMA
# ============================================================

def build_ollama_tools(
    tool_registry: ToolRegistry,
):
    """Convert FAiL tools into Ollama's tool schema."""

    tools = []

    for tool in tool_registry.get_tool_descriptions():

        if tool["name"] == "create_note":

            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "create_note",
                        "description": (
                            "Create a Markdown note inside the "
                            "AI-Lab Obsidian vault. "
                            "Only use this when the user explicitly "
                            "asks to create, make, write, add, or save "
                            "a note."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "folder": {
                                    "type": "string",
                                    "description": (
                                        "The exact Obsidian folder. "
                                        "Must be one of: "
                                        "00 - Dashboard, "
                                        "01 - Ideas, "
                                        "02 - Research, "
                                        "03 - Projects, "
                                        "04 - Architecture, "
                                        "05 - Decisions, "
                                        "06 - Documentation, "
                                        "07 - Canvases."
                                    ),
                                },
                                "title": {
                                    "type": "string",
                                    "description": (
                                        "The title of the Markdown note."
                                    ),
                                },
                                "content": {
                                    "type": "string",
                                    "description": (
                                        "The Markdown content of the note."
                                    ),
                                },
                            },
                            "required": [
                                "folder",
                                "title",
                                "content",
                            ],
                        },
                    },
                }
            )

    return tools


# ============================================================
# MAIN
# ============================================================

def main(input_fn=None) -> None:

    if input_fn is None:
        input_fn = input

    # --------------------------------------------------------
    # LOAD IDENTITY
    # --------------------------------------------------------

    identity = load_identity()

    # --------------------------------------------------------
    # LOAD MEMORY
    # --------------------------------------------------------

    memories = load_memories()

    # --------------------------------------------------------
    # CREATE TOOL REGISTRY
    # --------------------------------------------------------

    tool_registry = ToolRegistry()

    tool_registry.register(
        create_note_tool
    )

    # --------------------------------------------------------
    # CREATE TOOL MANAGER
    # --------------------------------------------------------

    tool_manager = ToolManager(
        tool_registry
    )

    # --------------------------------------------------------
    # BUILD OLLAMA TOOL DEFINITIONS
    # --------------------------------------------------------

    ollama_tools = build_ollama_tools(
        tool_registry
    )

    # --------------------------------------------------------
    # STARTUP
    # --------------------------------------------------------

    print("FAiL is starting...")
    print("Identity loaded successfully.")
    print(
        f"Persistent memories loaded: "
        f"{len(memories)}"
    )
    print(
        f"Tools available: "
        f"{len(ollama_tools)}"
    )
    print("Type 'exit' to end the session.\n")

    # --------------------------------------------------------
    # SYSTEM MESSAGE
    # --------------------------------------------------------

    system_prompt = build_system_prompt(
        identity,
        memories,
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    # ========================================================
    # CHAT LOOP
    # ========================================================

    while True:

        user_input = input_fn("You: ").strip()

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() == "exit":

            print(
                "\nFAiL: Session ended."
            )

            break

        # ----------------------------------------------------
        # IGNORE EMPTY INPUT
        # ----------------------------------------------------

        if not user_input:
            continue

        # ----------------------------------------------------
        # ADD USER MESSAGE
        # ----------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        # ====================================================
        # DETERMINISTIC CAPABILITY CHECK
        # ====================================================

        capability_answer = handle_capability_question(
            user_input
        )

        if capability_answer is not None:

            print(
                f"\nFAiL: "
                f"{capability_answer}\n"
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": capability_answer,
                }
            )

            continue


        # ----------------------------------------------------
        # MODEL ROUTING
        # ----------------------------------------------------

        model_choice = choose_model(
            user_input
        )

        print(
            f"[FAiL using "
            f"{model_choice.model}]"
        )

        # ====================================================
        # CAPABILITY GATING
        # ====================================================

        # Only expose tools when the user has explicitly
        # requested a note.

        if looks_like_tool_request(
            user_input
        ):

            available_tools = ollama_tools

            print(
                "[FAiL tool capability: "
                "create_note enabled]"
            )

        else:

            available_tools = []

            print(
                "[FAiL tool capability: "
                "no tools enabled]"
            )

        # ====================================================
        # AGENT LOOP
        # ====================================================

        max_tool_rounds = 3

        tool_round = 0

        while tool_round < max_tool_rounds:

            tool_round += 1

            print(
                f"[FAiL agent round: "
                f"{tool_round}/"
                f"{max_tool_rounds}]"
            )

            # ------------------------------------------------
            # CALL OLLAMA
            # ------------------------------------------------

            try:

                response = chat(
                    model=model_choice.model,
                    messages=messages,
                    tools=available_tools,
                    think=False,
                )

            except Exception as error:

                print(
                    "\nFAiL encountered an error: "
                    f"{error}\n"
                )

                break

            # ------------------------------------------------
            # CHECK TOOL CALLS
            # ------------------------------------------------

            tool_calls = response.message.tool_calls

            print(
                f"[FAiL tool calls: "
                f"{tool_calls}]"
            )

            # ------------------------------------------------
            # NORMAL RESPONSE
            # ------------------------------------------------

            if not tool_calls:

                assistant_message = (
                    response.message.content
                )

                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message,
                    }
                )

                print(
                    f"\nFAiL: "
                    f"{assistant_message}\n"
                )

                break

            # ------------------------------------------------
            # PRESERVE ASSISTANT TOOL-CALL MESSAGE
            # ------------------------------------------------

            messages.append(
                response.message
            )

            # =================================================
            # EXECUTE TOOL CALLS
            # =================================================

            for tool_call in tool_calls:

                tool_name = (
                    tool_call.function.name
                )

                arguments = dict(
                    tool_call.function.arguments
                )

                print(
                    f"[FAiL executing tool: "
                    f"{tool_name}]"
                )

                print(
                    f"[FAiL arguments: "
                    f"{arguments}]"
                )

                # --------------------------------------------
                # EXECUTE THROUGH TOOL MANAGER
                # --------------------------------------------

                try:

                    result = tool_manager.run(
                        tool_name,
                        **arguments,
                    )

                    print(
                        f"[FAiL tool result: "
                        f"{result}]"
                    )

                    tool_result = str(
                        result
                    )

                except Exception as error:

                    tool_result = (
                        f"Tool '{tool_name}' failed: "
                        f"{error}"
                    )

                    print(
                        f"\n[FAiL tool error: "
                        f"{tool_result}]\n"
                    )

                # --------------------------------------------
                # RETURN OBSERVATION TO MODEL
                # --------------------------------------------

                messages.append(
                    {
                        "role": "tool",
                        "content": tool_result,
                    }
                )

                print(
                    "[FAiL observation: "
                    "tool result returned to model]"
                )

            # ------------------------------------------------
            # THINK AGAIN
            # ------------------------------------------------

            print(
                "\n[FAiL: returning observation "
                "to model...]\n"
            )

        # ====================================================
        # MAX TOOL ROUNDS
        # ====================================================

        if tool_round >= max_tool_rounds:

            # This message is only displayed when FAiL
            # actually exhausted the agent loop.

            print(
                "\n[FAiL: maximum tool rounds reached]\n"
            )

        # ====================================================
        # MEMORY SYSTEM
        # ====================================================

        if not looks_like_memory_candidate(
            user_input
        ):
            continue

        try:

            candidate = detect_memory_candidate(
                user_input
            )

            if not persist_memory_candidate(
                candidate,
                input_fn=input_fn,
            ):
                continue

            print(
                "[FAiL memory: "
                "new memory saved]\n"
            )

        except Exception as error:

            print(
                "[Memory system warning: "
                f"{error}]\n"
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
