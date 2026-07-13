# Support Triage Agent

An LLM-powered agent that triages incoming customer-support tickets for a
payments company. It classifies each ticket, pulls customer context, and
either drafts a response or escalates to a human — based on explicit,
testable rules.

## What it does

For each ticket the agent:
1. **Classifies** it into one category (payment inquiry, dispute,
   technical issue, suspected fraud, or out-of-scope) with a confidence score.
2. **Retrieves customer context** via a tool call.
3. **Decides** whether to escalate or respond, using deterministic
   escalation rules.

Escalation is triggered by: a fraud signal, a flagged account, a financial
dispute, or low model confidence — checked in that order of precedence.

## Design decisions

**Provider-swappable LLM layer.** All model access is isolated in `llm.py`.
Switching providers (Gemini → Groq/Llama, etc.) touches one file; the agent
and tools are untouched. This project was migrated between providers by
editing `llm.py` alone.

**Logic separated from the model.** Escalation rules live in a pure function
(`_escalation_decision`) with no LLM dependency, so they can be unit-tested
deterministically. Model-quality questions are handled separately (see the
evaluation harness — companion project).

**Structured output by design.** Every step returns a structured trace
(category, confidence, tools called, escalation reason) so downstream
evaluation can consume it directly.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install groq python-dotenv pytest
```

Create a `.env` file (never commit this):
```

GROQ_API_KEY=your_key_here
```
## Run

```bash
python main.py
```

## Test

```bash
pytest test_agent.py -v
```

Unit tests cover the escalation logic in isolation — no network or API key
required, since the model layer is never invoked.

## Project structure

| File            | Responsibility                                  |
|-----------------|-------------------------------------------------|
| `llm.py`        | Provider-swappable LLM client                   |
| `tools.py`      | Agent tools (customer lookup, escalation, etc.) |
| `agent.py`      | Orchestration + escalation logic                |
| `test_agent.py` | Unit tests for escalation rules                 |
| `main.py`       | Demo runner over sample tickets                 |
