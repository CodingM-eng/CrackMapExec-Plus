"""HTML Report Generator: Self-contained, responsive, dark-mode security dashboard."""

from __future__ import annotations

import html
from datetime import datetime, timezone

from cmeplus import __version__
from cmeplus.core.results import ResultSet


def generate_html_dashboard(result_sets: list[ResultSet] | ResultSet, title: str = "CrackMapExec+ Assessment Report") -> str:
    """Generate self-contained, CSS-styled dark dashboard HTML report."""
    if isinstance(result_sets, ResultSet):
        sets = [result_sets]
    else:
        sets = result_sets

    total_targets = sum(rs.total for rs in sets)
    total_success = sum(rs.success_count for rs in sets)
    total_failed = sum(rs.failed_count + rs.unavailable_count for rs in sets)
    total_duration = sum(rs.total_duration for rs in sets)
    protocols = list({rs.protocol.upper() for rs in sets})
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build table rows
    rows_html = []
    for rs in sets:
        for res in rs.results:
            status_cls = res.status.value.lower()
            badge_text = res.status.value.upper()
            row = f"""
            <tr class="status-{status_cls}">
                <td><code>{html.escape(res.target)}</code></td>
                <td>{res.port or '-'}</td>
                <td><span class="badge badge-proto">{html.escape(res.protocol.upper())}</span></td>
                <td><span class="badge badge-{status_cls}">{html.escape(badge_text)}</span></td>
                <td>{res.duration:.2f}s</td>
                <td>{html.escape(res.message)}</td>
            </tr>
            """
            rows_html.append(row)

    table_body = "\n".join(rows_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --border-color: #334155;
            --text-primary: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --accent-yellow: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.5;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        h1 {{ font-size: 1.75rem; color: var(--accent-cyan); display: flex; align-items: center; gap: 0.5rem; }}
        .meta {{ color: var(--text-muted); font-size: 0.875rem; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            padding: 1.25rem;
        }}
        .card h3 {{ color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .card .value {{ font-size: 2rem; font-weight: 700; margin-top: 0.25rem; }}
        .value.success {{ color: var(--accent-green); }}
        .value.failed {{ color: var(--accent-red); }}
        .value.cyan {{ color: var(--accent-cyan); }}
        .controls {{
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
        }}
        input[type="text"] {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            width: 100%;
            max-width: 400px;
            font-size: 0.95rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            overflow: hidden;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background-color: #182234;
            color: var(--accent-cyan);
            font-weight: 600;
            font-size: 0.875rem;
        }}
        tr:hover {{ background-color: rgba(56, 189, 248, 0.04); }}
        code {{
            background: #090d16;
            padding: 0.15rem 0.4rem;
            border-radius: 0.25rem;
            color: var(--accent-cyan);
            font-family: monospace;
        }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-proto {{ background-color: #0369a1; color: #e0f2fe; }}
        .badge-success {{ background-color: #14532d; color: #86efac; }}
        .badge-failed, .badge-auth_failed {{ background-color: #7f1d1d; color: #fca5a5; }}
        .badge-unavailable, .badge-timeout {{ background-color: #78350f; color: #fde68a; }}
        .badge-error {{ background-color: #991b1b; color: #fecaca; }}
        .badge-skipped {{ background-color: #334155; color: #cbd5e1; }}
        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>CrackMapExec+ <span>Dashboard</span></h1>
                <div class="meta">Generated: {generated_at} • Engine Version: v{__version__}</div>
            </div>
            <div>
                <span class="badge badge-proto">Protocols: {", ".join(protocols)}</span>
            </div>
        </header>

        <section class="grid">
            <div class="card">
                <h3>Total Targets</h3>
                <div class="value cyan">{total_targets}</div>
            </div>
            <div class="card">
                <h3>Success</h3>
                <div class="value success">{total_success}</div>
            </div>
            <div class="card">
                <h3>Failed / Offline</h3>
                <div class="value failed">{total_failed}</div>
            </div>
            <div class="card">
                <h3>Total Duration</h3>
                <div class="value">{total_duration:.2f}s</div>
            </div>
        </section>

        <section>
            <div class="controls">
                <input type="text" id="filterInput" placeholder="Filter targets, protocols, status, or messages..." onkeyup="filterTable()">
            </div>

            <table id="resultsTable">
                <thead>
                    <tr>
                        <th>Target Endpoint</th>
                        <th>Port</th>
                        <th>Protocol</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Output / Response Detail</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </section>

        <footer>
            Authorized Security Lab & Educational Testing Report • CrackMapExec+ v{__version__}
        </footer>
    </div>

    <script>
        function filterTable() {{
            const input = document.getElementById("filterInput");
            const filter = input.value.toLowerCase();
            const rows = document.getElementById("resultsTable").getElementsByTagName("tr");
            for (let i = 1; i < rows.length; i++) {{
                const text = rows[i].textContent.toLowerCase();
                rows[i].style.display = text.includes(filter) ? "" : "none";
            }}
        }}
    </script>
</body>
</html>
"""
