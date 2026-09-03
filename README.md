# QA Agent Architecture

A systems design for an **AI-powered QA operating system**: seven specialised agents covering the
testing lifecycle, coordinated by an event-driven orchestrator, behind a FastAPI service.

## Read this first

This repository is **a design document plus a reference implementation**, and the two have very
different provenance. Being precise about which is which:

- **The architecture and specification are mine.**
  [`docs/QA-OS-Technical-Specification.docx`](docs/QA-OS-Technical-Specification.docx) — the agent
  decomposition, the saga/compensation model, the data schemas and the API surface — is my own
  design work.
- **The Python implementation was largely LLM-generated** from that specification in a single
  pass. It typechecks and is coherently structured, but it has **not been run against a real
  system**, and the agent prompts have not been iterated against real output.

Treat the code as a scaffold that shows the design made concrete, not as a battle-tested tool.
I removed the generated `COMPLETION_SUMMARY.md` and `PROJECT_SUMMARY.md` that shipped with it,
because they described the system as "production-ready" and "fully implemented", which it is not.

## The seven agents

| Agent | Input | Output |
|---|---|---|
| **Requirement Analyst** | Requirements doc, user story | Testable acceptance criteria, ambiguity flags |
| **Test Designer** | Acceptance criteria | Test cases with boundary and equivalence coverage |
| **Automation Engineer** | Test case | Executable Playwright script |
| **Test Runner** | Test suite | Execution results, artifacts, timings |
| **Bug Investigator** | Failure | Root-cause hypothesis, reproduction steps, severity |
| **Regression Planner** | Change set + history | Risk-ranked subset to re-run |
| **Quality Insights** | Run history | Trends, flakiness, coverage gaps |

The decomposition follows the handoffs a QA team actually makes. Each agent has one job and a
typed contract, so a weak one can be replaced — or swapped for a human — without disturbing
the rest.

## Design decisions worth defending

**Event-driven, not a pipeline.** Agents publish and subscribe rather than calling each other.
A test run finishing emits an event; the bug investigator and the insights agent both react. Adding
an eighth agent means subscribing to existing events, not editing a chain.

**Saga-based compensation.** A QA workflow is long-running and partly non-deterministic. When step
five fails, steps one through four may have created state — spun up environments, filed tickets.
Each step declares its compensating action so a failed workflow unwinds instead of leaking.

**Provider abstraction over the LLM.** `src/llm/provider.py` puts Anthropic, OpenAI and local
models behind one interface. Agents differ in how much reasoning they need; the requirement
analyst wants a strong model, the test runner barely needs one.

**Pydantic v2 as the contract layer.** `TestCase`, `TestSuite`, `BugReport` and `QualityMetrics`
are validated at every boundary, so a malformed LLM response fails at the edge with a clear
error rather than propagating.

## Layout

```
docs/            the technical specification (the primary artifact)
src/agents/      the seven agents + a shared base
src/orchestrator/ event bus, saga coordination, pipeline
src/models/      Pydantic domain models
src/llm/         provider abstraction (Anthropic / OpenAI / local)
src/api/         FastAPI routes — projects, test cases, executions, reports
config/          settings and per-agent configuration
tests/           pytest suite
scripts/         operational helpers
```

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env      # every value is UPDATE HERE; comments give the defaults
docker compose up         # brings up PostgreSQL and Redis alongside the API
```

Requires an LLM API key. The `local` provider path targets a self-hosted model if you would
rather not send requirements documents to a hosted API.

## Honest status

- Not run end-to-end against a live application.
- Agent prompts are first-draft; they have not been tuned against real outputs.
- The Kafka/event layer is implemented against the design but not load-tested.
- If you want the working, exercised version of this idea at smaller scope, see
  [ai-testcase-generator](https://github.com/MMC1410001/ai-testcase-generator) and
  [llm-prompt-evaluation-harness](https://github.com/MMC1410001/llm-prompt-evaluation-harness).

## Tech stack

Python · FastAPI · Pydantic v2 · SQLAlchemy · PostgreSQL · Redis · Kafka · Playwright ·
structlog · Docker Compose
