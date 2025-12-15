# Algorithme de Connexion - Version 3 (Corrigée)

## Structure des Modèles (Mise à jour)

### Modèle `Utilisateur`
- `identifiant`: Clé primaire (String, alphanumérique)
- `email`: Adresse email unique
- `mot_de_passe`: Mot de passe haché
- `nom`: Nom de l'utilisateur
- `prenom`: Prénom de l'utilisateur
- `role`: Rôle (DE, FORMATEUR, ETUDIANT)
- `actif`: Statut actif (Boolean, default=True)
- `mot_de_passe_temporaire`: Mot de passe temporaire (Boolean, default=False) ← **NOUVEAU**
- `date_creation`: Date de création
- `token_activation`: Token d'activation (nullable)
- `date_expiration_token`: Date d'expiration du token (nullable)

**Important**: Le DE n'a PAS de relation vers Formateur ou Etudiant

### Modèle `TentativeConnexion` (Nouveau)
```python
class TentativeConnexion(Base):
    __tablename__ = "tentative_connexion"
    
    id_tentative = Column(String(100), primary_key=True, nullable=False)
    email = Column(String(191), nullable=False)
    date_tentative = Column(DateTime, nullable=False, default=datetime.utcnow)
    succes = Column(Boolean, nullable=False, default=False)
```

## Algorithme 1: Initialisation Automatique du Compte DE

```pseudocode
FONCTION initialiser_compte_de()
    // Vérifier si un compte DE existe déjà
    de = SELECT * FROM utilisateur WHERE role = "DE" LIMIT 1
    
    SI de EST VIDE ALORS
        // Créer un identifiant unique pour le DE
        identifiant_de = "de_principal"
        
        // Créer le compte DE
        nouveau_de = {
            identifiant: identifiant_de,
            email: "de@genielogiciel.com",
            mot_de_passe: hacher_mot_de_passe("admin123"),
            nom: "Directeur",
            prenom: "Établissement",
            role: "DE",
            actif: True,
            mot_de_passe_temporaire: True,  // ← CHAMP NOUVEAU
            date_creation: datetime.utcnow(),
            token_activation: NULL,
            date_expiration_token: NULL
        }
        
        INSERT INTO utilisateur VALUES (nouveau_de)
        
        // NOTA: PAS de création de Formateur pour le DE
        // Le DE n'a pas de relation vers Formateur
        
        RETURN nouveau_de
    SINON
        RETURN de
    FIN SI
FIN FONCTION
```

## Algorithme 2: Route de Connexion (/login)

```pseudocode
ROUTE POST /login
    PARAMÈTRES:
        - email: String (obligatoire)  // ← SIMPLIFICATION: plus d'identifiant_email
        - mot_de_passe: String (obligatoire)
    
    ÉTAPES:
    
    1. // Vérifier la limitation des tentatives
        verifier_tentatives_connexion(email)  // ← NOUVEAU
        
        SI tentative_bloquee ALORS
            RETOURNER Erreur {
                code: "AUTH_04",
                message: "Trop de tentatives. Veuillez attendre 15 minutes."
            }
        
    2. // Rechercher l'utilisateur par email uniquement
        utilisateur = SELECT * FROM utilisateur 
                       WHERE email = email
                       LIMIT 1
    
    3. SI utilisateur EST VIDE ALORS
        // Enregistrer tentative échouée
        INSERT INTO tentative_connexion 
            VALUES (generer_id_unique("TENT"), email, datetime.utcnow(), False)
        
        RETOURNER Erreur {
            code: "AUTH_01",
            message: "Identifiants invalides"
        }
    
    4. SI utilisateur.actif = False ALORS
        // Enregistrer tentative échouée
        INSERT INTO tentative_connexion 
            VALUES (generer_id_unique("TENT"), email, datetime.utcnow(), False)
        
        RETOURNER Erreur {
            code: "AUTH_02",
            message: "Compte désactivé"
        }
    
    5. // Vérifier le mot de passe
        mot_de_passe_correct = verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe)
    
    6. SI mot_de_passe_correct = False ALORS
        // Enregistrer tentative échouée
        INSERT INTO tentative_connexion 
            VALUES (generer_id_unique("TENT"), email, datetime.utcnow(), False)
        
        RETOURNER Erreur {
            code: "AUTH_03",
            message: "Identifiants invalides"
        }
    
    7. // Enregistrer tentative réussie
        INSERT INTO tentative_connexion 
            VALUES (generer_id_unique("TENT"), email, datetime.utcnow(), True)
    
    8. // Vérifier si c'est le DE avec mot de passe temporaire
        est_de_avec_mot_de_passe_temp = (
            utilisateur.role == "DE" 
            AND utilisateur.mot_de_passe_temporaire = True
        )
    
    9. SI est_de_avec_mot_de_passe_temp ALORS
        // Générer un token de changement de mot de passe (valide 24h)
        token_changement = generer_token_unique(32)
        date_expiration = datetime.utcnow() + timedelta(hours=24)
    
        // Sauvegarder le token
        UPDATE utilisateur SET 
            token_activation = token_changement,
            date_expiration_token = date_expiration
        WHERE identifiant = utilisateur.identifiant
    
        // Retourner réponse spéciale pour redirection
        RETOURNER {
            statut: "CHANGEMENT_MOT_DE_PASSE_REQUIS",
            token: token_changement,
            utilisateur: {
                identifiant: utilisateur.identifiant,
                nom: utilisateur.nom,
                prenom: utilisateur.prenom,
                role: utilisateur.role,
                email: utilisateur.email
            }
        }
    
    10. // Connexion normale
        token_jwt = generer_token_jwt(utilisateur)
    
        RETOURNER {
            statut: "SUCCESS",
            token: token_jwt,
            utilisateur: {
                identifiant: utilisateur.identifiant,
                nom: utilisateur.nom,
                prenom: utilisateur.prenom,
                role: utilisateur.role,
                email: utilisateur.email
            }
        }
FIN ROUTE
```

## Algorithme 3: Vérification des Tentatives de Connexion

```pseudocode
FONCTION verifier_tentatives_connexion(email)
    // Compter les tentatives échouées dans les 15 dernières minutes
    tentatives = SELECT * FROM tentative_connexion 
                 WHERE email = email 
                 AND succes = False
                 AND date_tentative > datetime.utcnow() - timedelta(minutes=15)
    
    SI COUNT(tentatives) >= 5 ALORS
        RETOURNER Erreur {
            code: "AUTH_04",
            message: "Trop de tentatives. Veuillez attendre 15 minutes."
        }
    SINON
        RETOURNER null  // Pas de blocage
    FIN SI
FIN FONCTION
```

## Algorithme 4: Changement de Mot de Passe (DE - Première Connexion)

```pseudocode
ROUTE POST /changer-mot-de-passe
    PARAMÈTRES:
        - token: String
        - nouveau_mot_de_passe: String
        - confirmation_mot_de_passe: String
    
    ÉTAPES:
    
    1. // Valider le token
        utilisateur = SELECT * FROM utilisateur 
                       WHERE token_activation = token 
                       AND date_expiration_token > datetime.utcnow()
                       LIMIT 1
    
    2. SI utilisateur EST VIDE ALORS
        RETOURNER Erreur {
            code: "TOKEN_01",
            message: "Token invalide ou expiré"
        }
    
    3. // Vérifier que les mots de passe correspondent
        SI nouveau_mot_de_passe != confirmation_mot_de_passe ALORS
        RETOURNER Erreur {
            code: "PASSWORD_01",
            message: "Les mots de passe ne correspondent pas"
        }
    
    4. // Hacher le nouveau mot de passe
        mot_de_passe_hache = hacher_mot_de_passe(nouveau_mot_de_passe)
    
    5. // Mettre à jour le mot de passe et marquer comme non temporaire
        UPDATE utilisateur SET 
            mot_de_passe = mot_de_passe_hache,
            mot_de_passe_temporaire = False,  // ← MISE À JOUR
            token_activation = NULL,
            date_expiration_token = NULL
        WHERE identifiant = utilisateur.identifiant
    
    6. // Générer token JWT pour la session
        token_jwt = generer_token_jwt(utilisateur)
    
        RETOURNER {
            statut: "SUCCESS",
            message: "Mot de passe changé avec succès",
            token: token_jwt,
            utilisateur: {
                identifiant: utilisateur.identifiant,
                nom: utilisateur.nom,
                prenom: utilisateur.prenom,
                role: utilisateur.role,
                email: utilisateur.email
            }
        }
FIN ROUTE
```

## Algorithme 5: Création de Compte par le DE (Étudiant/Formateur)

```pseudocode
FONCTION creer_compte_par_de(role, donnees)
    // Générer un identifiant unique
    identifiant = generer_identifiant_unique(role)
    
    // Créer le compte utilisateur (inactif)
    utilisateur = {
        identifiant: identifiant,
        email: donnees.email,
        mot_de_passe: "",  // Pas de mot de passe initial
        nom: donnees.nom,
        prenom: donnees.prenom,
        role: role,
        actif: False,  // Compte inactif par défaut
        mot_de_passe_temporaire: False,  // ← PAS de mot de passe temporaire
        date_creation: datetime.utcnow(),
        token_activation: generer_token_unique(32),
        date_expiration_token: datetime.utcnow() + timedelta(hours=72)  // Valide 72h
    }
    
    INSERT INTO utilisateur VALUES (utilisateur)
    
    // Créer l'entrée spécifique (Étudiant ou Formateur)
    SI role == "ETUDIANT" ALORS
        etudiant = {
            id_etudiant: generer_id_unique("ETD"),
            identifiant: identifiant,
            matricule: donnees.matricule,
            id_promotion: donnees.id_promotion,
            date_inscription: donnees.date_inscription,
            statut: "ACTIF"
        }
        INSERT INTO etudiant VALUES (etudiant)
    
    SINON SI role == "FORMATEUR" ALORS
        formateur = {
            id_formateur: generer_id_unique("FRM"),
            identifiant: identifiant,
            numero_employe: donnees.numero_employe,
            specialite: donnees.specialite
        }
        INSERT INTO formateur VALUES (formateur)
    FIN SI
    
    // Envoyer email d'activation avec le token
    lien_activation = "http://application/activation?token=" + utilisateur.token_activation
    envoyer_email(donnees.email, "Activation de votre compte", 
                  "Veuillez activer votre compte en cliquant sur ce lien: " + lien_activation)
    
    RETURN {
        statut: "SUCCESS",
        message: "Compte créé. Un email d'activation a été envoyé.",
        utilisateur: {
            identifiant: utilisateur.identifiant,
            email: utilisateur.email,
            nom: utilisateur.nom,
            prenom: utilisateur.prenom,
            role: utilisateur.role
        }
    }
FIN FONCTION
```

## Algorithme 6: Activation de Compte (Étudiant/Formateur)

```pseudocode
ROUTE POST /activer-compte
    PARAMÈTRES:
        - token: String
        - mot_de_passe: String
        - confirmation_mot_de_passe: String
    
    ÉTAPES:
    
    1. // Valider le token
        utilisateur = SELECT * FROM utilisateur 
                       WHERE token_activation = token 
                       AND date_expiration_token > datetime.utcnow()
                       LIMIT 1
    
    2. SI utilisateur EST VIDE ALORS
        RETOURNER Erreur {
            code: "TOKEN_01",
            message: "Token invalide ou expiré"
        }
    
    3. SI utilisateur.actif = True ALORS  // ← VÉRIFICATION NOUVEAU
        RETOURNER Erreur {
            code: "ACTIVATION_01",
            message: "Compte déjà activé"
        }
    
    4. // Vérifier que les mots de passe correspondent
        SI mot_de_passe != confirmation_mot_de_passe ALORS
        RETOURNER Erreur {
            code: "PASSWORD_01",
            message: "Les mots de passe ne correspondent pas"
        }
    
    5. // Hacher le mot de passe
        mot_de_passe_hache = hacher_mot_de_passe(mot_de_passe)
    
    6. // Activer le compte
        UPDATE utilisateur SET 
            mot_de_passe = mot_de_passe_hache,
            actif = True,
            mot_de_passe_temporaire = False,  // ← PAS de mot de passe temporaire
            token_activation = NULL,
            date_expiration_token = NULL
        WHERE identifiant = utilisateur.identifiant
    
    7. // Générer token JWT pour la première connexion
        token_jwt = generer_token_jwt(utilisateur)
    
        RETOURNER {
            statut: "SUCCESS",
            message: "Compte activé avec succès. Vous pouvez maintenant vous connecter.",
            token: token_jwt,
            utilisateur: {
                identifiant: utilisateur.identifiant,
                nom: utilisateur.nom,
                prenom: utilisateur.prenom,
                role: utilisateur.role,
                email: utilisateur.email
            }
        }
FIN ROUTE
```

## Diagramme de Flux Global

```mermaid
flowchart TD
    A[Démarrage de l'application] --> B{Compte DE existe?}
    B -->|Non| C[Créer compte DE par défaut avec mot_de_passe_temporaire=True]
    B -->|Oui| D[Application prête]
    
    D --> E[Utilisateur accède à la page de connexion]
    E --> F[Utilisateur saisi email et mot de passe]
    F --> G{Vérification des tentatives}
    G -->|Trop de tentatives| H[Afficher message d'attente]
    G -->|OK| I{Vérification des identifiants}
    I -->|Invalides| J[Enregistrer tentative échouée]
    I -->|Valides| K{Utilisateur actif?}
    K -->|Non| J
    K -->|Oui| L{DE avec mot de passe temporaire?}
    L -->|Oui| M[Générer token changement mot de passe]
    L -->|Non| N[Générer token JWT]
    M --> O[Rediriger vers page de changement de mot de passe]
    O --> P[Utilisateur change mot de passe]
    P --> Q[Mettre à jour mot de passe et mot_de_passe_temporaire=False]
    Q --> N
    N --> R[Utilisateur connecté]
    J --> H
    
    S[DE crée un compte étudiant/formateur] --> T[Créer compte inactif avec token]
    T --> U[Envoyer email d'activation]
    U --> V[Utilisateur clique sur lien d'activation]
    V --> W[Vérifier compte non déjà actif]
    W --> X[Utilisateur définit son mot de passe]
    X --> Y[Activer compte et générer token JWT]
    Y --> R
```

## Validations et Sécurité

### Validations:
1. **Email**: Doit être une chaîne non vide et valide
2. **Mot de passe**: Doit avoir au moins 8 caractères
3. **Token**: Doit être valide et non expiré
4. **Rôle**: Doit être l'un des rôles définis (DE, FORMATEUR, ETUDIANT)
5. **Tentatives**: Maximum 5 tentatives échouées toutes les 15 minutes

### Sécurité:
1. **Hachage**: Tous les mots de passe sont hachés avec bcrypt ou PBKDF2
2. **Tokens**: Tokens uniques générés pour chaque opération sensible
3. **Expiration**: 
   - Tokens d'activation: 72h
   - Tokens de changement: 24h
   - Tentatives bloquées: 15 minutes
4. **JWT**: Tokens signés pour l'authentification des sessions
5. **Protection contre les attaques**: Limitation des tentatives de connexion
6. **Champ dédié**: `mot_de_passe_temporaire` pour gérer l'état du mot de passe

## Structures de Données Utilisées

### Utilisateur
```
{
    identifiant: String (primary key),
    email: String (unique),
    mot_de_passe: String (haché),
    nom: String,
    prenom: String,
    role: Enum (DE, FORMATEUR, ETUDIANT),
    actif: Boolean,
    mot_de_passe_temporaire: Boolean,  // ← NOUVEAU
    date_creation: DateTime,
    token_activation: String (nullable),
    date_expiration_token: DateTime (nullable)
}
```

### TentativeConnexion
```
{
    id_tentative: String (primary key),
    email: String,
    date_tentative: DateTime,
    succes: Boolean
}
```

## Cas Particuliers

1. **DE sans Formateur**: Le DE est un utilisateur de rôle "DE" sans entrée dans la table Formateur
2. **Compte inactif**: Les comptes créés par le DE sont inactifs jusqu'à activation
3. **Mot de passe temporaire**: Le DE a un mot de passe par défaut marqué par `mot_de_passe_temporaire = True`
4. **Connexion par email uniquement**: La route `/login` n'accepte que l'email, pas l'identifiant
5. **Limitation des tentatives**: Protection contre les attaques par force brute

## Améliorations par rapport à la Version 2

1. **🔒 Sécurité renforcée**: Ajout de la table `TentativeConnexion` pour limiter les tentatives
2. **✅ Détection fiable**: Utilisation du champ `mot_de_passe_temporaire` au lieu de comparaison de hash
3. **🎯 Simplification**: Route `/login` n'accepte que l'email (comme utilisé par l'interface)
4. **🛡️ Protection**: Vérification que le compte n'est pas déjà actif avant activation
5. **📊 Traçabilité**: Enregistrement de toutes les tentatives de connexion (réussies et échouées)
