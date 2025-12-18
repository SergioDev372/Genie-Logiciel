#!/usr/bin/env python3
"""
Test de connexion d'un étudiant créé
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from models import Utilisateur, TentativeConnexion
from core.auth import verifier_tentatives_connexion, generer_token_jwt
from core.jwt import verify_password, get_password_hash
from datetime import datetime, timedelta

def test_connexion_etudiant(email, mot_de_passe):
    """Test de connexion d'un étudiant"""
    db = SessionLocal()
    
    try:
        print(f"=== Test connexion étudiant ===")
        print(f"Email: {email}")
        print(f"Mot de passe: {mot_de_passe}")
        
        # 1. Vérifier les tentatives de connexion
        print("\n--- Vérification tentatives ---")
        erreur_tentatives = verifier_tentatives_connexion(db, email)
        if erreur_tentatives:
            print(f"❌ Trop de tentatives: {erreur_tentatives}")
            return False
        print("✅ Tentatives OK")
        
        # 2. Rechercher l'utilisateur
        print("\n--- Recherche utilisateur ---")
        utilisateur = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        
        if not utilisateur:
            print("❌ Utilisateur non trouvé")
            return False
        
        print(f"✅ Utilisateur trouvé: {utilisateur.nom} {utilisateur.prenom}")
        print(f"   Identifiant: {utilisateur.identifiant}")
        print(f"   Role: {utilisateur.role}")
        print(f"   Actif: {utilisateur.actif}")
        print(f"   Mot de passe temporaire: {utilisateur.mot_de_passe_temporaire}")
        
        # 3. Vérifier si actif
        if not utilisateur.actif:
            print("❌ Compte inactif")
            return False
        print("✅ Compte actif")
        
        # 4. Vérifier le mot de passe
        print("\n--- Vérification mot de passe ---")
        print(f"Mot de passe fourni: {mot_de_passe}")
        print(f"Hash en base: {utilisateur.mot_de_passe[:20]}...")
        
        # Désactiver temporairement les logs de debug
        import builtins
        original_print = builtins.print
        def silent_print(*args, **kwargs):
            if not any("Debug:" in str(arg) for arg in args):
                original_print(*args, **kwargs)
        builtins.print = silent_print
        
        verification = verify_password(mot_de_passe, utilisateur.mot_de_passe)
        
        builtins.print = original_print
        
        if not verification:
            print("❌ Mot de passe incorrect")
            # Enregistrer tentative échouée
            tentative = TentativeConnexion(
                email=email,
                succes=False
            )
            db.add(tentative)
            db.commit()
            return False
        
        print("✅ Mot de passe correct")
        
        # 5. Enregistrer tentative réussie
        tentative = TentativeConnexion(
            email=email,
            succes=True
        )
        db.add(tentative)
        db.commit()
        
        # 6. Vérifier si changement de mot de passe requis
        print("\n--- Vérification mot de passe temporaire ---")
        if utilisateur.mot_de_passe_temporaire:
            print("⚠️  Changement de mot de passe requis")
            
            # Générer token pour changement
            from core.auth import generer_token_unique
            token = generer_token_unique(32)
            date_expiration = datetime.utcnow() + timedelta(hours=24)
            
            utilisateur.token_activation = token
            utilisateur.date_expiration_token = date_expiration
            db.commit()
            
            resultat = {
                "statut": "CHANGEMENT_MOT_DE_PASSE_REQUIS",
                "token": token,
                "utilisateur": {
                    "identifiant": utilisateur.identifiant,
                    "nom": utilisateur.nom,
                    "prenom": utilisateur.prenom,
                    "role": utilisateur.role,
                    "email": utilisateur.email
                }
            }
            
            print("✅ Token de changement généré")
            print(f"   Token: {token[:20]}...")
            return resultat
        else:
            print("✅ Connexion normale")
            
            # Générer token JWT
            token_jwt = generer_token_jwt({
                "identifiant": utilisateur.identifiant,
                "email": utilisateur.email,
                "nom": utilisateur.nom,
                "prenom": utilisateur.prenom,
                "role": utilisateur.role
            })
            
            resultat = {
                "statut": "SUCCESS",
                "token": token_jwt,
                "utilisateur": {
                    "identifiant": utilisateur.identifiant,
                    "nom": utilisateur.nom,
                    "prenom": utilisateur.prenom,
                    "role": utilisateur.role,
                    "email": utilisateur.email
                }
            }
            
            print("✅ Token JWT généré")
            return resultat
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    # Utiliser les identifiants de l'étudiant créé précédemment
    email = "etudiant.test2@example.com"
    mot_de_passe = "LE0LAPOE"  # Remplacer par le mot de passe généré
    
    resultat = test_connexion_etudiant(email, mot_de_passe)
    
    if resultat:
        print(f"\n=== Résultat final ===")
        print(f"Statut: {resultat['statut']}")
        if resultat['statut'] == "CHANGEMENT_MOT_DE_PASSE_REQUIS":
            print("🔄 L'étudiant doit changer son mot de passe")
            print("   Il peut utiliser le token pour changer son mot de passe")
        else:
            print("🎉 Connexion réussie!")
            print("   L'étudiant peut utiliser l'API avec son token JWT")

if __name__ == "__main__":
    main()