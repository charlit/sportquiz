# QA — Sport Quiz, branche `refonte` (local, mobile 375x812 et 320x640) — 2026-10-08

Cible : http://localhost:8193/ (base de test `data/test-scores.json`, rien envoyé au site en ligne, rien déployé).
Niveau : Standard (corrige critique / élevé / moyen). Navigateur : gstack browse (headless).

Testé :
- **Aventure Ligue 1** : carte (18 clubs, 17 villes, Paris ×2), filtre par ville (souris, Entrée, Espace), puce « ✕ » de réinitialisation,
  10 étapes × 18 clubs (les 180 étapes produisent 5 questions), étape réussie, étape ratée (2 erreurs), chrono qui expire,
  « Réessayer », bouton ✕ en 2 appuis → carte du club, bouton « Carte », progression conservée, club terminé (vert sur la carte).
- **Non-régression** : Spécial Foot (100 questions, 3 vies, niveaux croissants), Multisport (15 questions, 7 sports dont boxe),
  Hardcore par sport (7 sports, points en jeu en direct), enregistrement du score, écran Classement (9 onglets, ouvert sur le dernier mode joué),
  règles ⓘ des 4 modes, tests serveur (questions.js et clubs.js).
- **Mobile** : aucun débordement horizontal à 320 px sur aucun écran.
- **Contenu** : recherche automatique des questions dont un nombre de l'énoncé se retrouve seulement dans la bonne réponse.

OK : 0 erreur JS sur tout le parcours.

| # | Sévérité | Catégorie | Problème | Statut |
|---|----------|-----------|----------|--------|
| 001 | Moyenne | Accessibilité | Carte : après un choix de ville au clavier, la carte est redessinée et le focus retombe sur la page ; Espace ne fonctionne pas | Corrigé `5b6dc0f` : focus rendu au même point, Entrée et Espace, `aria-pressed` |
| 002 | Moyenne | UX / texte | Échec d'étape : « Réessaie, les questions changent ! » alors que la plupart des étapes n'ont que 5 questions (4 sur 5 reviennent au 2e essai) | Corrigé `7e9a571` |
| 003 | Moyenne | Contenu | 5 questions où un nombre de l'énoncé donne la réponse (« créé en 1990 » → Ultra Boys 90, Commando Ultra' 84, Ultras Monaco 1994, Lens « sur 20 » → 20e, basket « ligne à 3 points » → 3) | Corrigé `31cd0bf` + `7891504` (la 1re reformulation OM était ambiguë avec les South Winners, 1987) |
| 004 | Faible | Visuel | À 320 px : noms des villes de la carte très petits (≈ 9 px) et bouton « ← Accueil » sur deux lignes | Reporté |

Captures : `screenshots/qa2-adv-timeout.png`, `qa2-320-home.png`, `qa2-320-adv.png`, `qa2-320-quiz.png`, `qa2-final.png`.

Tests de non-régression automatiques : non ajoutés (corrections côté page et contenu ; le contrôle des 180 étapes et la recherche
des nombres révélateurs ont été lancés dans le navigateur / en script).

Santé : **97 → 100** (Accessibilité 92 → 100, UX 92 → 100, Contenu 92 → 100 ; Visuel 97, point faible reporté).

"QA found 4 issues, fixed 3, health score 97 → 100."
