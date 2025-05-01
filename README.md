<div  id="sanscoeur" align="center">
  <img src="https://github.com/user-attachments/assets/d086a10b-e21c-401d-aca7-d9b09b41ebd6" alt="Sans Coeur">
  <p>Jeu de contrée en ligne développé avec Python, HTML, JavaScript et CSS.</p>
</div>

## Table des matières

- [Table des matières](#table-des-matières)
- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Contribuer](#contribuer)

## Description

SansCoeur est un jeu de contrée en ligne permettant aux joueurs de s'affronter en temps réel. Le projet est développé en Python pour le backend, avec Flask comme framework web, et utilise HTML, JavaScript et CSS pour le frontend.

## Fonctionnalités

- Jeu de contrée multijoueur en temps réel.
- Interface utilisateur interactive avec des graphismes personnalisés.
- Gestion des sessions de jeu et des profils joueurs.

## Prérequis

- Python 3.x
- Flask
- Autres dépendances listées dans `requirements.txt`

## Installation

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/iSeaox/SansCoeur.git
   ```

2. Accédez au répertoire du projet :

    ```bash
    cd SansCoeur
    ```

3. Installez les dépendances :

    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

1. Lancez l'application :

    ```bash
    python app.py
    ```

    Accédez au jeu via [http://127.0.0.1:5000/](http://127.0.0.1:5000/) dans votre navigateur.

## Structure du projet

Le projet est organisé comme suit :

```txt
└── 📁SansCoeur
    └── 📁socket_handlers
        └── __init__.py
        └── game_handlers.py
    └── 📁static                    # Fichiers statiques (CSS, images, JS)
        └── 📁css
            └── card.css
        └── 📁img
            └── ...
        └── 📁js
            └── 📁components
                └── deck.js
                └── gameInfo.js
                └── roundInfo.js
            └── dashboard.js
            └── utils.js
    └── 📁templates                 # Templates HTML
        └── base.html
        └── 📁components
            └── gameInfo.html
            └── roundInfo.html
        └── dashboard.html
        └── index.html
        └── login.html
        └── games.html              # Page listant les parties
        └── profile.html            # Page de profil utilisateur
    └── .gitignore
    └── app.py                      # Point d'entrée de l'application Flask
    └── auth.py                     # Gestion de l'authentification
    └── config.py                   # Configuration de l'application
    └── game.py                     # Logique du jeu
    └── gameManager.py              # Gestion des parties
    └── logManager.py               # Gestion des logs de jeu et chat
    └── player.py                   # Gestion des joueurs
    └── README.md
    └── requirement.txt             # Liste des dépendances Python
    └── round.py                    # Gestion des tours de jeu
    └── roundManager.py             # Gestion des manches de jeu
    └── statisticManager.py         # Analyse statistique des parties
    └── chat.py                     # Système de chat en jeu
    └── TODO.md                     # Liste des améliorations futures
```

## Contribuer

1. Forkez le dépôt.

2. Créez une branche pour votre fonctionnalité (git checkout -b feature/ma-fonctionnalité).

3. Commitez vos modifications (git commit -am 'Ajoute une nouvelle fonctionnalité').

4. Pushez sur votre branche (git push origin f-ma-fonctionnalité).

5. Ouvrez une pull request.
