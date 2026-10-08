# Regression: ISSUE-001 — un très bon score au Spécial Foot (> 30 000 pts) était refusé par le serveur (400)
# Found by /qa on 2026-10-08
# Report: .gstack/qa-reports/qa-report-sportquiz-local-2026-10-08.md
import os, re
import server

html = open(os.path.join(os.path.dirname(server.__file__), 'index.html'), encoding='utf-8').read()
plan = [int(x) for x in re.search(r'const FOOT_PLAN = \[([\d, ]+)\]', html).group(1).split(',')]
best = 100 * sum(lvl * n for lvl, n in enumerate(plan))   # bonne réponse instantanée = niveau × 100 pts
assert server.MAX_SCORE['foot'] >= best, (server.MAX_SCORE['foot'], best)
assert server.MAX_SCORE['multi'] >= 100 * 3 * sum(range(1, 6))   # Multisport : 3 questions par niveau
print('ok regression 001')
