import sqlite3

con = sqlite3.connect("results/history.db")

print("== Execuções ==")
for r in con.execute(
    "SELECT id, started_at, total, passed, failed, flaky, ROUND(duration_ms/1000.0, 1) "
    "FROM runs ORDER BY id"
):
    print(f"#{r[0]}  {r[1]}  total={r[2]} ok={r[3]} falhou={r[4]} flaky={r[5]}  {r[6]}s")

print("\n== Taxa de sucesso por teste ==")
for r in con.execute(
    "SELECT title, COUNT(*) AS runs, "
    "ROUND(100.0 * SUM(CASE WHEN status = 'expected' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct "
    "FROM test_results GROUP BY file, title ORDER BY pct, title"
):
    print(f"{r[2]:>5}%  ({r[1]} execuções)  {r[0]}")

print("\n== Testes mais lentos (média) ==")
for r in con.execute(
    "SELECT title, ROUND(AVG(duration_ms)) AS avg_ms FROM test_results "
    "GROUP BY file, title ORDER BY avg_ms DESC LIMIT 5"
):
    print(f"{r[1]:>7.0f} ms  {r[0]}")

print("\n== Testes com retry ou instáveis ==")
rows = list(con.execute(
    "SELECT title, COUNT(*) FROM test_results "
    "WHERE retries > 0 OR status = 'flaky' GROUP BY file, title"
))
for r in rows:
    print(f"{r[1]}x  {r[0]}")
if not rows:
    print("nenhum")