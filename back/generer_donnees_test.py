#!/usr/bin/env python3
"""
Script pour générer des données de test réalistes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from database.database import SessionLocal
from models import (
    Formation, Promotion, Utilisateur, Formateur, Etudiant, 
    RoleEnum, StatutEtudiantEnum
)
from core.jwt import get_password_hash
from utils.generators import (
    generer_identifiant_unique, generer_mot_de_passe_aleatoire,
    generer_matricule_unique, generer_numero_employe
)
from utils.promotion_generator import generer_promotion_automatique

def generer_donnees_test():
    """Génère des données de test réalistes"""
    db = SessionLocal()
    
    try:
        print("=== Génération de données de test ===")
        
        # 1. Créer plusieurs formations
        formations_data = [
            {
                "nom": "Développement Web Full Stack",
                "description": "Formation complète en développement web moderne (React, Node.js, Python)"
            },
            {
                "nom": "Data Science et Intelligence Artificielle", 
                "description": "Formation en analyse de données, machine learning et IA"
            },
            {
                "nom": "Cybersécurité et Réseaux",
                "description": "Formation en sécurité informatique et administration réseaux"
            },
            {
                "nom": "Développement Mobile",
                "description": "Formation en développement d'applications mobiles (iOS, Android, Flutter)"
            }
        ]
        
        formations_creees = []
        for form_data in formations_data:
            # Vérifier si existe déjà
            formation_existante = db.query(Formation).filter(
                Formation.nom_formation == form_data["nom"]
            ).first()
            
            if not formation_existante:
                formation_id = generer_identifiant_unique("FORMATION")
                formation = Formation(
                    id_formation=formation_id,
                    nom_formation=form_data["nom"],
                    description=form_data["description"],
                    date_debut=date(2024, 9, 1),
                    date_fin=date(2025, 6, 30)
                )
                db.add(formation)
                formations_creees.append(formation)
                print(f"✅ Formation créée: {form_data['nom']}")
            else:
                formations_creees.append(formation_existante)
                print(f"ℹ️  Formation existante: {form_data['nom']}")
        
        db.commit()
        
        # 2. Créer des promotions pour différentes années
        annees_academiques = ["2023-2024", "2024-2025", "2025-2026"]
        promotions_creees = []
        
        for annee in annees_academiques:
            for formation in formations_creees:
                try:
                    # Utiliser le générateur automatique
                    promotion = generer_promotion_automatique(db, annee)
                    if promotion not in promotions_creees:
                        promotions_creees.append(promotion)
                        print(f"✅ Promotion générée: {promotion.libelle}")
                except Exception as e:
                    print(f"⚠️  Erreur génération promotion {annee}: {e}")
        
        # 3. Créer des formateurs
        formateurs_data = [
            {"nom": "Martin", "prenom": "Jean", "email": "jean.martin@genielogiciel.com", "specialite": "Développement Web"},
            {"nom": "Dubois", "prenom": "Marie", "email": "marie.dubois@genielogiciel.com", "specialite": "Data Science"},
            {"nom": "Leroy", "prenom": "Pierre", "email": "pierre.leroy@genielogiciel.com", "specialite": "Cybersécurité"},
            {"nom": "Bernard", "prenom": "Sophie", "email": "sophie.bernard@genielogiciel.com", "specialite": "Développement Mobile"},
            {"nom": "Petit", "prenom": "Luc", "email": "luc.petit@genielogiciel.com", "specialite": "Base de données"},
            {"nom": "Moreau", "prenom": "Claire", "email": "claire.moreau@genielogiciel.com", "specialite": "UX/UI Design"}
        ]
        
        formateurs_crees = 0
        for form_data in formateurs_data:
            # Vérifier si existe déjà
            utilisateur_existant = db.query(Utilisateur).filter(
                Utilisateur.email == form_data["email"]
            ).first()
            
            if not utilisateur_existant:
                # Créer utilisateur
                identifiant = generer_identifiant_unique("FORMATEUR")
                mot_de_passe = generer_mot_de_passe_aleatoire()
                
                utilisateur = Utilisateur(
                    identifiant=identifiant,
                    email=form_data["email"],
                    mot_de_passe=get_password_hash(mot_de_passe),
                    nom=form_data["nom"],
                    prenom=form_data["prenom"],
                    role=RoleEnum.FORMATEUR,
                    actif=True,
                    mot_de_passe_temporaire=False  # Comptes de test activés
                )
                
                # Créer formateur
                id_formateur = generer_identifiant_unique("FORMATEUR")
                formateur = Formateur(
                    id_formateur=id_formateur,
                    identifiant=identifiant,
                    numero_employe=generer_numero_employe(),
                    specialite=form_data["specialite"]
                )
                
                db.add(utilisateur)
                db.add(formateur)
                formateurs_crees += 1
                print(f"✅ Formateur créé: {form_data['prenom']} {form_data['nom']} ({form_data['specialite']})")
        
        db.commit()
        
        # 4. Créer des étudiants
        etudiants_data = [
            {"nom": "Dupont", "prenom": "Alice", "email": "alice.dupont@student.com"},
            {"nom": "Durand", "prenom": "Bob", "email": "bob.durand@student.com"},
            {"nom": "Lemoine", "prenom": "Camille", "email": "camille.lemoine@student.com"},
            {"nom": "Rousseau", "prenom": "David", "email": "david.rousseau@student.com"},
            {"nom": "Vincent", "prenom": "Emma", "email": "emma.vincent@student.com"},
            {"nom": "Fournier", "prenom": "Felix", "email": "felix.fournier@student.com"},
            {"nom": "Girard", "prenom": "Gabrielle", "email": "gabrielle.girard@student.com"},
            {"nom": "Andre", "prenom": "Hugo", "email": "hugo.andre@student.com"},
            {"nom": "Lefebvre", "prenom": "Iris", "email": "iris.lefebvre@student.com"},
            {"nom": "Simon", "prenom": "Jules", "email": "jules.simon@student.com"},
            {"nom": "Michel", "prenom": "Lea", "email": "lea.michel@student.com"},
            {"nom": "Garcia", "prenom": "Maxime", "email": "maxime.garcia@student.com"},
            {"nom": "David", "prenom": "Nina", "email": "nina.david@student.com"},
            {"nom": "Bertrand", "prenom": "Oscar", "email": "oscar.bertrand@student.com"},
            {"nom": "Roux", "prenom": "Pauline", "email": "pauline.roux@student.com"}
        ]
        
        etudiants_crees = 0
        # Répartir les étudiants sur les promotions disponibles
        for i, etud_data in enumerate(etudiants_data):
            # Vérifier si existe déjà
            utilisateur_existant = db.query(Utilisateur).filter(
                Utilisateur.email == etud_data["email"]
            ).first()
            
            if not utilisateur_existant and promotions_creees:
                # Sélectionner une promotion (rotation)
                promotion = promotions_creees[i % len(promotions_creees)]
                
                # Créer utilisateur
                identifiant = generer_identifiant_unique("ETUDIANT")
                mot_de_passe = generer_mot_de_passe_aleatoire()
                
                utilisateur = Utilisateur(
                    identifiant=identifiant,
                    email=etud_data["email"],
                    mot_de_passe=get_password_hash(mot_de_passe),
                    nom=etud_data["nom"],
                    prenom=etud_data["prenom"],
                    role=RoleEnum.ETUDIANT,
                    actif=True,
                    mot_de_passe_temporaire=False  # Comptes de test activés
                )
                
                # Créer étudiant
                id_etudiant = generer_identifiant_unique("ETUDIANT")
                etudiant = Etudiant(
                    id_etudiant=id_etudiant,
                    identifiant=identifiant,
                    matricule=generer_matricule_unique(),
                    id_promotion=promotion.id_promotion,
                    date_inscription=datetime.now().date(),
                    statut=StatutEtudiantEnum.ACTIF
                )
                
                db.add(utilisateur)
                db.add(etudiant)
                etudiants_crees += 1
                print(f"✅ Étudiant créé: {etud_data['prenom']} {etud_data['nom']} → {promotion.libelle}")
        
        db.commit()
        
        # 5. Résumé final
        print(f"\n=== Résumé de la génération ===")
        print(f"✅ Formations: {len(formations_creees)}")
        print(f"✅ Promotions: {len(promotions_creees)}")
        print(f"✅ Formateurs créés: {formateurs_crees}")
        print(f"✅ Étudiants créés: {etudiants_crees}")
        
        # Statistiques finales
        total_formateurs = db.query(Formateur).count()
        total_etudiants = db.query(Etudiant).count()
        total_promotions = db.query(Promotion).count()
        total_formations = db.query(Formation).count()
        
        print(f"\n=== Statistiques finales ===")
        print(f"📊 Total formateurs: {total_formateurs}")
        print(f"📊 Total étudiants: {total_etudiants}")
        print(f"📊 Total promotions: {total_promotions}")
        print(f"📊 Total formations: {total_formations}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    generer_donnees_test()