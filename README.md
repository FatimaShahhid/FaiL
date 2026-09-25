# FAiL

FAiL is a local agentic AI framework built around personal memory, model routing, tools, and knowledge.

FAiL is intentionally being developed as a living work-in-progress rather than a finished product.

## What exists today

* Local Ollama model execution
* Simple model routing
* Identity loading
* Consent-controlled persistent memory
* Deterministic capability awareness
* Tool registry and tool validation
* Tool execution
* Obsidian note creation
* Automated tests

## Current boundaries

FAiL does **not** currently implement:

* Reading, searching, or listing existing Obsidian notes
* Editing existing Obsidian notes
* RBAC
* Audit logging
* Knowledge graphs
* Autonomous planning or background execution
* Memory retrieval, ranking, or deduplication
* A general policy engine

The authoritative source of FAiL's implemented capabilities is:

`fail/core/architecture.py`

FAiL should never claim a capability that is not actually implemented.

## Architecture

FAiL separates model reasoning from deterministic system capabilities.

```text
User
  |
  v
FAiL Agent
  |
  +-- Identity
  |
  +-- Model Router
  |
  +-- Capability Awareness
  |
  +-- Memory
  |
  +-- Tools
        |
        +-- Obsidian Integration
```

The language model does not define what FAiL can actually do. Implemented capabilities are defined by the architecture and available tools.

## Memory

FAiL includes a persistent memory system based on explicit human consent.

The current memory flow is:

```text
User information
      |
      v
Memory detection
      |
      v
Policy eligibility
      |
      v
Explicit human consent
      |
      v
Normalization
      |
      v
Persistent storage
```

Information is not persisted simply because the model considers it useful.

Advanced memory retrieval, ranking, embeddings, deduplication, and autonomous memory management are not currently implemented.

## Models

The current local development setup uses Ollama with:

* `llama3.2:1b`
* `qwen3:1.7b`
* `qwen3:4b`

Model routing selects an appropriate local model based on the request.

## Tools

FAiL uses a tool registry and tool manager to control tool execution.

Each tool has:

* A name
* A description
* Parameters
* An executable function

Tool requests are validated before execution.

```text
Model
  |
  v
Tool request
  |
  v
Tool validation
  |
  v
Tool execution
```

## Obsidian

FAiL currently integrates with an Obsidian vault for note creation.

The vault location can be configured using the `FAIL_OBSIDIAN_VAULT` environment variable.

Example:

```powershell
$env:FAIL_OBSIDIAN_VAULT="C:\Path\To\Your\Obsidian\Vault"
```

The current Obsidian integration supports creating Markdown notes.

Reading, searching, listing, and editing existing Obsidian notes are not currently implemented.

## Project structure

```text
fail/
├── agents/
├── core/
│   ├── architecture.py
│   ├── identity_loader.py
│   ├── memory.py
│   ├── memory_candidate.py
│   ├── memory_consent.py
│   ├── memory_detector.py
│   ├── memory_manager.py
│   ├── memory_policy.py
│   └── model_router.py
│
├── integrations/
│   └── obsidian.py
│
├── memory/
│   ├── identity/
│   └── persistent/
│
├── tools/
│   ├── manager.py
│   ├── obsidian_tools.py
│   ├── registry.py
│   └── tool.py
│
├── AGENTS.md
├── main.py
└── test_*.py
```

## Testing

Run the FAiL test suite with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s fail -p "test_*.py" -v
```

## Development status

FAiL is under active development.

The project is being built incrementally, with working capabilities tested and verified before new architectural layers are added.

Future development may include:

* Obsidian retrieval and search
* Knowledge retrieval
* Knowledge graphs
* More advanced tool use
* Multi-step planning
* Verification and recovery
* Controlled background execution
* Security and access controls
* Audit logging

These are future development areas, not currently implemented capabilities.

## License

MIT

See the `LICENSE` file for the full license text.
