# TODOs - Sans Cœur Online

Ce document recense les tâches et améliorations à apporter au projet SansCoeur.

## Gestion du jeu

- **gameManager.py** : Supprimer la fonction dépréciée `getGame()` qui devrait être remplacée par `getGameByID()`
- **game.py** : Améliorer la distribution des cartes (actuellement commenté comme "TODO: gérer la distribution des cartes mieux que ça")
- **round.py** : Penser à implémenter la coupe du jeu avant la distribution (commenté comme "TODO: Pensez à couper le jeu")

## Utilisateurs et authentification

- **app.py** : Configurer une vraie base de données pour remplacer le stockage temporaire des utilisateurs (commenté comme "TODO: Setup real BDD")

## Prochaines fonctionnalités

- Améliorer l'affichage des scores à la fin de la partie
- Implémenter un système de statistiques plus complet pour les joueurs
- Ajouter la recherche de GIF
- Créer un request_game_info_update
