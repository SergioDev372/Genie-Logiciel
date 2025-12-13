# Backend FastAPI – Suivi de Projets

Ce dossier contient le backend **FastAPI** pour la gestion du système de suivi de projets (utilisateurs, formations, promotions, étudiants, formateurs, espaces pédagogiques, travaux, etc.).

Ce guide explique comment installer et lancer le backend en local, et comment créer la base de données MySQL.

---

## 1. Prérequis

- Python 3.11+ ou 3.13
- MySQL ou MariaDB installé et démarré
- Git installé

---

## 2. Création et activation de l'environnement virtuel (Windows / PowerShell)

Toutes les commandes suivantes se font **depuis ce dossier** `back`.

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Vous devez voir `(venv)` au début de la ligne de commande.

---

## 3. Installer les dépendances Python

Un fichier `requirements.txt` est fourni dans ce dossier `back`.

```bash
pip install -r requirements.txt
```

Cela installe : FastAPI, Uvicorn, SQLAlchemy, PyMySQL, cryptography, etc.

---

## 4. Créer la base MySQL manuellement

Ouvrir **phpMyAdmin** (ou un autre client MySQL) et :

1. Se connecter avec l'utilisateur MySQL configuré dans `database/database.py`.

   Par défaut dans le projet :

   ```python
   SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/genie_logiciel"
   ```

   - utilisateur : `root`
   - mot de passe : (vide)
   - hôte : `localhost`
   - base : `genie_logiciel`

2. Créer la base de données (si elle n'existe pas encore) :

   ```sql
   CREATE DATABASE genie_logiciel
     CHARACTER SET utf8mb4
     COLLATE utf8mb4_general_ci;
   ```

3. Si vous utilisez un autre utilisateur/mot de passe MySQL, adaptez la chaîne de connexion dans `database/database.py`.

---

## 5. Lancer le serveur FastAPI

Depuis ce dossier `back`, avec l'environnement virtuel `(venv)` activé :

```bash
uvicorn main:app --reload
```

Le backend sera accessible sur :

- API : http://127.0.0.1:8000/
- Documentation Swagger : http://127.0.0.1:8000/docs

Au démarrage, SQLAlchemy :

- se connecte à la base `genie_logiciel` définie dans `database/database.py`,
- crée automatiquement toutes les tables définies dans `models.py` (Utilisateur, Formation, Promotion, Etudiant, Formateur, EspacePedagogique, Travail, GroupeEtudiant, Assignation, Livraison, ...).

---

## 6. Notes pour l'équipe front-end

- Pour consommer l'API, utilisez l'URL de base : `http://127.0.0.1:8000`.
- La documentation interactive est disponible sur `/docs`.
- Les endpoints de création de comptes / connexions ne doivent **jamais** exposer les champs sensibles (`mot_de_passe`, `token_activation`, etc.).
- Les mots de passe sont stockés hachés côté backend.

---

## 7. Récapitulatif rapide des commandes

Toujours à partir de ce dossier `back` :

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```
