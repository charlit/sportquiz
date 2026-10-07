# Sport Quiz

QCM de sport : 15 questions de plus en plus difficiles (5 niveaux), 20 s par question, classement partagé.

- **Spécial Foot** et **Multisport** (foot, rugby, basket, tennis, F1, cyclisme) : 15 questions, 2 vies
- **Hardcore** : 1 vie, niveaux 4-5 sans fin, au choix tous sports / foot / rugby / basket (classement par mode)
- **Aventure** : foot, rugby, basket, F1 ou tennis, 10 étapes de 5 questions, 4 bonnes réponses pour débloquer la suivante (progression gardée dans le navigateur)
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
