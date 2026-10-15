import json
import os
import sqlite3
from pathlib import Path

RESULTS = Path("results/results.json")
DB = Path(os.environ.get("HISTORY_DB", "results/history.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL UNIQUE,
  duration_ms REAL NOT NULL,
  total INTEGER NOT NULL,
  passed INTEGER NOT NULL,
  failed INTEGER NOT NULL,
  flaky INTEGER NOT NULL,
  skipped INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS test_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL REFERENCES runs(id),
  file TEXT NOT NULL,
  title TEXT NOT NULL,
  project TEXT NOT NULL,
  status TEXT NOT NULL,
  duration_ms REAL NOT NULL,
  retries INTEGER NOT NULL
);
"""


def collect_specs(suites):
    for suite in suites:
        yield from suite.get("specs", [])
        yield from collect_specs(suite.get("suites", []))


def main():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    stats = data["stats"]
    total = stats["expected"] + stats["unexpected"] + stats["flaky"] + stats["skipped"]

    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    try:
        cur = con.execute(
            "INSERT INTO runs (started_at, duration_ms, total, passed, failed, flaky, skipped) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (stats["startTime"], stats["duration"], total,
             stats["expected"], stats["unexpected"], stats["flaky"], stats["skipped"]),
        )
    except sqlite3.IntegrityError:
        print("Esta execução já foi importada, nada a fazer.")
        return

    run_id = cur.lastrowid
    rows = []
    for spec in collect_specs(data["suites"]):
        for test in spec["tests"]:
            results = test.get("results", [])
            last = results[-1] if results else {}
            rows.append((
                run_id, spec["file"], spec["title"], test["projectName"],
                test["status"], last.get("duration", 0), max(len(results) - 1, 0),
            ))

    con.executemany(
        "INSERT INTO test_results (run_id, file, title, project, status, duration_ms, retries) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    con.commit()

    print(f"Execução {run_id} importada: {len(rows)} testes.")
    print("Histórico:")
    for r in con.execute(
        "SELECT id, started_at, total, passed, failed, flaky FROM runs ORDER BY id"
    ):
        print(f"  #{r[0]}  {r[1]}  total={r[2]} ok={r[3]} falhou={r[4]} flaky={r[5]}")


if __name__ == "__main__":
    main()