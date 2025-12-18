# Système de Dashboards React

## Vue d'ensemble

Système complet de dashboards adaptatifs selon le rôle utilisateur (DE, FORMATEUR, ETUDIANT) avec authentification JWT et gestion automatique des promotions.

## Architecture

### 🏗️ **Structure des composants**
```
src/
├── components/
│   ├── dashboards/
│   │   ├── DEDashboard.jsx          # Dashboard Directeur d'Établissement
│   │   ├── FormateurDashboard.jsx   # Dashboard Formateur
│   │   └── EtudiantDashboard.jsx    # Dashboard Étudiant
│   ├── forms/
│   │   ├── CreateFormateur.jsx      # Formulaire création formateur
│   │   └── CreateEtudiant.jsx       # Formulaire création étudiant
│   ├── common/
│   │   ├── Navbar.jsx               # Barre de navigation
│   │   ├── StatCard.jsx             # Cartes de statistiques
│   │   └── LoadingSpinner.jsx       # Indicateur de chargement
│   ├── Login.jsx                    # Connexion
│   └── ChangePassword.jsx           # Changement mot de passe
├── services/
│   └── api.js                       # Client API avec intercepteurs
├── utils/
│   └── auth.js                      # Utilitaires authentification
└── App.jsx                          # Routeur principal
```

### 🔐 **Flux d'authentification**
```
1. LOGIN → Vérification identifiants
2. SI mot_de_passe_temporaire → ChangePassword
3. SINON → Redirection dashboard selon rôle
4. Sauvegarde token JWT + données utilisateur
5. Auto-reconnexion au rechargement
```

## Fonctionnalités par rôle

### 👨‍💼 **Dashboard DE (Directeur d'Établissement)**

**Statistiques affichées :**
- Total formateurs, étudiants, promotions, formations
- Étudiants actifs/suspendus
- Promotions récentes
- Comptes créés récemment

**Actions disponibles :**
- ✅ Créer formateur (modal avec formulaire)
- ✅ Créer étudiant (modal avec sélection année académique)
- ✅ Vue d'ensemble complète de l'établissement

**Fonctionnalités :**
- Création formateur avec email automatique
- Création étudiant avec génération automatique de promotion
- Tableaux interactifs avec données temps réel
- Statistiques visuelles avec cartes colorées

### 👨‍🏫 **Dashboard Formateur**

**Statistiques affichées :**
- Espaces pédagogiques gérés
- Travaux créés
- Nombre d'étudiants
- Assignations à corriger

**Sections :**
- Mes espaces pédagogiques (cartes avec détails)
- Travaux récents (tableau)
- Statistiques de correction

### 🎓 **Dashboard Étudiant**

**Statistiques affichées :**
- Travaux total/terminés/en cours/en retard
- Moyenne générale
- Informations promotion et matricule

**Sections :**
- Mes cours (espaces pédagogiques)
- Mes travaux avec statuts et notes
- Indicateurs de retard visuels

## API Integration

### 🔌 **Client API (services/api.js)**
```javascript
// Configuration automatique
- Base URL: http://127.0.0.1:8000
- Headers automatiques
- Intercepteur JWT automatique
- Gestion erreurs 401 (déconnexion auto)

// Endpoints utilisés
- POST /api/auth/login
- POST /api/auth/changer-mot-de-passe
- GET /api/dashboard/de
- GET /api/dashboard/formateur
- GET /api/dashboard/etudiant
- GET /api/gestion-comptes/annees-academiques
- POST /api/gestion-comptes/creer-formateur
- POST /api/gestion-comptes/creer-etudiant
```

### 🛡️ **Gestion authentification**
```javascript
// Sauvegarde automatique
localStorage.setItem('authToken', token)
localStorage.setItem('userData', JSON.stringify(user))

// Auto-reconnexion
useEffect(() => {
  const existingAuth = getAuthData()
  if (existingAuth) redirectToDashboard(role)
}, [])

// Déconnexion sécurisée
clearAuthData() + redirection login
```

## Interface utilisateur

### 🎨 **Design System**
- **Couleurs** : Palette cohérente avec badges colorés par rôle
- **Cartes** : Statistiques avec icônes Lucide React
- **Tableaux** : Responsive avec hover effects
- **Modals** : Formulaires centrés avec validation
- **Navigation** : Navbar avec infos utilisateur et déconnexion

### 📱 **Responsive Design**
- Grilles adaptatives (CSS Grid)
- Cartes flexibles (minmax)
- Tableaux avec scroll horizontal
- Modals adaptées mobile

### ⚡ **UX/Performance**
- Loading spinners pendant chargements
- Messages d'erreur contextuels
- Validation temps réel formulaires
- Auto-refresh données après actions

## Workflow utilisateur complet

### 🚀 **Première connexion DE**
1. Login avec `de@genielogiciel.com` / `admin123`
2. Changement mot de passe obligatoire
3. Redirection dashboard DE
4. Création formateurs/étudiants via modals

### 👨‍🏫 **Première connexion Formateur**
1. Réception email avec identifiants
2. Login avec email + mot de passe temporaire
3. Changement mot de passe obligatoire
4. Redirection dashboard formateur
5. Vue espaces pédagogiques et travaux

### 🎓 **Première connexion Étudiant**
1. Réception email avec identifiants
2. Login avec email + mot de passe temporaire
3. Changement mot de passe obligatoire
4. Redirection dashboard étudiant
5. Vue cours et travaux assignés

## Sécurité

### 🔒 **Mesures implémentées**
- Tokens JWT avec expiration automatique
- Déconnexion automatique si token invalide
- Validation côté client et serveur
- Hashage sécurisé mots de passe (SHA-256)
- Protection CORS configurée

### 🛡️ **Gestion des erreurs**
- Messages d'erreur contextuels
- Retry automatique sur échec réseau
- Fallback gracieux si API indisponible
- Logs détaillés pour debugging

## Déploiement

### 🚀 **Développement**
```bash
# Frontend React
cd front-react
npm run dev
# → http://localhost:5174

# Backend FastAPI
cd back
uvicorn main:app --reload
# → http://127.0.0.1:8000
```

### 📦 **Production**
```bash
# Build React
npm run build

# Servir avec nginx/apache
# API FastAPI avec gunicorn
```

## Tests validés

✅ **Authentification complète**
- Login DE/Formateur/Étudiant
- Changement mot de passe obligatoire
- Sauvegarde/récupération tokens
- Déconnexion sécurisée

✅ **Dashboards fonctionnels**
- Chargement données temps réel
- Statistiques correctes
- Navigation fluide
- Responsive design

✅ **Création de comptes**
- Formateur avec email automatique
- Étudiant avec promotion automatique
- Validation formulaires
- Gestion erreurs

✅ **Intégration API**
- Tous endpoints fonctionnels
- Gestion erreurs robuste
- Performance optimisée

## Prochaines étapes

🔄 **Améliorations possibles**
- Notifications temps réel
- Système de messagerie
- Gestion fichiers/documents
- Calendrier intégré
- Rapports/exports PDF
- Mode sombre
- Internationalisation