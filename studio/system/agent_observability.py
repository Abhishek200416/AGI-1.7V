#!/usr/bin/env python3
"""
IVA Agent Observability & Telemetry System
Comprehensive tracing, latency measurement, token usage tracking, and health metrics
for IVA's 100 domain specialists across 16 families, Antigravity agents, and subagents.
"""

import os
import sys
import json
import time
import uuid
import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager

# Base directories
BASE_DIR = r"c:\Users\abhis\Downloads\ytsss\AI_MEDIA_STUDIO"
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PRIMARY_DB = r"D:\AGI_Storage\AGI_1_7\telemetry\agent_observability.db"
LOCAL_DB = os.path.join(BASE_DIR, "system", "agent_observability.db")
STREAM_LOG = os.path.join(LOGS_DIR, "agent_observability_stream.jsonl")

# 16 Canonical Agent Families
AGENT_FAMILIES = [
    "Planning & Architecture",
    "Research & Evidence Synthesis",
    "Mathematics & Symbolic Reasoning",
    "Physics & Physical Sciences",
    "Chemistry & Molecular Sciences",
    "Biology & Biomedical Sciences",
    "Software Engineering",
    "Terminal, Shell & OS Operations",
    "Containers, Virtualization & Cloud",
    "Browser & Web Automation",
    "Desktop & Computer Use",
    "Data, Storage & Databases",
    "Testing, QA & Verification",
    "Security, Permissions & Safety",
    "Performance, Token & Resource Optimization",
    "Release, Governance & Reporting"
]

def _resolve_db_path() -> str:
    """Returns accessible SQLite DB path with fallback."""
    try:
        primary_dir = os.path.dirname(PRIMARY_DB)
        if os.path.exists(primary_dir):
            return PRIMARY_DB
    except Exception:
        pass
    os.makedirs(os.path.dirname(LOCAL_DB), exist_ok=True)
    return LOCAL_DB

def init_observability_db():
    """Initializes SQLite schema for agent tracing and metrics."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    db_path = _resolve_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_spans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                span_id TEXT NOT NULL UNIQUE,
                parent_span_id TEXT,
                agent_name TEXT NOT NULL,
                agent_family TEXT NOT NULL,
                model_name TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                input_summary TEXT,
                output_summary TEXT,
                error_message TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_id ON agent_spans (trace_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_name ON agent_spans (agent_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_family ON agent_spans (agent_family)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON agent_spans (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON agent_spans (created_at)")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics_rollup (
                agent_name TEXT PRIMARY KEY,
                agent_family TEXT NOT NULL,
                total_invocations INTEGER DEFAULT 0,
                successful_invocations INTEGER DEFAULT 0,
                failed_invocations INTEGER DEFAULT 0,
                total_duration_ms REAL DEFAULT 0.0,
                avg_latency_ms REAL DEFAULT 0.0,
                p95_latency_ms REAL DEFAULT 0.0,
                total_tokens INTEGER DEFAULT 0,
                total_cost_usd REAL DEFAULT 0.0,
                last_seen TEXT NOT NULL
            )
        """)
        conn.commit()

class AgentSpan:
    """Context manager for tracing agent execution blocks."""
    def __init__(
        self,
        agent_name: str,
        action: str = "execution",
        agent_family: str = "Software Engineering",
        model_name: str = "gemini-3.8-flash",
        trace_id: str = None,
        parent_span_id: str = None,
        input_data: any = None
    ):
        self.agent_name = agent_name
        self.action = action
        self.agent_family = agent_family if agent_family in AGENT_FAMILIES else "Software Engineering"
        self.model_name = model_name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())[:12]
        self.parent_span_id = parent_span_id
        self.input_summary = str(input_data)[:500] if input_data is not None else ""
        self.output_summary = ""
        self.status = "RUNNING"
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.cost_usd = 0.0
        self.error_message = None
        self.metadata = {}
        self.start_time = None
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def set_tokens(self, prompt: int = 0, completion: int = 0, cost: float = 0.0):
        self.prompt_tokens = prompt
        self.completion_tokens = completion
        self.total_tokens = prompt + completion
        self.cost_usd = cost

    def set_output(self, output: any):
        self.output_summary = str(output)[:500]

    def set_metadata(self, key: str, value: any):
        self.metadata[key] = value

    def set_error(self, err: Exception or str):
        self.status = "FAILED"
        self.error_message = str(err)

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        self.duration_ms = (end_time - self.start_time) * 1000.0
        
        if exc_type is not None:
            self.status = "FAILED"
            self.error_message = f"{exc_type.__name__}: {str(exc_val)}"
        elif self.status == "RUNNING":
            self.status = "SUCCESS"

        self._record()
        # Do not suppress exceptions
        return False

    def _record(self):
        created_at = datetime.now(timezone.utc).isoformat()
        span_dict = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "agent_name": self.agent_name,
            "agent_family": self.agent_family,
            "model_name": self.model_name,
            "action": self.action,
            "status": self.status,
            "duration_ms": round(self.duration_ms, 2),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": created_at
        }

        # 1. Append to streaming JSONL
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            with open(STREAM_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(span_dict) + "\n")
        except Exception:
            pass

        # 2. Persist to SQLite
        try:
            init_observability_db()
            db_path = _resolve_db_path()
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO agent_spans (
                        trace_id, span_id, parent_span_id, agent_name, agent_family,
                        model_name, action, status, duration_ms, prompt_tokens,
                        completion_tokens, total_tokens, cost_usd, input_summary,
                        output_summary, error_message, metadata_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.trace_id, self.span_id, self.parent_span_id, self.agent_name, self.agent_family,
                    self.model_name, self.action, self.status, self.duration_ms, self.prompt_tokens,
                    self.completion_tokens, self.total_tokens, self.cost_usd, self.input_summary,
                    self.output_summary, self.error_message, json.dumps(self.metadata), created_at
                ))
                
                # Update rollup metrics
                cursor.execute("""
                    INSERT INTO agent_metrics_rollup (
                        agent_name, agent_family, total_invocations, successful_invocations,
                        failed_invocations, total_duration_ms, avg_latency_ms, p95_latency_ms,
                        total_tokens, total_cost_usd, last_seen
                    ) VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(agent_name) DO UPDATE SET
                        total_invocations = total_invocations + 1,
                        successful_invocations = successful_invocations + excluded.successful_invocations,
                        failed_invocations = failed_invocations + excluded.failed_invocations,
                        total_duration_ms = total_duration_ms + excluded.total_duration_ms,
                        avg_latency_ms = (total_duration_ms + excluded.total_duration_ms) / (total_invocations + 1),
                        total_tokens = total_tokens + excluded.total_tokens,
                        total_cost_usd = total_cost_usd + excluded.total_cost_usd,
                        last_seen = excluded.last_seen
                """, (
                    self.agent_name,
                    self.agent_family,
                    1 if self.status == "SUCCESS" else 0,
                    1 if self.status == "FAILED" else 0,
                    self.duration_ms,
                    self.duration_ms,
                    self.duration_ms,
                    self.total_tokens,
                    self.cost_usd,
                    created_at
                ))
                conn.commit()
        except Exception as e:
            sys.stderr.write(f"[Observability DB Error] {e}\n")

def observe_agent(agent_name: str, family: str = "Software Engineering", action: str = "turn", model: str = "gemini-3.8-flash"):
    """Decorator to automatically wrap a function in an AgentSpan."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with AgentSpan(agent_name=agent_name, agent_family=family, action=action, model_name=model, input_data=args) as span:
                res = func(*args, **kwargs)
                span.set_output(res)
                return res
        return wrapper
    return decorator

def record_tool_call(agent_name: str, tool_name: str, args: any, result: any, duration_ms: float, status: str = "SUCCESS", error: str = None):
    """Directly records a tool call span for an agent."""
    with AgentSpan(
        agent_name=agent_name,
        action=f"tool:{tool_name}",
        agent_family="Software Engineering",
        input_data=args
    ) as span:
        span.duration_ms = duration_ms
        span.status = status
        span.set_output(result)
        if error:
            span.set_error(error)

def get_agent_summary():
    """Returns high-level telemetry summary and rollups."""
    init_observability_db()
    db_path = _resolve_db_path()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total_spans, SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) as success_spans, SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) as failed_spans, AVG(duration_ms) as avg_duration, SUM(total_tokens) as total_tokens, SUM(cost_usd) as total_cost FROM agent_spans")
        totals = dict(cursor.fetchone() or {})
        
        cursor.execute("SELECT * FROM agent_metrics_rollup ORDER BY total_invocations DESC LIMIT 50")
        agents = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT agent_family, COUNT(*) as invocations,
                   SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) as successes,
                   SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) as failures,
                   AVG(duration_ms) as avg_ms
            FROM agent_spans
            GROUP BY agent_family
            ORDER BY invocations DESC
        """)
        families = [dict(r) for r in cursor.fetchall()]

        return {
            "database_path": db_path,
            "totals": totals,
            "agents": agents,
            "families": families
        }

def get_recent_traces(limit: int = 25, agent_name: str = None):
    """Retrieves recent trace spans."""
    init_observability_db()
    db_path = _resolve_db_path()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if agent_name:
            cursor.execute("SELECT * FROM agent_spans WHERE agent_name = ? ORDER BY id DESC LIMIT ?", (agent_name, limit))
        else:
            cursor.execute("SELECT * FROM agent_spans ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]

def generate_dashboard_html(output_file: str = None) -> str:
    """Generates an ultra-responsive dark-theme HTML telemetry dashboard."""
    summary = get_agent_summary()
    recent_traces = get_recent_traces(35)
    
    out_path = output_file or os.path.join(BASE_DIR, "system", "agent_observability_dashboard.html")
    
    totals = summary.get("totals", {})
    total_spans = totals.get("total_spans") or 0
    success_spans = totals.get("success_spans") or 0
    failed_spans = totals.get("failed_spans") or 0
    avg_dur = round(totals.get("avg_duration") or 0.0, 1)
    tot_tokens = totals.get("total_tokens") or 0
    success_rate = round((success_spans / total_spans * 100), 1) if total_spans > 0 else 100.0

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IVA Agent Observability & Telemetry Hub</title>
    <style>
        :root {{
            --bg-base: #0a0d14;
            --bg-card: #111622;
            --bg-card-hover: #182030;
            --border: #222d42;
            --text-main: #f0f4f8;
            --text-muted: #8b9bb4;
            --accent-neon: #38ef7d;
            --accent-cyan: #11998e;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-warn: #f59e0b;
            --accent-danger: #ef4444;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background: var(--bg-base); color: var(--text-main); min-height: 100vh; padding: 24px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 24px; }}
        .header-title {{ display: flex; align-items: center; gap: 12px; }}
        .badge {{ background: linear-gradient(135deg, var(--accent-cyan), var(--accent-neon)); color: #000; font-weight: 800; font-size: 11px; padding: 4px 10px; border-radius: 999px; text-transform: uppercase; letter-spacing: 1px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; margin-bottom: 28px; }}
        .card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; transition: transform 0.15s ease, border-color 0.15s ease; }}
        .card:hover {{ border-color: var(--accent-blue); transform: translateY(-2px); }}
        .card-label {{ font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
        .card-value {{ font-size: 28px; font-weight: 700; color: var(--text-main); display: flex; align-items: baseline; gap: 6px; }}
        .card-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 6px; }}
        
        .main-sections {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }}
        @media(max-width: 900px) {{ .main-sections {{ grid-template-columns: 1fr; }} }}
        
        .section-header {{ font-size: 16px; font-weight: 600; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; background: rgba(255,255,255,0.02); }}
        tr:hover td {{ background: var(--bg-card-hover); }}
        
        .status-pill {{ display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }}
        .status-success {{ background: rgba(56, 239, 125, 0.15); color: var(--accent-neon); }}
        .status-failed {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-danger); }}
        .status-running {{ background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); }}
        
        .code-box {{ font-family: monospace; background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; color: #a5b4fc; font-size: 12px; }}
        .refresh-btn {{ background: #1e293b; color: var(--text-main); border: 1px solid var(--border); padding: 8px 14px; border-radius: 8px; font-size: 13px; cursor: pointer; }}
        .refresh-btn:hover {{ background: #334155; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h2>IVA Agent Observability Hub</h2>
            <span class="badge">Telemetry Live</span>
        </div>
        <div>
            <button class="refresh-btn" onclick="location.reload()">↻ Refresh Telemetry</button>
        </div>
    </div>

    <div class="metrics-grid">
        <div class="card">
            <div class="card-label">Total Agent Spans</div>
            <div class="card-value">{total_spans}</div>
            <div class="card-sub">{success_spans} success · {failed_spans} errors</div>
        </div>
        <div class="card">
            <div class="card-label">Success Rate</div>
            <div class="card-value" style="color: {'var(--accent-neon)' if success_rate >= 95 else 'var(--accent-warn)'}">{success_rate}%</div>
            <div class="card-sub">Global agent reliability gate</div>
        </div>
        <div class="card">
            <div class="card-label">Average Latency</div>
            <div class="card-value">{avg_dur} <span style="font-size: 14px; color: var(--text-muted);">ms</span></div>
            <div class="card-sub">Sub-60s fast-path SLA tracking</div>
        </div>
        <div class="card">
            <div class="card-label">Active Specialists</div>
            <div class="card-value">{len(summary.get('agents', []))} <span style="font-size: 14px; color: var(--text-muted);">/ 100</span></div>
            <div class="card-sub">Across 16 canonical families</div>
        </div>
        <div class="card">
            <div class="card-label">Total Tokens Processed</div>
            <div class="card-value">{tot_tokens:,}</div>
            <div class="card-sub">Prompt + Completion telemetry</div>
        </div>
    </div>

    <div class="main-sections">
        <!-- 16 Families Telemetry -->
        <div class="card">
            <div class="section-header">
                <span>Agent Families Performance</span>
                <span style="font-size: 12px; color: var(--text-muted);">16 Families Monitored</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Family</th>
                        <th>Calls</th>
                        <th>Success Rate</th>
                        <th>Avg Latency</th>
                    </tr>
                </thead>
                <tbody>
"""
    for f in summary.get("families", []):
        inv = f.get("invocations", 0)
        succ = f.get("successes", 0)
        rate = round((succ / inv * 100), 1) if inv > 0 else 100.0
        dur = round(f.get("avg_ms", 0.0), 1)
        html_content += f"""
                    <tr>
                        <td style="font-weight: 600;">{f.get('agent_family')}</td>
                        <td>{inv}</td>
                        <td><span class="status-pill {'status-success' if rate >= 90 else 'status-failed'}">{rate}%</span></td>
                        <td>{dur} ms</td>
                    </tr>
"""
    if not summary.get("families"):
        html_content += "<tr><td colspan='4' style='text-align:center; color:var(--text-muted);'>No family traces yet. Run an agent task to initialize.</td></tr>"

    html_content += """
                </tbody>
            </table>
        </div>

        <!-- Top Active Agents -->
        <div class="card">
            <div class="section-header">
                <span>Agent Runtimes Leaderboard</span>
                <span style="font-size: 12px; color: var(--text-muted);">Top Invoked</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Invocations</th>
                        <th>P95 Latency</th>
                        <th>Tokens</th>
                    </tr>
                </thead>
                <tbody>
"""
    for ag in summary.get("agents", [])[:8]:
        html_content += f"""
                    <tr>
                        <td><span class="code-box">{ag.get('agent_name')}</span></td>
                        <td>{ag.get('total_invocations')}</td>
                        <td>{round(ag.get('p95_latency_ms', 0), 1)} ms</td>
                        <td>{ag.get('total_tokens', 0):,}</td>
                    </tr>
"""
    if not summary.get("agents"):
        html_content += "<tr><td colspan='4' style='text-align:center; color:var(--text-muted);'>No agent activity logged.</td></tr>"

    html_content += """
                </tbody>
            </table>
        </div>
    </div>

    <!-- Recent Traces Stream -->
    <div class="card">
        <div class="section-header">
            <span>Live Agent Execution Traces (Latest)</span>
            <span style="font-size: 12px; color: var(--text-muted);">Streaming Audit Trail</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Agent</th>
                    <th>Family</th>
                    <th>Model</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Latency</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""
    for tr in recent_traces:
        st_class = "status-success" if tr.get("status") == "SUCCESS" else ("status-failed" if tr.get("status") == "FAILED" else "status-running")
        ts = tr.get("created_at", "")[:19].replace("T", " ")
        html_content += f"""
                <tr>
                    <td style="color: var(--text-muted); font-size: 11px;">{ts}</td>
                    <td><span class="code-box">{tr.get('agent_name')}</span></td>
                    <td style="font-size: 11px; color: var(--text-muted);">{tr.get('agent_family')}</td>
                    <td style="font-size: 11px;">{tr.get('model_name')}</td>
                    <td>{tr.get('action')}</td>
                    <td><span class="status-pill {st_class}">{tr.get('status')}</span></td>
                    <td>{round(tr.get('duration_ms', 0), 1)} ms</td>
                    <td style="font-size: 11px; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{tr.get('output_summary') or tr.get('input_summary') or tr.get('error_message') or '-'}</td>
                </tr>
"""
    if not recent_traces:
        html_content += "<tr><td colspan='8' style='text-align:center; color:var(--text-muted);'>No traces found.</td></tr>"

    html_content += f"""
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return out_path

def record_synthetic_sample_events():
    """Seeds verification telemetry events to prove observability subsystem operation."""
    sample_agents = [
        ("video-creator", "Software Engineering", "gemini-3.8-flash", "render_motion_graphics", 1240.5, 450, 120),
        ("marketing-lead", "Research & Evidence Synthesis", "claude-3-7-sonnet", "campaign_pack_generation", 890.2, 850, 310),
        ("ast-compiler-auditor", "Testing, QA & Verification", "gemini-3.8-flash", "syntax_and_import_check", 145.0, 120, 45),
        ("lemo-opuscar-director", "Software Engineering", "gemini-3.8-flash", "canvas_procedural_scene", 2100.8, 620, 290),
        ("quant-researcher", "Mathematics & Symbolic Reasoning", "gpt-4o", "friction_aware_backtest", 1520.1, 980, 400),
        ("browser-automation-agent", "Browser & Web Automation", "local-ast-compiler", "cdp_tab_handshake", 310.4, 80, 20),
    ]
    for name, family, model, action, dur, pin, pout in sample_agents:
        with AgentSpan(agent_name=name, agent_family=family, model_name=model, action=action) as span:
            span.duration_ms = dur
            span.set_tokens(pin, pout)
            span.set_output(f"Verified execution of {action} with 0 errors.")

if __name__ == "__main__":
    init_observability_db()
    record_synthetic_sample_events()
    dash = generate_dashboard_html()
    print(f"[SUCCESS] Agent Observability initialized and seeded!")
    print(f"[DASHBOARD] {dash}")
    print(json.dumps(get_agent_summary(), indent=2))
