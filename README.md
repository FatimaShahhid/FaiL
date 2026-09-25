# FAiL

FAiL is a local agentic AI framework built around personal memory, model routing, tools, and knowledge.

FAiL is intentionally being developed as a living work-in-progress rather than a finished product.

## What exists today

- Local Ollama model execution
- Simple model routing
- Identity loading
- Consent-controlled persistent memory
- Deterministic capability awareness
- Tool registry and tool validation
- Obsidian note creation
- Automated tests

## Current boundaries

FAiL does **not** currently implement:

- Reading, searching, or listing existing Obsidian notes
- RBAC
- Audit logging
- Knowledge graphs
- Autonomous planning or background execution
- Memory retrieval, ranking, or deduplication
- A general policy engine

The authoritative source of FAiL's implemented capabilities is:

`fail/core/architecture.py`

FAiL should never claim a capability that is not actually implemented.

## Models

The current local development setup uses Ollama with:

- `llama3.2:1b`
- `qwen3:1.7b`

## Obsidian

FAiL's Obsidian integration uses the `FAIL_OBSIDIAN_VAULT` environment variable to locate the user's vault.

Example:

```powershell
$env:FAIL_OBSIDIAN_VAULT="C:\Path\To\Your\Obsidian\Vault"
