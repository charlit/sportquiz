# Sport Quiz

QCM de sport : 15 questions de plus en plus difficiles (5 niveaux), 20 s par question, classement partagé.

- **Spécial Foot** et **Multisport** (foot, rugby, basket, tennis, F1, cyclisme) : 15 questions, 2 vies
- **Hardcore** : 1 vie, niveaux 4-5 sans fin, au choix tous sports / foot / rugby / basket (classement par mode)
- **Aventure** : foot, rugby, basket, F1 ou tennis, 10 étapes de 5 questions, 4 bonnes réponses pour débloquer la suivante (progression gardée dans le navigateur)
- Questions dans `questions.json` (seule source) : `[niveau, question, bonne réponse, mauvaise, mauvaise, mauvaise]`.
  `server.py` le sert à la page sous forme de `questions.js` ; l'app iOS ([sportquiz-ios](https://github.com/charlit/sportquiz-ios))
  l'embarque et télécharge en arrière-plan la dernière version depuis GitHub (`main`) : **une question poussée sur `main` arrive
  dans l'app sans republier sur l'App Store** (à la partie suivante, ou au lancement suivant).
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
