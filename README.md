# Sport Quiz

QCM de sport : 15 questions de plus en plus difficiles (5 niveaux), 20 s par question, classement partagé.

- **Spécial Foot** : 100 questions, 3 vies
- **Hardcore** : 1 vie, niveaux 4-5 sans fin, au choix tous sports / foot / rugby / basket (classement par mode)
- **Aventure** : un menu des pays, puis la carte du pays (toucher une ville affiche ses clubs) : 18 clubs de Ligue 1, 10 grands clubs d'Espagne, 10 du Royaume-Uni
  (Angleterre + Celtic et Rangers), 10 d'Allemagne et 10 d'Italie ; 10 étapes par club, de 2024-2026 (étape 1) à 1996-1999 (étape 10),
  5 questions par étape, 4 bonnes réponses pour débloquer la suivante (progression gardée dans le navigateur).
  **Mondial** : les 12 Coupes du monde (1978-2022) sur une carte du monde (pays organisateurs), 5 étapes par édition
  (phase de groupes → finale, de plus en plus dur).
  Questions dans `clubs.json` (`pays` : fr / es / uk / de / it / wc ; `[étape, question, bonne réponse, mauvaise ×3]`), servies à la page sous forme de `clubs.js`.
- Questions dans `questions/<sport>.json`, un fichier par sport (foot, tennis, rugby, basket, f1, velo, boxe ; seule source) :
  `[niveau, question, bonne réponse, mauvaise, mauvaise, mauvaise]`. `server.py` les réunit et les sert à la page sous forme de `questions.js` ; l'app iOS ([sportquiz-ios](https://github.com/charlit/sportquiz-ios))
  les embarque et télécharge en arrière-plan la dernière version depuis GitHub (`main`) : **une question poussée sur `main` arrive
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
