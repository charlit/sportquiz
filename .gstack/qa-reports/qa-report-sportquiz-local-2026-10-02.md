# QA — Sport Quiz (local, desktop + mobile 375x812) — 2026-10-02

Cible : http://localhost:8193/ (base de test `data/test-scores.json`, rien envoyé au site en ligne).
Niveau : Standard (corrige critique / élevé / moyen). Navigateur : gstack browse (headless).

Testé : accueil, 5 modes jusqu'au Game over, chrono qui expire (perte d'une vie), écran de fin,
enregistrement du score (pseudo vide, pseudo HTML `<b>x</b><i>`, triple clic), onglets du classement,
retour arrière du navigateur en pleine partie, mobile en Multisport et Hardcore Rugby, contenu de la base (818 questions).

OK : 0 erreur JS, pseudo HTML bien échappé (pas d'injection), pas de débordement horizontal sur mobile,
chrono et vies corrects, points en jeu affichés en direct en Hard/Hardcore, tests serveur verts.

| # | Sévérité | Catégorie | Problème | Statut |
|---|----------|-----------|----------|--------|
| 001 | Moyenne | UX | Aucun moyen de quitter une partie en cours ; « retour » du navigateur sort du site | Corrigé `a0cde18` : bouton ✕ + confirmation, annule aussi la question suivante déjà programmée |
| 002 | Moyenne | UX | Pseudo fait d'espaces : « Impossible d'enregistrer, réessaie. » (fait croire à une panne) + erreur 400 | Corrigé `3b423f0` : `pattern=".*\S.*"`, bloqué par le navigateur avant l'envoi |
| 005 | Moyenne | Accessibilité | Résultat (Bravo / Raté / Game over) jamais annoncé aux lecteurs d'écran | Corrigé `676dc96` : `role="status" aria-live`, « pts en jeu » sorti de la zone annoncée |
| 003 | Faible | Fonctionnel | Triple clic sur « Enregistrer » envoie 3 requêtes (sans effet : le serveur garde le meilleur score) | Corrigé `a84f33d` : envoi verrouillé pendant la requête (1 seul POST vérifié) |
| 004 | Faible | Contenu | 13 questions où la bonne réponse se devine à sa longueur (ex. règle du 50:22, « ace », lob, amortie). Pas de biais global : bonne réponse la plus longue dans 21 % des cas (hasard = 25 %) | Corrigé `ffe3e3f` : mauvaises réponses réécrites à longueur comparable, 0 cas restant |
| 006 | Faible | Contenu | Sous-titre « 15 questions » faux pour les modes Hard / Hardcore (sans fin) | Corrigé `f8470ec` : « Des questions de plus en plus dures… » |

Tests de non-régression automatiques : non ajoutés (les tests du projet couvrent le serveur Python ; les 3 corrections sont côté page, vérifiées au navigateur).

Captures : `screenshots/initial.png`, `issue-001-no-quit.png`, `issue-001-after.png`, `issue-002-blank-pseudo.png`,
`issue-002-after.png`, `issue-003-after.png`, `issue-006-after.png`, `issue-005-before-answer.png`, `issue-005-after.png`, `page-hard-mobile.png`, `final-mobile-quiz.png`.

Santé : **96 → 100** (UX 84 → 100, Accessibilité 92 → 100, Fonctionnel 97 → 100, Contenu 94 → 100).

"QA found 6 issues, fixed 6, health score 96 → 100."
