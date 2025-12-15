"""
Script pour recréer complètement la base de données avec tentative_connexion
"""

from database.database import engine
from sqlalchemy import text
import datetime

def recreate_database_schema():
    print("=== Recréation complète du schéma de la base de données ===\n")
    
    try:
        with engine.connect() as connection:
            # 1. Supprimer toutes les tables existantes
            print("1. Suppression des tables existantes...")
            
            # Obtenir la liste des tables
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            # Supprimer les tables dans le bon ordre (respect des contraintes de clé étrangère)
            tables_to_drop = [
                'livraison', 'assignation', 'groupe_etudiant', 'travail',
                'espace_pedagogique', 'etudiant', 'formateur', 'promotion',
                'formation', 'utilisateur', 'tentative_connexion'
            ]
            
            for table in tables_to_drop:
                if table in tables:
                    connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    print(f"   ✓ Table {table} supprimée")
            
            # 2. Créer la table tentative_connexion (pour la sécurité)
            print("\n2. Création de la table tentative_connexion...")
            connection.execute(text("""
                CREATE TABLE tentative_connexion (
                    id_tentative VARCHAR(100) PRIMARY KEY,
                    email VARCHAR(191) NOT NULL,
                    date_tentative DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    succes BOOLEAN NOT NULL DEFAULT FALSE
                )
            """))
            print("   ✓ Table tentative_connexion créée")
            
            # 3. Créer la table utilisateur avec le nouveau schéma
            print("\n3. Création de la table utilisateur...")
            connection.execute(text("""
                CREATE TABLE utilisateur (
                    identifiant VARCHAR(100) PRIMARY KEY,
                    email VARCHAR(191) UNIQUE NOT NULL,
                    mot_de_passe VARCHAR(255) NOT NULL,
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100) NOT NULL,
                    role ENUM('DE', 'FORMATEUR', 'ETUDIANT') NOT NULL,
                    actif BOOLEAN NOT NULL DEFAULT TRUE,
                    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    token_activation VARCHAR(255),
                    date_expiration_token DATETIME,
                    mot_de_passe_temporaire BOOLEAN NOT NULL DEFAULT FALSE
                )
            """))
            print("   ✓ Table utilisateur créée")
            
            # 4. Créer la table formation
            print("\n4. Création de la table formation...")
            connection.execute(text("""
                CREATE TABLE formation (
                    id_formation VARCHAR(100) PRIMARY KEY,
                    nom_formation VARCHAR(191) UNIQUE NOT NULL,
                    description TEXT,
                    date_debut DATE NOT NULL,
                    date_fin DATE
                )
            """))
            print("   ✓ Table formation créée")
            
            # 5. Créer la table promotion
            print("\n5. Création de la table promotion...")
            connection.execute(text("""
                CREATE TABLE promotion (
                    id_promotion VARCHAR(100) PRIMARY KEY,
                    id_formation VARCHAR(100) NOT NULL,
                    annee_academique VARCHAR(20) NOT NULL,
                    libelle VARCHAR(255) NOT NULL,
                    date_debut DATE NOT NULL,
                    date_fin DATE NOT NULL,
                    FOREIGN KEY (id_formation) REFERENCES formation(id_formation),
                    CONSTRAINT uq_promotion_formation_annee UNIQUE (id_formation, annee_academique)
                )
            """))
            print("   ✓ Table promotion créée")
            
            # 6. Créer la table formateur
            print("\n6. Création de la table formateur...")
            connection.execute(text("""
                CREATE TABLE formateur (
                    id_formateur VARCHAR(100) PRIMARY KEY,
                    identifiant VARCHAR(100) NOT NULL,
                    numero_employe VARCHAR(100),
                    specialite VARCHAR(255),
                    FOREIGN KEY (identifiant) REFERENCES utilisateur(identifiant),
                    CONSTRAINT uq_formateur_identifiant UNIQUE (identifiant)
                )
            """))
            print("   ✓ Table formateur créée")
            
            # 7. Créer la table etudiant
            print("\n7. Création de la table etudiant...")
            connection.execute(text("""
                CREATE TABLE etudiant (
                    id_etudiant VARCHAR(100) PRIMARY KEY,
                    identifiant VARCHAR(100) NOT NULL,
                    matricule VARCHAR(100) UNIQUE NOT NULL,
                    id_promotion VARCHAR(100) NOT NULL,
                    date_inscription DATE NOT NULL,
                    statut ENUM('ACTIF', 'SUSPENDU', 'EXCLU') NOT NULL DEFAULT 'ACTIF',
                    FOREIGN KEY (identifiant) REFERENCES utilisateur(identifiant),
                    FOREIGN KEY (id_promotion) REFERENCES promotion(id_promotion),
                    CONSTRAINT uq_etudiant_identifiant UNIQUE (identifiant)
                )
            """))
            print("   ✓ Table etudiant créée")
            
            # 8. Créer la table espace_pedagogique
            print("\n8. Création de la table espace_pedagogique...")
            connection.execute(text("""
                CREATE TABLE espace_pedagogique (
                    id_espace VARCHAR(100) PRIMARY KEY,
                    id_promotion VARCHAR(100) NOT NULL,
                    nom_matiere VARCHAR(255) NOT NULL,
                    description TEXT,
                    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    id_formateur VARCHAR(100) NOT NULL,
                    code_acces VARCHAR(100),
                    FOREIGN KEY (id_promotion) REFERENCES promotion(id_promotion),
                    FOREIGN KEY (id_formateur) REFERENCES formateur(id_formateur)
                )
            """))
            print("   ✓ Table espace_pedagogique créée")
            
            # 9. Créer la table travail
            print("\n9. Création de la table travail...")
            connection.execute(text("""
                CREATE TABLE travail (
                    id_travail VARCHAR(100) PRIMARY KEY,
                    id_espace VARCHAR(100) NOT NULL,
                    titre VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    type_travail ENUM('INDIVIDUEL', 'COLLECTIF') NOT NULL,
                    date_echeance DATETIME NOT NULL,
                    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    fichier_consigne VARCHAR(255),
                    note_max DECIMAL(3,1) NOT NULL DEFAULT 20.0,
                    FOREIGN KEY (id_espace) REFERENCES espace_pedagogique(id_espace)
                )
            """))
            print("   ✓ Table travail créée")
            
            # 10. Créer la table groupe_etudiant
            print("\n10. Création de la table groupe_etudiant...")
            connection.execute(text("""
                CREATE TABLE groupe_etudiant (
                    id_groupe VARCHAR(100) PRIMARY KEY,
                    id_travail VARCHAR(100) NOT NULL,
                    nom_groupe VARCHAR(255) NOT NULL,
                    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_travail) REFERENCES travail(id_travail)
                )
            """))
            print("   ✓ Table groupe_etudiant créée")
            
            # 11. Créer la table assignation
            print("\n11. Création de la table assignation...")
            connection.execute(text("""
                CREATE TABLE assignation (
                    id_assignation VARCHAR(100) PRIMARY KEY,
                    id_etudiant VARCHAR(100) NOT NULL,
                    id_travail VARCHAR(100) NOT NULL,
                    id_groupe VARCHAR(100),
                    date_assignment DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    statut ENUM('ASSIGNE', 'EN_COURS', 'RENDU', 'NOTE') NOT NULL DEFAULT 'ASSIGNE',
                    FOREIGN KEY (id_etudiant) REFERENCES etudiant(id_etudiant),
                    FOREIGN KEY (id_travail) REFERENCES travail(id_travail),
                    FOREIGN KEY (id_groupe) REFERENCES groupe_etudiant(id_groupe)
                )
            """))
            print("   ✓ Table assignation créée")
            
            # 12. Créer la table livraison
            print("\n12. Création de la table livraison...")
            connection.execute(text("""
                CREATE TABLE livraison (
                    id_livraison VARCHAR(100) PRIMARY KEY,
                    id_assignation VARCHAR(100) NOT NULL,
                    chemin_fichier VARCHAR(255) NOT NULL,
                    date_livraison DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    commentaire TEXT,
                    note_attribuee DECIMAL(3,1),
                    feedback TEXT,
                    FOREIGN KEY (id_assignation) REFERENCES assignation(id_assignation)
                )
            """))
            print("   ✓ Table livraison créée")
            
            # 13. Créer le compte DE par défaut
            print("\n13. Création du compte DE par défaut...")
            de_password_hash = "hashed_admin123_password"  # Dans un vrai cas, on utiliserait bcrypt
            connection.execute(text("""
                INSERT INTO utilisateur (identifiant, email, mot_de_passe, nom, prenom, role, actif, mot_de_passe_temporaire)
                VALUES ('de_principal', 'de@genielogiciel.com', :password, 'Directeur', 'Établissement', 'DE', TRUE, TRUE)
            """), {"password": de_password_hash})
            print("   ✓ Compte DE créé")
            
            print("\n=== Schéma de la base de données recréé avec succès ===")
            print("Toutes les tables ont été créées avec les bons types de champs (String pour les IDs)")
            print("Le compte DE a été créé avec mot_de_passe_temporaire = TRUE")
            print("La table tentative_connexion a été ajoutée pour la sécurité")
            print("Structure exactement conforme aux modèles Python + sécurité")
            
    except Exception as e:
        print(f"Erreur lors de la recréation du schéma: {e}")
        raise

if __name__ == "__main__":
    recreate_database_schema()