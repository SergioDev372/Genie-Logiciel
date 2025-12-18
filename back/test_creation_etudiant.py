#!/usr/bin/env python3
"""
Script de test pour la création d'étudiant
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
DE_EMAIL = "de@genielogiciel.com"
DE_PASSWORD = "admin123"

def se_connecter_de():
    """Se connecter en tant que DE"""
    print("=== Connexion DE ===")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": DE_EMAIL,
        "mot_de_passe": DE_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["statut"] == "SUCCESS":
            print("✅ Connexion DE réussie")
            return data["token"]
        else:
            print(f"⚠️  Changement de mot de passe requis: {data}")
            return None
    else:
        print(f"❌ Erreur connexion: {response.status_code} - {response.text}")
        return None

def creer_etudiant(token, promotion_id):
    """Créer un étudiant de test"""
    print("\n=== Création étudiant ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    etudiant_data = {
        "email": "etudiant.test@example.com",
        "nom": "Dupont",
        "prenom": "Jean",
        "id_promotion": promotion_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/gestion-comptes/creer-etudiant",
        headers=headers,
        json=etudiant_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        data = response.json()
        print("✅ Étudiant créé avec succès!")
        print(f"   Identifiant: {data['identifiant']}")
        print(f"   ID étudiant: {data['id_etudiant']}")
        print(f"   Matricule: {data['matricule']}")
        print(f"   Email envoyé: {data['email_envoye']}")
        return data
    else:
        print(f"❌ Erreur création étudiant: {response.text}")
        return None

def main():
    # 1. Se connecter en tant que DE
    token = se_connecter_de()
    if not token:
        print("❌ Impossible de se connecter en tant que DE")
        return
    
    # 2. Utiliser l'ID de promotion créé précédemment
    promotion_id = "USR_1766068050_7585"  # ID de la promotion créée
    
    # 3. Créer un étudiant
    etudiant = creer_etudiant(token, promotion_id)
    
    if etudiant:
        print("\n=== Test réussi ===")
        print("L'étudiant peut maintenant se connecter avec:")
        print(f"Email: etudiant.test@example.com")
        print("Mot de passe: (voir l'email ou les logs)")

if __name__ == "__main__":
    main()