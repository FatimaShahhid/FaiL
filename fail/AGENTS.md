# FAiL Engineering Rules

## Project authority

- The file `fail/core/architecture.py` is the authoritative source of truth for FAiL's currently implemented capabilities.
- The model must never invent capabilities, integrations, tools, commands, APIs, services, or implementation details that are not actually implemented.
- Aspirational Obsidian documentation is not authoritative when it conflicts with the codebase.
- Do not treat planned functionality as implemented functionality.

## Architectural boundaries

- Preserve the existing FAiL architecture unless the user explicitly asks for an architectural change.
- Do not redesign working subsystems merely because a different design appears preferable.
- Do not modify the memory system unless the user explicitly requests a memory-system change.
- Do not change the semantics of explicit human memory consent.
- Do not remove or alter existing safety boundaries without explicit instruction.

## Development workflow

For non-trivial tasks:

1. Inspect the relevant code and tests first.
2. Identify the root cause or exact requirement.
3. Describe the proposed change before implementing it.
4. Make the smallest safe change necessary.
5. Run the affected tests.
6. Run the full relevant FAiL test suite.
7. Report exactly what changed, why it changed, and the test results.

For simple tasks, direct implementation is acceptable when the change is clearly localized.

## Change discipline

- Do not rewrite entire files when a localized change is sufficient.
- Do not delete working code without explicit justification.
- Do not create duplicate implementations of existing functionality.
- Do not modify backup/archive files unless explicitly asked.
- Do not silently "clean up" unrelated code while implementing a requested change.
- Do not change documentation merely to make the implementation appear more complete.

## Testing

The primary FAiL test command is:

.\.venv\Scripts\python.exe -m unittest discover -s fail -p "test_*.py" -v

A passing baseline must be preserved unless the requested change intentionally changes behavior.

## Current known boundaries

The following are currently not implemented unless the authoritative architecture says otherwise:

- Reading/searching/listing existing Obsidian notes
- RBAC
- Audit logging
- Knowledge graphs
- Autonomous planning/background execution
- Memory retrieval/ranking/search/deduplication
- General policy enforcement

Do not implement any of these merely because they appear useful.

## Agent behavior

- Prefer verification over assumptions.
- When a finding is uncertain, inspect the current file and verify it.
- Do not claim a function is dead, unreachable, unused, or obsolete without checking its current call sites.
- Treat tests as evidence, not as the sole definition of architecture.
- Before making changes, distinguish between:
  - confirmed implementation issue
  - documentation issue
  - cleanup
  - intentional/stale artifact
  - false finding

## FAiL scope

The `fail/` directory is the active FAiL implementation.

The following should be treated as archival unless explicitly requested:

- `fail/main_before_tool_call.py`

Do not modify archival files during normal FAiL development.
