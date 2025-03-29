# SansCoeur

**Description** : Jeu de contrée en ligne développé avec Python, HTML, JavaScript et CSS.

## Table des matières

- [SansCoeur](#sanscoeur)
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

SansCoeur/
│
├── app.py                # Point d'entrée de l'application Flask
├── auth.py               # Gestion de l'authentification
├── config.py             # Configuration de l'application
├── game.py               # Logique du jeu
├── player.py             # Gestion des profils joueurs
├── round.py              # Gestion des tours de jeu
├── requirements.txt     # Liste des dépendances Python
├── .gitignore           # Fichiers à ignorer par Git
├── static/              # Fichiers statiques (CSS, images, JS)
└── templates/           # Templates HTML

## Contribuer

1. Forkez le dépôt.

2. Créez une branche pour votre fonctionnalité (git checkout -b feature/ma-fonctionnalité).

3. Commitez vos modifications (git commit -am 'Ajoute une nouvelle fonctionnalité').

4. Pushez sur votre branche (git push origin feature/ma-fonctionnalité).

5. Ouvrez une pull request.
