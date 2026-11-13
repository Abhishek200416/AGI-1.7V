import os
import sys
import pytest

# Add paths
sys.path.insert(0, r"C:\Users\abhis\Projects\IVA\studio\system")
sys.path.insert(0, r"C:\Users\abhis\Projects\IVA\iva")

import agent_observability as obs

def test_agent_span_lifecycle():
    with obs.AgentSpan(
        agent_name="test-observability-agent",
        agent_family="Software Engineering",
        action="unit_test_verification",
        model_name="gemini-3.8-flash"
    ) as span:
        span.set_tokens(prompt=120, completion=45, cost=0.0001)
        span.set_output("Verification passed cleanly")
        span.set_metadata("test_key", "test_value")

    assert span.status == "SUCCESS"
    assert span.duration_ms > 0
    assert span.total_tokens == 165

def test_agent_summary_and_metrics():
    summary = obs.get_agent_summary()
    assert "totals" in summary
    assert "agents" in summary
    assert "families" in summary
    assert summary["totals"]["total_spans"] >= 1

def test_recent_traces_retrieval():
    traces = obs.get_recent_traces(limit=5)
    assert isinstance(traces, list)
    assert len(traces) >= 1
    assert "agent_name" in traces[0]

def test_dashboard_html_generation(tmp_path):
    dash_file = tmp_path / "test_dashboard.html"
    out = obs.generate_dashboard_html(str(dash_file))
    assert os.path.exists(out)
    with open(out, "r", encoding="utf-8") as f:
        content = f.read()
    assert "IVA Agent Observability Hub" in content
    assert "16 Families Monitored" in content
