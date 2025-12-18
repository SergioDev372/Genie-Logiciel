#!/usr/bin/env python3
"""
Test direct de création d'étudiant (sans API)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from models import Utilisateur, Etudiant, Promotion, RoleEnum, StatutEtudiantEnum
from core.jwt import get_password_hash
from utils.generators import generer_identifiant_unique, generer_mot_de_passe_aleatoire, generer_matricule_unique
from utils.email_service import email_service
from datetime import datetime

def test_creation_etudiant():
    """Test direct de création d'étudiant"""
    db = SessionLocal()
    
    try:
        print("=== Test création étudiant direct ===")
        
        # 1. Vérifier qu'une promotion existe
        promotion = db.query(Promotion).first()
        if not promotion:
            print("❌ Aucune promotion trouvée. Exécutez d'abord init_donnees_test.py")
            return
        
        print(f"✅ Promotion trouvée: {promotion.libelle} (ID: {promotion.id_promotion})")
        
        # 2. Données de l'étudiant
        email_etudiant = "etudiant.test2@example.com"
        
        # Vérifier si l'email existe déjà
        email_existant = db.query(Utilisateur).filter(Utilisateur.email == email_etudiant).first()
        if email_existant:
            print(f"⚠️  Email {email_etudiant} existe déjà, suppression...")
            # Supprimer l'étudiant existant
            etudiant_existant = db.query(Etudiant).filter(Etudiant.identifiant == email_existant.identifiant).first()
            if etudiant_existant:
                db.delete(etudiant_existant)
            db.delete(email_existant)
            db.commit()
        
        # 3. Génération automatique
        identifiant = generer_identifiant_unique("ETUDIANT")
        mot_de_passe = generer_mot_de_passe_aleatoire()
        id_etudiant = generer_identifiant_unique("ETUDIANT")
        matricule = generer_matricule_unique()
        
        print(f"Identifiant: {identifiant}")
        print(f"Mot de passe: {mot_de_passe}")
        print(f"ID étudiant: {id_etudiant}")
        print(f"Matricule: {matricule}")
        
        # 4. Création utilisateur
        nouvel_utilisateur = Utilisateur(
            identifiant=identifiant,
            email=email_etudiant,
            mot_de_passe=get_password_hash(mot_de_passe),
            nom="Dupont",
            prenom="Jean",
            role=RoleEnum.ETUDIANT,
            actif=True,
            token_activation=None,
            date_expiration_token=None,
            mot_de_passe_temporaire=True
        )
        
        # 5. Création étudiant
        nouvel_etudiant = Etudiant(
            id_etudiant=id_etudiant,
            identifiant=identifiant,
            matricule=matricule,
            id_promotion=promotion.id_promotion,
            date_inscription=datetime.utcnow().date(),
            statut=StatutEtudiantEnum.ACTIF
        )
        
        # 6. Sauvegarde
        db.add(nouvel_utilisateur)
        db.add(nouvel_etudiant)
        db.commit()
        db.refresh(nouvel_utilisateur)
        db.refresh(nouvel_etudiant)
        
        print("✅ Étudiant créé avec succès!")
        
        # 7. Test envoi email
        print("\n=== Test envoi email ===")
        email_envoye = email_service.envoyer_email_creation_compte(
            destinataire=email_etudiant,
            prenom="Jean",
            email=email_etudiant,
            mot_de_passe=mot_de_passe,
            role="ETUDIANT"
        )
        
        if email_envoye:
            print("✅ Email envoyé avec succès")
        else:
            print("⚠️  Email non envoyé (voir logs)")
        
        # 8. Test de vérification du mot de passe
        print("\n=== Test vérification mot de passe ===")
        from core.jwt import verify_password
        hash_mdp = nouvel_utilisateur.mot_de_passe
        verification = verify_password(mot_de_passe, hash_mdp)
        print(f"Mot de passe: {mot_de_passe}")
        print(f"Hash: {hash_mdp[:20]}...")
        print(f"Vérification: {'✅ OK' if verification else '❌ ERREUR'}")
        
        print(f"\n=== Informations de connexion ===")
        print(f"Email: {email_etudiant}")
        print(f"Mot de passe: {mot_de_passe}")
        print(f"L'étudiant peut maintenant se connecter!")
        
        return {
            "email": email_etudiant,
            "mot_de_passe": mot_de_passe,
            "identifiant": identifiant,
            "matricule": matricule
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    test_creation_etudiant()