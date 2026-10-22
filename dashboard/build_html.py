import html
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path(os.environ.get("HISTORY_DB", "results/history.db"))
OUT = Path("docs/index.html")
MAX_RUNS_IN_CHARTS = 30

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#666;--card:#f3f3f3;--line:#d9d9d9;
--ok:#2e9e5b;--flaky:#e0a100;--fail:#d64545;--bar:#3b6fd4}
@media (prefers-color-scheme: dark){:root{--bg:#111;--fg:#eee;--muted:#9a9a9a;
--card:#1c1c1c;--line:#333;--ok:#3fbf77;--flaky:#f0b429;--fail:#ef6b6b;--bar:#6f9bf0}}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--bg);color:var(--fg);
font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.5}
main{max-width:900px;margin:0 auto}
h1{margin:0 0 4px}h2{margin:32px 0 8px;font-size:1.15rem}
.sub{color:var(--muted);margin:0 0 24px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.card{background:var(--card);border-radius:8px;padding:14px 16px}
.card .v{font-size:1.6rem;font-weight:600}.card .k{color:var(--muted);font-size:.85rem}
svg{width:100%;height:auto;display:block}
.bar{fill:var(--bar)}.ok{fill:var(--ok)}.flaky{fill:var(--flaky)}.fail{fill:var(--fail)}
.axis{stroke:var(--line)}.lbl{fill:var(--muted);font-size:11px}
.legend{color:var(--muted);font-size:.85rem;margin-top:4px}
.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 12px}
.dot.ok{background:var(--ok)}.dot.flaky{background:var(--flaky)}.dot.fail{background:var(--fail)}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600}td.n{text-align:right;white-space:nowrap}
.good{color:var(--ok)}.bad{color:var(--fail)}
.note{color:var(--muted);font-size:.85rem;margin-top:32px}
"""


def duration_chart(runs):
    w, h, pad_l, pad_b, pad_t = 640, 220, 44, 28, 16
    vals = [r[2] / 1000 for r in runs]
    vmax = max(vals) or 1
    slot = (w - pad_l - 10) / len(vals)
    bw = min(slot * 0.7, 40)
    p = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Duration of each run in seconds">']
    p.append(f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - 10}" y2="{h - pad_b}" class="axis"/>')
    for i, (r, v) in enumerate(zip(runs, vals)):
        bh = (h - pad_b - pad_t) * v / vmax
        x = pad_l + i * slot + (slot - bw) / 2
        y = h - pad_b - bh
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" class="bar">'
                 f'<title>Run #{r[0]}: {v:.1f}s</title></rect>')
        p.append(f'<text x="{x + bw / 2:.1f}" y="{h - pad_b + 14}" class="lbl" text-anchor="middle">#{r[0]}</text>')
    p.append(f'<text x="{pad_l - 6}" y="{pad_t + 4}" class="lbl" text-anchor="end">{vmax:.1f}s</text>')
    p.append(f'<text x="{pad_l - 6}" y="{h - pad_b}" class="lbl" text-anchor="end">0</text>')
    p.append("</svg>")
    return "".join(p)


def status_chart(runs):
    w, h, pad_l, pad_b, pad_t = 640, 220, 44, 28, 16
    tmax = max(r[3] for r in runs) or 1
    slot = (w - pad_l - 10) / len(runs)
    bw = min(slot * 0.7, 40)
    p = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Test outcomes per run">']
    p.append(f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - 10}" y2="{h - pad_b}" class="axis"/>')
    for i, r in enumerate(runs):
        x = pad_l + i * slot + (slot - bw) / 2
        y_cursor = h - pad_b
        for count, cls, name in ((r[4], "ok", "passed"), (r[6], "flaky", "flaky"), (r[5], "fail", "failed")):
            if not count:
                continue
            seg = (h - pad_b - pad_t) * count / tmax
            y_cursor -= seg
            p.append(f'<rect x="{x:.1f}" y="{y_cursor:.1f}" width="{bw:.1f}" height="{seg:.1f}" class="{cls}">'
                     f'<title>Run #{r[0]}: {count} {name}</title></rect>')
        p.append(f'<text x="{x + bw / 2:.1f}" y="{h - pad_b + 14}" class="lbl" text-anchor="middle">#{r[0]}</text>')
    p.append(f'<text x="{pad_l - 6}" y="{pad_t + 4}" class="lbl" text-anchor="end">{tmax}</text>')
    p.append(f'<text x="{pad_l - 6}" y="{h - pad_b}" class="lbl" text-anchor="end">0</text>')
    p.append("</svg>")
    return "".join(p)


def main():
    if not DB.exists():
        print("Banco não encontrado. Rode antes: python3 dashboard/ingest.py")
        return
    con = sqlite3.connect(DB)

    runs = con.execute(
        "SELECT id, started_at, duration_ms, total, passed, failed, flaky FROM runs ORDER BY id"
    ).fetchall()
    if not runs:
        print("Nenhuma execução no banco.")
        return
    chart_runs = runs[-MAX_RUNS_IN_CHARTS:]

    tests = con.execute(
        "SELECT title, file, COUNT(*), "
        "ROUND(100.0 * SUM(CASE WHEN status = 'expected' THEN 1 ELSE 0 END) / COUNT(*), 1), "
        "ROUND(AVG(duration_ms)), "
        "SUM(CASE WHEN retries > 0 OR status = 'flaky' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN attempts > 1 THEN 1 ELSE 0 END), COUNT(attempts), project "
        "FROM test_results GROUP BY file, title, project ORDER BY 4, 5 DESC"
    ).fetchall()

    overall = con.execute(
        "SELECT ROUND(100.0 * SUM(CASE WHEN status = 'expected' THEN 1 ELSE 0 END) / COUNT(*), 1) "
        "FROM test_results"
    ).fetchone()[0]
    avg_duration = sum(r[2] for r in runs) / len(runs) / 1000
    last = runs[-1]

    rows_html = []
    for title, file, n, pct, avg_ms, retried, multi, measured, project in tests:
        attempts_cell = f"{multi} of {measured} runs" if measured else "-"
        cls = "good" if pct == 100 else "bad"
        rows_html.append(
            f"<tr><td>{html.escape(title)}<br><span class='lbl'>{html.escape(file)} - {html.escape(project)}</span></td>"
            f"<td class='n {cls}'>{pct}%</td><td class='n'>{n}</td>"
            f"<td class='n'>{avg_ms / 1000:.1f}s</td><td class='n'>{retried}</td>"
            f"<td class='n'>{attempts_cell}</td></tr>"
        )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Conduit QA Suite - Results</title><style>" + CSS + "</style></head><body><main>"
        "<h1>Conduit QA Suite</h1>"
        f'<p class="sub">Playwright results history. {len(runs)} runs, '
        f"{html.escape(runs[0][1][:10])} to {html.escape(last[1][:10])}. Generated {generated}.</p>"
        '<div class="cards">'
        f'<div class="card"><div class="v">{len(runs)}</div><div class="k">runs recorded</div></div>'
        f'<div class="card"><div class="v">{last[4]}/{last[3]}</div><div class="k">passed in the latest run</div></div>'
        f'<div class="card"><div class="v">{overall}%</div><div class="k">pass rate, all runs</div></div>'
        f'<div class="card"><div class="v">{avg_duration:.1f}s</div><div class="k">average run duration</div></div>'
        "</div>"
        "<h2>Duration per run</h2>" + duration_chart(chart_runs) +
        "<h2>Outcomes per run</h2>" + status_chart(chart_runs) +
        '<div class="legend"><span class="dot ok"></span>passed<span class="dot flaky"></span>flaky'
        '<span class="dot fail"></span>failed</div>'
        "<h2>Tests</h2>"
        '<div class="tablewrap"><table><thead><tr><th>Test</th><th class="n">Pass rate</th>'
        '<th class="n">Runs</th><th class="n">Avg time</th><th class="n">Retried</th><th class="n">Needed 2+ attempts</th></tr></thead><tbody>'
        + "".join(rows_html) +
        "</tbody></table></div>"
        '<p class="note">Pass rate counts the final result of each test. Retries done inside a test '
        "(for example with toPass) are only visible when the test records them, as the article test does. Test run time includes running "
        "tests in parallel, so single-test times are not isolated measurements.</p>"
        "</main></body></html>"
    )

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Página gerada em {OUT} ({len(runs)} execuções, {len(tests)} testes).")


if __name__ == "__main__":
    main()