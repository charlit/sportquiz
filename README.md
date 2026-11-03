# Sport Quiz

QCM de foot : 15 questions de plus en plus difficiles (5 niveaux), 20 s par question, classement partagé.

- **Spécial Foot** : 100 questions, 3 vies
- **Hardcore** : 1 vie, niveaux 4-5 sans fin, au choix tout le foot ou les clubs d'un pays (classement par mode)
- **Aventure** : un menu des pays, puis la carte du pays (toucher une ville affiche ses clubs) : 18 clubs de Ligue 1, 10 grands clubs d'Espagne, 10 du Royaume-Uni
  (Angleterre + Celtic et Rangers), 10 d'Allemagne et 10 d'Italie ; 10 étapes par club, de 2024-2026 (étape 1) à 1996-1999 (étape 10),
  5 questions par étape, 4 bonnes réponses pour débloquer la suivante (progression gardée dans le navigateur).
  Questions dans `clubs.json` (`pays` : fr / es / uk / de / it ; `[étape, question, bonne réponse, mauvaise ×3]`), servies à la page sous forme de `clubs.js` ;
  l'app iOS télécharge aussi la dernière version de `clubs.json` depuis GitHub (`main`), comme les questions par sport.
- Questions de foot général dans `questions/foot.json` (seule source ; le quiz n'a plus d'autres sports) :
  `[niveau, question, bonne réponse, mauvaise, mauvaise, mauvaise]`. `server.py` les réunit et les sert à la page sous forme de `questions.js` ; l'app iOS ([sportquiz-ios](https://github.com/charlit/sportquiz-ios))
  les embarque et télécharge en arrière-plan la dernière version depuis GitHub (`main`) : **une question poussée sur `main` arrive
  dans l'app sans republier sur l'App Store** (à la partie suivante, ou au lancement suivant).
- **Défi de la semaine** : chaque lundi, 10 questions sur une personnalité (`semaine.json` : `debut` = un lundi « AAAA-MM-JJ »,
  `titre`, `icone`, `intro`, `q` = 10 × `[niveau, question, bonne réponse, mauvaise ×3]`), une seule tentative, classement remis à zéro chaque lundi
  (serveur : « semaine:<debut> », app : classement Game Center récurrent `sportquiz.semaine`). Sans défi pour la semaine en cours, la tuile l'annonce.
  L'app télécharge aussi `semaine.json` depuis GitHub : **ajouter des semaines à l'avance suffit, sans mise à jour de l'app**.
- **Avant-match** : 24 h avant une grosse affiche entre deux clubs de l'Aventure (Ligue 1, Liga, Premier League, Bundesliga,
  Serie A, Ligue des champions), un quiz de 10 questions (5 par équipe, tirées de `clubs.json`) apparaît sur l'accueil, rejouable
  jusqu'au coup d'envoi, sans classement. `matchs.json` est mis à jour toutes les 6 h par le robot GitHub
  (`.github/workflows/matchs.yml` → `scripts/matchs.py`, calendrier football-data.org, clé dans le secret `FOOTBALL_DATA_KEY`).
- `server.py` (Python, stdlib) sert le jeu + `api/scores` ; scores dans `data/scores.json`
- Page **`/admin`** (joueurs du site, dernière partie, badges, meilleurs scores, joueurs par mode) : identifiant `admin`,
  mot de passe dans la variable d'environnement `QUIZ_ADMIN_PASSWORD` (sans elle, la page n'existe pas).

## Local

```bash
python server.py        # http://localhost:8000
python test_server.py   # self-check
```

## Mac mini

```bash
docker run -d --name sportquiz --restart unless-stopped -p 8089:8000 -e QUIZ_ADMIN_PASSWORD='…' -v ~/sportquiz:/app -w /app python:3.12-alpine python server.py
```
Caddy : `handle_path /quiz/* { reverse_proxy host.docker.internal:8089 }`
