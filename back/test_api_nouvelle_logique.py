#!/usr/bin/env python3
"""
Test de l'API avec la nouvelle logique de promotions automatiques
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from models import Utilisateur, RoleEnum
from core.auth import generer_token_jwt
from utils.promotion_generator import lister_annees_disponibles

def simuler_requete_creation_etudiant():
    """Simule une requête de création d'étudiant via l'API"""
    db = SessionLocal()
    
    try:
        print("=== Simulation requête API création étudiant ===")
        
        # 1. Simuler l'authentification du DE
        print("\n--- Authentification DE ---")
        de = db.query(Utilisateur).filter(Utilisateur.role == RoleEnum.DE).first()
        if not de:
            print("❌ Aucun compte DE trouvé")
            return False
        
        print(f"✅ DE trouvé: {de.email}")
        
        # 2. Lister les années disponibles (comme le ferait le frontend)
        print("\n--- Années académiques disponibles ---")
        annees = lister_annees_disponibles()
        for i, annee in enumerate(annees):
            print(f"  {i+1}. {annee}")
        
        # 3. Simuler les données de création d'étudiant
        print("\n--- Données de création étudiant ---")
        etudiant_data = {
            "email": "nouveau.etudiant@example.com",
            "nom": "Durand",
            "prenom": "Marie",
            "annee_academique": "2024-2025"  # Le DE sélectionne juste l'année
        }
        
        print(f"Email: {etudiant_data['email']}")
        print(f"Nom: {etudiant_data['nom']}")
        print(f"Prénom: {etudiant_data['prenom']}")
        print(f"Année académique: {etudiant_data['annee_academique']}")
        
        # 4. Simuler la logique de la route (sans FastAPI)
        print("\n--- Simulation logique route ---")
        
        # Import des fonctions nécessaires
        from utils.promotion_generator import valider_annee_academique, generer_promotion_automatique
        from utils.generators import generer_identifiant_unique, generer_mot_de_passe_aleatoire, generer_matricule_unique
        from core.jwt import get_password_hash
        from models import Etudiant, StatutEtudiantEnum
        from datetime import datetime
        
        # Validation email
        email_existant = db.query(Utilisateur).filter(Utilisateur.email == etudiant_data['email']).first()
        if email_existant:
            print("⚠️  Email existe déjà, suppression pour le test...")
            etudiant_existant = db.query(Etudiant).filter(Etudiant.identifiant == email_existant.identifiant).first()
            if etudiant_existant:
                db.delete(etudiant_existant)
            db.delete(email_existant)
            db.commit()
        
        # Validation année académique
        if not valider_annee_academique(etudiant_data['annee_academique']):
            print("❌ Année académique invalide")
            return False
        print("✅ Année académique valide")
        
        # Génération automatique de la promotion
        promotion = generer_promotion_automatique(db, etudiant_data['annee_academique'])
        print(f"✅ Promotion générée/trouvée: {promotion.libelle}")
        
        # Génération des données étudiant
        identifiant = generer_identifiant_unique("ETUDIANT")
        mot_de_passe = generer_mot_de_passe_aleatoire()
        id_etudiant = generer_identifiant_unique("ETUDIANT")
        matricule = generer_matricule_unique()
        
        # Création utilisateur
        nouvel_utilisateur = Utilisateur(
            identifiant=identifiant,
            email=etudiant_data['email'],
            mot_de_passe=get_password_hash(mot_de_passe),
            nom=etudiant_data['nom'],
            prenom=etudiant_data['prenom'],
            role=RoleEnum.ETUDIANT,
            actif=True,
            token_activation=None,
            date_expiration_token=None,
            mot_de_passe_temporaire=True
        )
        
        # Création étudiant
        nouvel_etudiant = Etudiant(
            id_etudiant=id_etudiant,
            identifiant=identifiant,
            matricule=matricule,
            id_promotion=promotion.id_promotion,
            date_inscription=datetime.now().date(),
            statut=StatutEtudiantEnum.ACTIF
        )
        
        # Sauvegarde
        db.add(nouvel_utilisateur)
        db.add(nouvel_etudiant)
        db.commit()
        db.refresh(nouvel_utilisateur)
        db.refresh(nouvel_etudiant)
        
        print("✅ Étudiant créé avec succès!")
        
        # Simulation envoi email
        from utils.email_service import email_service
        email_envoye = email_service.envoyer_email_creation_compte(
            destinataire=etudiant_data['email'],
            prenom=etudiant_data['prenom'],
            email=etudiant_data['email'],
            mot_de_passe=mot_de_passe,
            role="ETUDIANT"
        )
        
        # 5. Résultat final (comme retourné par l'API)
        print("\n--- Résultat API simulé ---")
        resultat = {
            "message": "Compte étudiant créé avec succès",
            "email_envoye": email_envoye,
            "identifiant": identifiant,
            "id_etudiant": id_etudiant,
            "matricule": matricule,
            "promotion": {
                "id_promotion": promotion.id_promotion,
                "libelle": promotion.libelle,
                "annee_academique": promotion.annee_academique
            },
            "identifiants_connexion": {
                "email": etudiant_data['email'],
                "mot_de_passe": mot_de_passe
            }
        }
        
        print(f"✅ Message: {resultat['message']}")
        print(f"✅ Email envoyé: {resultat['email_envoye']}")
        print(f"✅ Identifiant: {resultat['identifiant']}")
        print(f"✅ Matricule: {resultat['matricule']}")
        print(f"✅ Promotion: {resultat['promotion']['libelle']}")
        print(f"✅ Identifiants de connexion:")
        print(f"   - Email: {resultat['identifiants_connexion']['email']}")
        print(f"   - Mot de passe: {resultat['identifiants_connexion']['mot_de_passe']}")
        
        return resultat
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    print("🚀 Test de l'API avec promotions automatiques")
    
    resultat = simuler_requete_creation_etudiant()
    
    if resultat:
        print("\n🎉 Test API réussi!")
        print("\n📋 Résumé:")
        print("- Le DE sélectionne seulement l'année académique")
        print("- La promotion est générée automatiquement")
        print("- L'étudiant reçoit ses identifiants par email")
        print("- L'étudiant peut se connecter immédiatement")
        print("- À la première connexion, il devra changer son mot de passe")
    else:
        print("\n❌ Test API échoué")

if __name__ == "__main__":
    main()