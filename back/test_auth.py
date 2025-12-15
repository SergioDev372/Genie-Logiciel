#!/usr/bin/env python3
"""
Test script pour vérifier le système d'authentification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, engine
from models import Base, Utilisateur, TentativeConnexion, RoleEnum
from core.auth import initialiser_compte_de
from datetime import datetime, timedelta

def test_initialiser_compte_de():
    """Test de la fonction initialiser_compte_de"""
    print("Test de initialiser_compte_de...")
    
    # Créer une session de base de données
    db = SessionLocal()
    
    try:
        # Vérifier si le compte DE existe déjà
        de_existant = db.query(Utilisateur).filter(Utilisateur.role == RoleEnum.DE).first()
        if de_existant:
            print(f"Compte DE existant trouvé: {de_existant.email}")
        
        # Appeler la fonction
        resultat = initialiser_compte_de(db)
        
        if resultat:
            print(f"✓ Compte DE initialisé avec succès:")
            print(f"  - Email: {resultat['email']}")
            print(f"  - Nom: {resultat['nom']}")
            print(f"  - Prénom: {resultat['prenom']}")
            print(f"  - Rôle: {resultat['role']}")
            print(f"  - Mot de passe temporaire: {resultat['mot_de_passe_temporaire']}")
        else:
            print("✗ Échec de l'initialisation du compte DE")
            
    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
    finally:
        db.close()

def test_database_connection():
    """Test de la connexion à la base de données"""
    print("\nTest de la connexion à la base de données...")
    
    try:
        db = SessionLocal()
        # Essayer d'exécuter une simple requête
        result = db.execute("SELECT 1").fetchone()
        if result:
            print("✓ Connexion à la base de données réussie")
        else:
            print("✗ Connexion à la base de données échouée")
    except Exception as e:
        print(f"✗ Erreur de connexion: {e}")
    finally:
        db.close()

def test_models():
    """Test de la création des modèles"""
    print("\nTest de la création des modèles...")
    
    try:
        # Vérifier si les tables existent
        inspector = engine.inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['utilisateur', 'tentative_connexion']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"✗ Tables manquantes: {missing_tables}")
        else:
            print("✓ Toutes les tables requises existent")
            
    except Exception as e:
        print(f"✗ Erreur lors de la vérification des modèles: {e}")

if __name__ == "__main__":
    print("=== Test du système d'authentification ===")
    
    # Test de la connexion à la base de données
    test_database_connection()
    
    # Test de la création des modèles
    test_models()
    
    # Test de l'initialisation du compte DE
    test_initialiser_compte_de()
    
    print("\n=== Tests terminés ===")