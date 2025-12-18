# Backend FastAPI – Suivi de Projets Pédagogiques

Ce dossier contient le backend **FastAPI** pour la gestion du système de suivi de projets pédagogiques (utilisateurs, formations, promotions, étudiants, formateurs, espaces pédagogiques, travaux, etc.).

Ce guide explique comment installer et lancer le backend en local, et comment créer la base de données MySQL.

---

## 🚀 Démarrage Rapide (Équipe Front-end)

### Prérequis
- Python 3.11+ ou 3.13
- MySQL ou MariaDB installé et démarré

### Installation et Lancement (3 commandes)

```bash
# 1. Créer et activer l'environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le serveur
uvicorn main:app --reload
```

### Accès
- **API** : http://127.0.0.1:8000/
- **Documentation Swagger** : http://127.0.0.1:8000/docs
- **Compte DE par défaut** : `de@genielogiciel.com` / `admin123`

---

## 📋 Configuration Initiale

### 1. Base de données MySQL
Ouvrir **phpMyAdmin** et créer la base :

```sql
CREATE DATABASE genie_logiciel
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
```

### 2. Configuration (si nécessaire)
Modifier `database/database.py` si votre configuration MySQL diffère :

```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://utilisateur:motdepasse@hote/genie_logiciel"
```

### 3. Initialisation automatique
Au premier démarrage, le système :
- ✅ Crée automatiquement toutes les tables
- ✅ Initialise le compte Directeur d'Établissement (DE)
- ✅ Affiche le mot de passe temporaire dans la console

---

## 🔐 Authentification

### Compte Directeur d'Établissement (DE)
- **Email** : `de@genielogiciel.com`
- **Mot de passe temporaire** : `admin123`
- **Obligatoire** : Changez le mot de passe lors de la première connexion

### Flow d'authentification
1. **Connexion** : `POST /api/auth/login`
2. **Première connexion DE** : Redirection vers changement mot de passe
3. **Connexion normale** : Token JWT retourné

### Endpoints disponibles
- `POST /api/auth/login` - Connexion
- `POST /api/auth/changer-mot-de-passe` - Changement mot de passe (DE)
- `POST /api/auth/activer-compte` - Activation compte utilisateur
- `POST /api/auth/reset-tentatives` - Réinitialiser tentatives (debug)

---

## 🛠️ Pour l'Équipe Front-end

### Consommation de l'API
- **URL de base** : `http://127.0.0.1:8000`
- **Headers requis** : `Authorization: Bearer <token_jwt>`
- **Content-Type** : `application/json`

### Exemple de connexion
```javascript
const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'de@genielogiciel.com',
    mot_de_passe: 'admin123'
  })
});

const data = await response.json();
// Si data.statut === "CHANGEMENT_MOT_DE_PASSE_REQUIS", rediriger vers formulaire
// Sinon, utiliser data.token pour les requêtes authentifiées
```

### Gestion des erreurs
Les erreurs retournent un format structuré :
```json
{
  "detail": {
    "code": "AUTH_01",
    "message": "Identifiants invalides"
  }
}
```

### Codes d'erreur fréquents
- `AUTH_01` : Identifiants invalides
- `AUTH_04` : Trop de tentatives (attendre 15 minutes)

---

## 📚 Modèles de Données

### Entités principales
- **Utilisateur** : Base avec rôles (DE, FORMATEUR, ETUDIANT)
- **Formation/Promotion** : Structure pédagogique
- **EspacePedagogique** : Espaces de cours par formateur
- **Travail** : Devoirs individuels/collectifs
- **Assignation/Livraison** : Suivi des rendus

### Relations
```
Utilisateur ←→ Etudiant/Formateur
Formation → Promotions → Etudiants
Formateur → EspacesPédagogiques → Travaux → Assignations → Livraisons
```

---

## 🧪 Tests

### Lancer les tests
```bash
# Tests unitaires
pytest test_auth_unitaire.py

# Tests d'intégration
python test_auth.py
```

---

## 📝 Notes importantes

### Sécurité
- ✅ Mots de passe hashés avec SHA-256
- ✅ Tokens JWT avec expiration 30 minutes
- ✅ Protection contre bruteforce (5 tentatives/15min)
- ✅ CORS configuré pour développement (`origins = ["*"]`)

### Développement
- 🔄 Mode `--reload` activé pour développement
- 📚 Documentation interactive disponible sur `/docs`
- 🐛 Logs détaillés dans la console pour debug

### Production
- 🔒 Modifier `origins` pour restreindre les domaines
- 🔑 Utiliser variables d'environnement pour les secrets
- 🗄️ Configurer Alembic pour les migrations en production

---

## 🆘 Support

En cas de problème :
1. Vérifiez les logs dans la console au démarrage
2. Consultez la documentation Swagger : http://127.0.0.1:8000/docs
3. Vérifiez la connexion à la base de données MySQL

---

**Dernière mise à jour** : Décembre 2024
