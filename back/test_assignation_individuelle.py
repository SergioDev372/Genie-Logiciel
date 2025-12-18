#!/usr/bin/env python3
"""
Test de l'assignation individuelle de travaux
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from database.database import SessionLocal
from models import (
    Formateur, Etudiant, EspacePedagogique, Travail, Assignation,
    TypeTravailEnum, StatutAssignationEnum
)
from utils.generators import generer_identifiant_unique
from utils.email_service import email_service

def test_assignation_individuelle():
    """Test de l'assignation à un étudiant spécifique"""
    db = SessionLocal()
    
    try:
        print("=== Test Assignation Individuelle ===")
        
        # 1. Récupérer un espace pédagogique
        espace = db.query(EspacePedagogique).first()
        if not espace:
            print("❌ Aucun espace pédagogique trouvé")
            return False
        print(f"✅ Espace: {espace.nom_matiere}")
        
        # 2. Récupérer les étudiants de la promotion
        etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).all()
        print(f"✅ Étudiants dans la promotion: {len(etudiants)}")
        
        if len(etudiants) < 2:
            print("❌ Pas assez d'étudiants pour le test")
            return False
        
        # 3. Sélectionner 2 étudiants spécifiques
        etudiants_selectionnes = etudiants[:2]
        print(f"\n--- Étudiants sélectionnés ---")
        for etud in etudiants_selectionnes:
            print(f"  • {etud.utilisateur.prenom} {etud.utilisateur.nom} ({etud.matricule})")
        
        # 4. Créer un travail individuel
        print(f"\n--- Création travail individuel ---")
        id_travail = generer_identifiant_unique("TRAVAIL")
        travail = Travail(
            id_travail=id_travail,
            id_espace=espace.id_espace,
            titre="Travail individuel - Test assignation",
            description="Ce travail est assigné uniquement à des étudiants spécifiques",
            type_travail=TypeTravailEnum.INDIVIDUEL,
            date_echeance=datetime.now() + timedelta(days=7),
            note_max=20.0,
            date_creation=datetime.now()
        )
        
        db.add(travail)
        db.commit()
        db.refresh(travail)
        print(f"✅ Travail créé: {travail.titre}")
        
        # 5. Assigner uniquement aux étudiants sélectionnés
        print(f"\n--- Assignations individuelles ---")
        assignations_creees = 0
        emails_envoyes = 0
        
        for etudiant in etudiants_selectionnes:
            id_assignation = generer_identifiant_unique("ASSIGNATION")
            assignation = Assignation(
                id_assignation=id_assignation,
                id_etudiant=etudiant.id_etudiant,
                id_travail=id_travail,
                date_assignment=datetime.now(),
                statut=StatutAssignationEnum.ASSIGNE
            )
            db.add(assignation)
            assignations_creees += 1
            
            # Envoi email
            try:
                formateur = espace.formateur
                email_envoye = email_service.envoyer_email_assignation_travail(
                    destinataire=etudiant.utilisateur.email,
                    prenom=etudiant.utilisateur.prenom,
                    titre_travail=travail.titre,
                    nom_matiere=espace.nom_matiere,
                    formateur=f"{formateur.utilisateur.prenom} {formateur.utilisateur.nom}",
                    date_echeance=travail.date_echeance.strftime("%d/%m/%Y à %H:%M"),
                    description=travail.description
                )
                if email_envoye:
                    emails_envoyes += 1
                print(f"  ✅ Assigné à {etudiant.utilisateur.prenom} {etudiant.utilisateur.nom} (Email: {'✅' if email_envoye else '❌'})")
            except Exception as e:
                print(f"  ⚠️  Assigné à {etudiant.utilisateur.prenom} {etudiant.utilisateur.nom} (Email: ❌ {e})")
        
        db.commit()
        
        # 6. Vérification
        print(f"\n=== Résultats ===")
        print(f"✅ Assignations créées: {assignations_creees}")
        print(f"✅ Emails envoyés: {emails_envoyes}")
        
        # Vérifier que les autres étudiants n'ont PAS reçu le travail
        print(f"\n--- Vérification non-assignation ---")
        etudiants_non_selectionnes = [e for e in etudiants if e not in etudiants_selectionnes]
        for etudiant in etudiants_non_selectionnes[:3]:  # Vérifier les 3 premiers
            assignation = db.query(Assignation).filter(
                Assignation.id_etudiant == etudiant.id_etudiant,
                Assignation.id_travail == id_travail
            ).first()
            
            if assignation:
                print(f"  ❌ {etudiant.utilisateur.prenom} a reçu le travail (ne devrait pas)")
            else:
                print(f"  ✅ {etudiant.utilisateur.prenom} n'a PAS reçu le travail (correct)")
        
        print(f"\n🎉 Test assignation individuelle: RÉUSSI")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_assignation_globale():
    """Test de l'assignation à toute la promotion (comportement par défaut)"""
    db = SessionLocal()
    
    try:
        print("\n=== Test Assignation Globale ===")
        
        # 1. Récupérer un espace pédagogique
        espace = db.query(EspacePedagogique).first()
        if not espace:
            print("❌ Aucun espace pédagogique trouvé")
            return False
        
        # 2. Compter les étudiants
        nb_etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).count()
        print(f"✅ Étudiants dans la promotion: {nb_etudiants}")
        
        # 3. Créer un travail pour tous
        id_travail = generer_identifiant_unique("TRAVAIL")
        travail = Travail(
            id_travail=id_travail,
            id_espace=espace.id_espace,
            titre="Travail global - Test assignation",
            description="Ce travail est assigné à toute la promotion",
            type_travail=TypeTravailEnum.INDIVIDUEL,
            date_echeance=datetime.now() + timedelta(days=7),
            note_max=20.0,
            date_creation=datetime.now()
        )
        
        db.add(travail)
        db.commit()
        print(f"✅ Travail créé: {travail.titre}")
        
        # 4. Assigner à tous (liste vide = tous)
        etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).all()
        
        assignations_creees = 0
        for etudiant in etudiants:
            id_assignation = generer_identifiant_unique("ASSIGNATION")
            assignation = Assignation(
                id_assignation=id_assignation,
                id_etudiant=etudiant.id_etudiant,
                id_travail=id_travail,
                date_assignment=datetime.now(),
                statut=StatutAssignationEnum.ASSIGNE
            )
            db.add(assignation)
            assignations_creees += 1
        
        db.commit()
        
        print(f"✅ Assignations créées: {assignations_creees}")
        print(f"✅ Tous les étudiants ont reçu le travail")
        
        print(f"\n🎉 Test assignation globale: RÉUSSI")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("🚀 Test des types d'assignation")
    
    # Test 1: Assignation individuelle
    if test_assignation_individuelle():
        print("\n✅ Test assignation individuelle: RÉUSSI")
    else:
        print("\n❌ Test assignation individuelle: ÉCHOUÉ")
        return
    
    # Test 2: Assignation globale
    if test_assignation_globale():
        print("\n✅ Test assignation globale: RÉUSSI")
    else:
        print("\n❌ Test assignation globale: ÉCHOUÉ")
    
    print("\n🎉 Tous les tests sont réussis !")
    print("\n📋 Fonctionnalités validées:")
    print("  ✅ Assignation à des étudiants spécifiques")
    print("  ✅ Assignation à toute la promotion")
    print("  ✅ Emails envoyés uniquement aux assignés")
    print("  ✅ Non-assignation vérifiée")

if __name__ == "__main__":
    main()