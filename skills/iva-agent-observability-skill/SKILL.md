---
name: iva-agent-observability-skill
description: Enterprise-grade Agent Observability, Telemetry & Tracing for IVA. Tracks execution latencies, invocation counts, tool calls, status, token consumption, and failure rates across IVA's 100 domain specialists (16 canonical families) and Antigravity agents. Provides SQLite trace persistence, streaming JSONL logs, live HTML telemetry dashboard, and CLI diagnostics.
---

# IVA Agent Observability & Telemetry Skill

Tracks, traces, and visualizes real-time performance and reliability metrics across all IVA specialists and subagents.

## Core Capabilities

1. **OpenTelemetry-Compatible Tracing**:
   - `trace_id` (UUID), `span_id`, `parent_span_id`
   - Agent classification: name, family (16 canonical families), model, action
   - Precise latency measurement (`duration_ms`), status (`SUCCESS`, `FAILED`, `RUNNING`)
   - Token & resource consumption (prompt, completion, total, cost)

2. **Storage Architecture**:
   - Primary DB: `D:\AGI_Storage\AGI_1_7\telemetry\agent_observability.db`
   - Local DB: `AI_MEDIA_STUDIO/system/agent_observability.db`
   - Streaming JSONL: `logs/agent_observability_stream.jsonl`

3. **Python Tracing API**:
   ```python
   from agent_observability import AgentSpan, observe_agent, record_tool_call

   # Context manager
   with AgentSpan(agent_name="quant-researcher", agent_family="Mathematics & Symbolic Reasoning") as span:
       span.set_tokens(prompt=500, completion=200)
       span.set_output("Backtest passed with 0 errors")

   # Function decorator
   @observe_agent(agent_name="ast-auditor", family="Testing, QA & Verification")
   def audit_code(target_file):
       ...
   ```

4. **Live Telemetry Dashboard**:
   - Modern dark UI with real-time stats cards, 16-family health matrix, agent leaderboard, token expenditure graph, and live trace stream.
   - Generated via: `iva studios observability --dashboard`

## CLI Commands

```powershell
# Display high-level telemetry summary
iva studios observability --summary

# Inspect recent execution trace timeline
iva studios observability --traces --limit 25

# Generate & view live HTML dashboard
iva studios observability --dashboard

# Run synthetic verification trace emission
iva studios observability --test
```
