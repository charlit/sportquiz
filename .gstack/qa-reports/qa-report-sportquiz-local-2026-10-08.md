# QA — Sport Quiz, main (local, mobile 375x812 et 320x640) — 2026-10-08

Cible : http://localhost:8193/ (base de test `data/test-scores.json`, rien envoyé au site en ligne, rien déployé).
Niveau : Standard (corrige critique / élevé / moyen). Navigateur : gstack browse (headless ; Aside indisponible sous Windows).
Périmètre : nouveautés du jour (Aventure Espagne / Royaume-Uni, 16 nouveaux badges, palier Platine) + non-régression.

Testé en jouant (réponses cliquées dans la page, pas de raccourci sur la logique des badges) :
- **Aventure** : onglets France / Espagne / Royaume-Uni, cartes et villes, liste des clubs, étape ratée (2 erreurs) puis « Réessayer »,
  étape réussie, étape 10 → « Champion ! », retour « Autre club » dans le bon pays, ville verte quand tous ses clubs sont finis.
- **Badges** gagnés en jouant : Supporter, Globe-trotter, Vuelta des clubs, Polyvalent + Décathlonien (Multisport 15/15, 4 500 pts),
  Série + Grand Chelem (Hardcore Tennis, 15 d'affilée), Marathon + Légende du foot (Spécial Foot 98/100) puis Sans faute (100/100).
- **Encart** : Or à 11 badges (« encore 1 pour l'encart Platine »), Platine à 12, Légende animée à 22.
- **Profil web** : création d'un profil avec 11 badges, tous gardés par le serveur.
- **Mobile 320 px** : pas de défilement horizontal (Aventure, profil).
- Console : aucune erreur JS (seules erreurs réseau : le 400 du bug 001 et un 403 volontaire, code de profil faux).

| # | Sévérité | Catégorie | Problème | Statut |
|---|----------|-----------|----------|--------|
| 001 | Élevée | Fonctionnel | Spécial Foot : un très bon score (31 900 et 32 500 pts) est refusé par le serveur (400, « Impossible d'enregistrer, réessaie. »). Le plafond serveur était 30 000 alors que le maximum possible est 32 500 (FOOT_PLAN). Touche aussi le site en ligne. | Corrigé `ec0f108` (+ test `a5377bb`) : 32 500 enregistré, 1er au classement |
| 002 | Faible | Visuel | Onglet « Royaume-Uni » sur deux lignes à 375 px et moins (onglets plus hauts) | Reporté |
| 003 | Faible | Contenu | Sous Windows, les drapeaux emoji s'affichent en lettres (FR / ES / GB) ; normal sur iPhone / Mac | Reporté (police du système) |

Faux positif écarté : le serveur local de test tournait depuis avant l'ajout des badges et ignorait les nouveaux ; après redémarrage, tous gardés.
Le serveur en ligne avait déjà été redémarré au déploiement des badges.

Captures : `screenshots/qa3-es-map.jpg`, `qa3-uk-map.jpg`, `qa3-champion.jpg`, `qa3-es-done.jpg`, `qa3-multi-end.jpg`,
`qa3-foot-end.jpg`, `qa3-foot-save.jpg` (avant), `issue-001-after.jpg` (après), `qa3-320-adv.jpg`, `qa3-320-profile.jpg`, `qa3-legende.jpg`.

Test de non-régression : `test_regression_001.py` (le plafond serveur doit couvrir le meilleur score possible calculé depuis FOOT_PLAN ;
échoue sur l'ancien code, passe après correction).

Santé : **97 → 100** (Fonctionnel 85 → 100 ; Visuel 97, Contenu 97 : points faibles reportés ; total pondéré 96,6 → 99,6).

"QA found 3 issues, fixed 1, health score 97 → 100."

**À déployer** : la correction 001 est dans `server.py` ; le jeu en ligne refuse encore les scores au-dessus de 30 000 tant que
le Mac mini n'a pas été mis à jour et redémarré (non fait : consigne de ne pas déployer pendant la QA).
