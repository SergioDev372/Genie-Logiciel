#!/usr/bin/env python3
"""
Test du système de génération automatique de promotions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from models import Utilisateur, Etudiant, Promotion, Formation, RoleEnum, StatutEtudiantEnum
from core.jwt import get_password_hash
from utils.generators import generer_identifiant_unique, generer_mot_de_passe_aleatoire, generer_matricule_unique
from utils.promotion_generator import (
    generer_promotion_automatique,
    lister_annees_disponibles,
    valider_annee_academique,
    lister_promotions_existantes
)
from utils.email_service import email_service
from datetime import datetime

def test_generation_promotions():
    """Test de génération automatique de promotions"""
    db = SessionLocal()
    
    try:
        print("=== Test génération automatique de promotions ===")
        
        # 1. Lister les années disponibles
        print("\n--- Années académiques disponibles ---")
        annees = lister_annees_disponibles()
        for annee in annees:
            print(f"  - {annee}")
        
        # 2. Tester la validation d'années
        print("\n--- Test validation années ---")
        annees_test = ["2024-2025", "2023-2024", "2025-2026", "2024-2026", "invalid", "2024"]
        for annee in annees_test:
            valide = valider_annee_academique(annee)
            print(f"  {annee}: {'✅ Valide' if valide else '❌ Invalide'}")
        
        # 3. Générer des promotions pour différentes années
        print("\n--- Génération de promotions ---")
        annees_a_generer = ["2024-2025", "2025-2026", "2023-2024"]
        
        for annee in annees_a_generer:
            print(f"\nGénération pour {annee}:")
            promotion = generer_promotion_automatique(db, annee)
            print(f"  ✅ Promotion créée/trouvée:")
            print(f"     ID: {promotion.id_promotion}")
            print(f"     Libellé: {promotion.libelle}")
            print(f"     Date début: {promotion.date_debut}")
            print(f"     Date fin: {promotion.date_fin}")
            print(f"     Formation: {promotion.formation.nom_formation}")
        
        # 4. Lister toutes les promotions
        print("\n--- Toutes les promotions ---")
        promotions = lister_promotions_existantes(db)
        for promo in promotions:
            print(f"  - {promo['annee_academique']}: {promo['libelle']}")
            print(f"    ID: {promo['id_promotion']}")
            print(f"    Période: {promo['date_debut']} → {promo['date_fin']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_creation_etudiant_avec_annee():
    """Test de création d'étudiant avec année académique"""
    db = SessionLocal()
    
    try:
        print("\n=== Test création étudiant avec année académique ===")
        
        # Données de l'étudiant
        email_etudiant = "etudiant.annee@example.com"
        annee_academique = "2024-2025"
        
        # Supprimer l'étudiant s'il existe déjà
        email_existant = db.query(Utilisateur).filter(Utilisateur.email == email_etudiant).first()
        if email_existant:
            print(f"⚠️  Suppression de l'étudiant existant...")
            etudiant_existant = db.query(Etudiant).filter(Etudiant.identifiant == email_existant.identifiant).first()
            if etudiant_existant:
                db.delete(etudiant_existant)
            db.delete(email_existant)
            db.commit()
        
        # 1. Valider l'année académique
        if not valider_annee_academique(annee_academique):
            print(f"❌ Année académique invalide: {annee_academique}")
            return False
        print(f"✅ Année académique valide: {annee_academique}")
        
        # 2. Générer la promotion automatiquement
        promotion = generer_promotion_automatique(db, annee_academique)
        print(f"✅ Promotion générée: {promotion.libelle} (ID: {promotion.id_promotion})")
        
        # 3. Créer l'étudiant
        identifiant = generer_identifiant_unique("ETUDIANT")
        mot_de_passe = generer_mot_de_passe_aleatoire()
        id_etudiant = generer_identifiant_unique("ETUDIANT")
        matricule = generer_matricule_unique()
        
        nouvel_utilisateur = Utilisateur(
            identifiant=identifiant,
            email=email_etudiant,
            mot_de_passe=get_password_hash(mot_de_passe),
            nom="Martin",
            prenom="Sophie",
            role=RoleEnum.ETUDIANT,
            actif=True,
            token_activation=None,
            date_expiration_token=None,
            mot_de_passe_temporaire=True
        )
        
        nouvel_etudiant = Etudiant(
            id_etudiant=id_etudiant,
            identifiant=identifiant,
            matricule=matricule,
            id_promotion=promotion.id_promotion,  # Utiliser l'ID de la promotion générée
            date_inscription=datetime.now().date(),
            statut=StatutEtudiantEnum.ACTIF
        )
        
        db.add(nouvel_utilisateur)
        db.add(nouvel_etudiant)
        db.commit()
        db.refresh(nouvel_utilisateur)
        db.refresh(nouvel_etudiant)
        
        print("✅ Étudiant créé avec succès!")
        print(f"   Email: {email_etudiant}")
        print(f"   Mot de passe: {mot_de_passe}")
        print(f"   Matricule: {matricule}")
        print(f"   Promotion: {promotion.libelle}")
        print(f"   Année académique: {annee_academique}")
        
        return {
            "email": email_etudiant,
            "mot_de_passe": mot_de_passe,
            "promotion": promotion.libelle,
            "annee_academique": annee_academique
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    print("🚀 Test du système de promotions automatiques")
    
    # Test 1: Génération de promotions
    if test_generation_promotions():
        print("\n✅ Test génération promotions: RÉUSSI")
    else:
        print("\n❌ Test génération promotions: ÉCHOUÉ")
        return
    
    # Test 2: Création d'étudiant avec année
    resultat = test_creation_etudiant_avec_annee()
    if resultat:
        print("\n✅ Test création étudiant: RÉUSSI")
        print(f"\n🎯 L'étudiant peut se connecter avec:")
        print(f"   Email: {resultat['email']}")
        print(f"   Mot de passe: {resultat['mot_de_passe']}")
        print(f"   Il sera automatiquement assigné à: {resultat['promotion']}")
    else:
        print("\n❌ Test création étudiant: ÉCHOUÉ")

if __name__ == "__main__":
    main()