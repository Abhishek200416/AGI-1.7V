#!/usr/bin/env python3
"""
IVA Studios <-> IVA Video Skill Codebase-to-Motion Video Generator
Inspects any local codebase repository (module tree, key Python/JS/TS files, LOC stats)
and generates a self-contained IVA Video Skill 1080x1920 procedural Canvas showcase film
(`.html`) + voiceover script demonstrating the app, where to find it, and how to use it.
"""

import html
import json
import os
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".osworld_venv", "dist", "build"}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".rs", ".go"}


def analyze_codebase(repo_dir: str, max_files: int = 8) -> dict:
    """Collect real module names, file counts, and LOC metrics from a repository."""
    root = Path(repo_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_dir}")

    files = []
    total_loc = 0
    for cur_root, dirs, names in os.walk(root):
        dirs[:] = [d for d in sorted(dirs) if d not in SKIP_DIRS]
        for name in sorted(names):
            p = Path(cur_root) / name
            if p.suffix.lower() in CODE_EXTS:
                try:
                    lines = len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
                except Exception:
                    lines = 0
                total_loc += lines
                files.append({"path": str(p.relative_to(root)).replace("\\", "/"), "loc": lines})

    top_files = sorted(files, key=lambda x: x["loc"], reverse=True)[:max_files]
    return {
        "repo_name": root.name,
        "total_code_files": len(files),
        "total_loc": total_loc,
        "top_modules": top_files,
    }


def build_codebase_motion_html(
    repo_dir: str,
    out_html: str,
    app_url: str = "",
    how_to_use: str = "",
    duration_s: float = 42.0,
) -> dict:
    """Generate an IVA Video Skill 1080x1920 procedural motion HTML canvas showcasing a codebase."""
    summary = analyze_codebase(repo_dir)
    repo_name = summary["repo_name"]
    total_files = summary["total_code_files"]
    total_loc = summary["total_loc"]
    mods_json = json.dumps(summary["top_modules"])
    url_label = html.escape(app_url or f"github.com/Abhishek200416/{repo_name}")
    usage_label = html.escape(how_to_use or "python setup_iva.py && python run_iva.py")

    script_text = (
        f"Look inside {repo_name}: {total_files} real code modules and {total_loc:,} lines working autonomously. "
        f"From core engine architecture to automated tests, every component executes as one pipeline. "
        f"Find it at {url_label}, run {usage_label}, and watch it ship."
    )

    canvas_html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:#050811;overflow:hidden}}
canvas{{display:block;width:1080px;height:1920px}}
</style></head>
<body>
<canvas id="c" width="1080" height="1920"></canvas>
<script>
const W=1080, H=1920, DUR={duration_s:.2f};
const REPO={json.dumps(repo_name)};
const MODS={mods_json};
const FILES={total_files}, LOC={total_loc};
const URL_LBL={json.dumps(url_label)};
const USAGE_LBL={json.dumps(usage_label)};
const ctx=document.getElementById('c').getContext('2d');

function wrapText(text, x, y, maxW, lh) {{
  const words = text.split(' ');
  let line = '';
  for (let i = 0; i < words.length; i++) {{
    const test = line + words[i] + ' ';
    if (ctx.measureText(test).width > maxW && i > 0) {{
      ctx.fillText(line.trim(), x, y);
      line = words[i] + ' ';
      y += lh;
    }} else {{
      line = test;
    }}
  }}
  ctx.fillText(line.trim(), x, y);
}}

window.render = function(t) {{
  const p = Math.min(1, Math.max(0, t / DUR));
  ctx.fillStyle = '#050811';
  ctx.fillRect(0, 0, W, H);

  // Dynamic neon grid & telemetry pulse
  ctx.strokeStyle = 'rgba(0, 240, 255, 0.08)';
  ctx.lineWidth = 2;
  const shift = (t * 40) % 90;
  for (let gx = 0; gx < W; gx += 90) {{ ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke(); }}
  for (let gy = shift; gy < H; gy += 90) {{ ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke(); }}

  // Header badge
  ctx.fillStyle = '#00f0ff';
  ctx.font = 'bold 34px Consolas, monospace';
  ctx.fillText('IVA VIDEO SKILL // CODEBASE IN MOTION', 70, 140);
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 74px Arial, sans-serif';
  ctx.fillText(REPO.toUpperCase(), 70, 235);

  // Real metrics counter animation
  const animFiles = Math.round(FILES * Math.min(1, t / 4.0));
  const animLoc = Math.round(LOC * Math.min(1, t / 5.0));
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.fillRect(70, 290, W - 140, 190);
  ctx.strokeStyle = '#38bdf8';
  ctx.strokeRect(70, 290, W - 140, 190);
  ctx.fillStyle = '#94a3b8';
  ctx.font = 'bold 28px Consolas, monospace';
  ctx.fillText('ACTIVE MODULES', 110, 355);
  ctx.fillText('VERIFIED SOURCE LOC', 560, 355);
  ctx.fillStyle = '#facc15';
  ctx.font = 'bold 64px Consolas, monospace';
  ctx.fillText(String(animFiles), 110, 435);
  ctx.fillStyle = '#34d399';
  ctx.fillText(animLoc.toLocaleString(), 560, 435);

  // Animated architecture modules tree
  let y0 = 560;
  MODS.slice(0, 6).forEach((m, idx) => {{
    const active = (t > 2 + idx * 3.5);
    const barW = active ? Math.min(W - 220, Math.max(140, (m.loc / (MODS[0]?.loc || 1)) * (W - 220))) : 40;
    ctx.fillStyle = active ? 'rgba(30, 41, 59, 0.92)' : 'rgba(15, 23, 42, 0.5)';
    ctx.fillRect(70, y0, W - 140, 105);
    ctx.fillStyle = active ? '#00f0ff' : '#475569';
    ctx.fillRect(70, y0 + 95, barW, 8);
    ctx.fillStyle = '#e2e8f0';
    ctx.font = 'bold 28px Consolas, monospace';
    ctx.fillText(m.path.slice(-42), 95, y0 + 48);
    ctx.fillStyle = '#fbbf24';
    ctx.font = '24px Consolas, monospace';
    ctx.fillText(m.loc + ' lines', 95, y0 + 82);
    y0 += 126;
  }});

  // Where to find & how to use card (lower-third safe margin)
  ctx.fillStyle = 'rgba(2, 6, 23, 0.94)';
  ctx.fillRect(55, 1380, W - 110, 290);
  ctx.strokeStyle = '#fbbf24';
  ctx.lineWidth = 3;
  ctx.strokeRect(55, 1380, W - 110, 290);
  ctx.fillStyle = '#fbbf24';
  ctx.font = 'bold 30px Consolas, monospace';
  ctx.fillText('WHERE TO FIND & RUN', 85, 1435);
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 32px Arial, sans-serif';
  wrapText(URL_LBL + '  |  ' + USAGE_LBL, 85, 1495, W - 170, 46);
}};
window.READY = true;
window.render(0);
</script></body></html>"""

    os.makedirs(os.path.dirname(os.path.abspath(out_html)), exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(canvas_html)

    return {"html_path": out_html, "script_text": script_text, "summary": summary}


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "codebase_motion.html")
        res = build_codebase_motion_html(r"C:\Users\abhis\Projects\IVA", out)
        print(f"[PASS] Codebase Motion HTML built for {res['summary']['repo_name']}: "
              f"{res['summary']['total_code_files']} files, {res['summary']['total_loc']:,} LOC")
