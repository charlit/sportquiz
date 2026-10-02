# Sport Quiz

QCM de sport : 15 questions de plus en plus difficiles (5 niveaux), 20 s par question, classement partagé.

- **Spécial Foot** ou **Multisport** (foot, tennis, rugby, F1, cyclisme)
- Questions dans `questions.js` : `[niveau, question, bonne réponse, mauvaise, mauvaise, mauvaise]`
- `server.py` (Python, stdlib) sert le jeu + `api/scores` ; scores dans `data/scores.json`

## Local

```bash
python server.py        # http://localhost:8000
python test_server.py   # self-check
```

## Mac mini

```bash
docker run -d --name sportquiz --restart unless-stopped -p 8089:8000 -v ~/sportquiz:/app -w /app python:3.12-alpine python server.py
```
Caddy : `handle_path /quiz/* { reverse_proxy host.docker.internal:8089 }`
