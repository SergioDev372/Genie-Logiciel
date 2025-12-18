# Système de Promotions Automatiques

## Vue d'ensemble

Le système génère automatiquement les promotions en fonction de l'année académique sélectionnée par le DE lors de la création d'étudiants. Plus besoin de créer manuellement les promotions !

## Fonctionnalités

### ✅ **Génération automatique de promotions**
- Création automatique basée sur l'année académique (format: `2024-2025`)
- Dates automatiques : 1er septembre → 30 juin
- Libellé automatique : `Promotion 2024-2025`
- Réutilisation des promotions existantes

### ✅ **Interface simplifiée pour le DE**
- Sélection d'une année académique au lieu d'un ID de promotion
- Liste des années disponibles via API
- Validation automatique du format

### ✅ **Formation par défaut**
- Création automatique d'une "Formation Générale" si aucune formation n'existe
- Réutilisation des formations existantes

## API Endpoints

### `GET /api/gestion-comptes/annees-academiques`
Liste les années académiques disponibles pour la création d'étudiants.

**Réponse :**
```json
{
  "annees_disponibles": ["2025-2026", "2026-2027", "2027-2028", "2028-2029"],
  "format": "YYYY-YYYY",
  "exemple": "2024-2025"
}
```

### `GET /api/gestion-comptes/promotions`
Liste toutes les promotions existantes.

**Réponse :**
```json
{
  "promotions": [
    {
      "id_promotion": "USR_1766068574_9098",
      "annee_academique": "2025-2026",
      "libelle": "Promotion 2025-2026",
      "date_debut": "2025-09-01",
      "date_fin": "2026-06-30",
      "formation": "Formation Générale"
    }
  ],
  "total": 1
}
```

### `POST /api/gestion-comptes/creer-etudiant` (Modifié)
Création d'étudiant avec année académique au lieu d'ID de promotion.

**Requête :**
```json
{
  "email": "etudiant@example.com",
  "nom": "Dupont",
  "prenom": "Jean",
  "annee_academique": "2024-2025"
}
```

**Réponse :**
```json
{
  "message": "Compte étudiant créé avec succès",
  "email_envoye": true,
  "identifiant": "ETD_1766068646_4264",
  "id_etudiant": "ETD_1766068646_7734",
  "matricule": "MAT20254072"
}
```

## Logique de génération

### Algorithme de génération de promotion
```
1. Vérifier si promotion existe pour l'année académique
2. SI existe → Retourner promotion existante
3. SINON :
   a. Obtenir/créer formation par défaut
   b. Extraire années de début/fin (ex: 2024-2025 → 2024, 2025)
   c. Générer dates : 1er sept année_début → 30 juin année_fin
   d. Créer promotion avec libellé automatique
   e. Sauvegarder et retourner
```

### Validation d'année académique
- Format obligatoire : `YYYY-YYYY`
- Année de fin = Année de début + 1
- Années entre 2020 et 2050
- Exemples valides : `2024-2025`, `2023-2024`
- Exemples invalides : `2024-2026`, `2024`, `invalid`

## Avantages

### 🎯 **Simplicité pour le DE**
- Plus besoin de créer manuellement les promotions
- Interface intuitive avec sélection d'année
- Gestion automatique des formations

### 🔄 **Réutilisation intelligente**
- Les promotions existantes sont réutilisées
- Pas de doublons
- Cohérence des données

### 📅 **Gestion temporelle automatique**
- Calcul automatique des années disponibles
- Dates de début/fin cohérentes
- Adaptation au calendrier académique

### 🛡️ **Robustesse**
- Validation stricte des formats
- Gestion d'erreurs complète
- Transactions sécurisées

## Workflow utilisateur

### Pour le DE (Création d'étudiant)
1. **Authentification** : Se connecter en tant que DE
2. **Sélection année** : Choisir l'année académique dans la liste
3. **Saisie données** : Email, nom, prénom de l'étudiant
4. **Création** : Le système génère automatiquement la promotion
5. **Confirmation** : L'étudiant reçoit ses identifiants par email

### Pour l'étudiant
1. **Réception email** : Identifiants de connexion
2. **Première connexion** : Avec email + mot de passe temporaire
3. **Changement mot de passe** : Obligatoire à la première connexion
4. **Accès complet** : Utilisation normale de l'application

## Exemples d'utilisation

### Création d'étudiant pour 2024-2025
```bash
# Le DE sélectionne "2024-2025" dans l'interface
# Le système :
# 1. Vérifie si "Promotion 2024-2025" existe
# 2. Si non, la crée automatiquement avec :
#    - Dates: 2024-09-01 → 2025-06-30
#    - Libellé: "Promotion 2024-2025"
# 3. Assigne l'étudiant à cette promotion
# 4. Envoie l'email avec les identifiants
```

### Années disponibles (exemple en décembre 2024)
```
- 2025-2026 (année suivante)
- 2026-2027 (dans 2 ans)
- 2027-2028 (dans 3 ans)
- 2028-2029 (dans 4 ans)
```

## Tests validés

✅ Génération automatique de promotions  
✅ Validation des formats d'année  
✅ Réutilisation des promotions existantes  
✅ Création d'étudiants avec année académique  
✅ Envoi d'emails avec identifiants  
✅ Connexion et changement de mot de passe  

## Migration

- **Promotions existantes** : Conservées et réutilisées
- **Étudiants existants** : Non affectés
- **Nouvelles créations** : Utilisent le nouveau système
- **Compatibilité** : Totale avec l'existant