# Specification: hello-world-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md` and `intent.md`)
- [x] Bootstrap agent code in `assets/hello-world-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/hello-world-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skills are required for this agent — the greeting and response logic is simple enough to express entirely in the system prompt. No multi-step workflows, domain-specific rules, or reference material are needed.

---

## Project-Specific Tasks

### REQ-01 & REQ-02: Greeting and Basic Conversation

- [x] Write the system prompt in `app/agent.py` `@prompt_section` to instruct the agent to:
  - Greet the user warmly when they send their first message, introducing itself as the Hello World Agent
  - Respond helpfully and concisely to any follow-up message
  - Keep responses short and friendly — this is a demo agent, not an assistant with deep domain knowledge
- [x] Confirm the agent returns a greeting response when given any opening message (manual smoke test via `python -m app.main`)

### REQ-03: No External Integrations

- [x] Confirm `asset.yaml` has an empty `requires` list (no MCP servers)
- [x] Confirm `app/agent.py` does NOT import or reference any MCP tool loading (`get_mcp_tools` call should return an empty list)
- [x] Confirm no `api-specs/` or `mcp-specs/` directories exist under this asset

---

## Business Instrumentation

- [x] Implement business step instrumentation for all 5 milestones from the PRD using structured logging (pattern: `[MILESTONE_ID].[achieved|missed]: [description]`) and OpenTelemetry spans:
  - M1: Agent scaffold ready
  - M2: Greeting response delivered
  - M3: Conversation loop completed
  - M4: Tests passed
  - M5: Agent deployed and reachable
- [x] Extract business logic from `stream()` into a plain async helper method `_run_agent()` to avoid `GeneratorExit` span context errors
- [x] Verify `auto_instrument()` is called at the top of `main.py` before any AI framework imports

---

## MCP Tool Integration

This agent has zero SAP API touchpoints — skip all MCP integration tasks.

- [x] Confirm no MCP wiring is present in `app/agent.py`
- [x] Skip `mcp-translation-file`, `setup-solution` MCP asset creation, and `mcp-mock-config` (no MCP servers, no mock needed)

---

## Testing

- [x] Install test dependencies: `pip install -r requirements-test.txt` (from `assets/hello-world-agent/`)
- [x] Write unit tests in `assets/hello-world-agent/tests/`:
  - `test_agent.py` — test that the agent returns a greeting string and a follow-up response; mock the LLM to return canned responses
- [x] Write one integration test in `assets/hello-world-agent/tests/test_integration.py`:
  - Call the agent's `invoke` function with a greeting message; assert a non-empty response is returned; mock LLM and all external systems
- [x] Run `pytest` from `assets/hello-world-agent/` (no args) — fix any failures before proceeding
- [x] Verify `assets/hello-world-agent/app/agent.py` has exactly 9 decorated functions (run `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/hello-world-agent/app/agent.py` — must return 9)
- [x] Run `pytest` again from `assets/hello-world-agent/` (no args) to produce final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/hello-world-agent/`
