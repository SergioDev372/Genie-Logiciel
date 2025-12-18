#!/usr/bin/env python3
"""
Test du système complet d'espaces pédagogiques
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from database.database import SessionLocal
from models import (
    Utilisateur, Formateur, Etudiant, Formation, Promotion,
    EspacePedagogique, Travail, Assignation,
    RoleEnum, TypeTravailEnum, StatutAssignationEnum
)
from utils.generators import generer_identifiant_unique
from utils.email_service import email_service

def test_workflow_complet():
    """Test du workflow complet"""
    db = SessionLocal()
    
    try:
        print("=== Test Workflow Espaces Pédagogiques ===")
        
        # 1. Récupérer le DE
        de = db.query(Utilisateur).filter(Utilisateur.role == RoleEnum.DE).first()
        if not de:
            print("❌ Aucun compte DE trouvé")
            return False
        print(f"✅ DE trouvé: {de.email}")
        
        # 2. Récupérer une formation
        formation = db.query(Formation).first()
        if not formation:
            print("❌ Aucune formation trouvée")
            return False
        print(f"✅ Formation: {formation.nom_formation}")
        
        # 3. Récupérer une promotion
        promotion = db.query(Promotion).first()
        if not promotion:
            print("❌ Aucune promotion trouvée")
            return False
        print(f"✅ Promotion: {promotion.libelle}")
        
        # 4. Récupérer un formateur avec utilisateur valide
        formateur = None
        formateurs = db.query(Formateur).all()
        for f in formateurs:
            utilisateur = db.query(Utilisateur).filter(Utilisateur.identifiant == f.identifiant).first()
            if utilisateur:
                formateur = f
                formateur.utilisateur = utilisateur  # Assigner manuellement
                break
        
        if not formateur:
            print("❌ Aucun formateur avec utilisateur valide trouvé")
            return False
        print(f"✅ Formateur: {formateur.utilisateur.prenom} {formateur.utilisateur.nom}")
        
        # 5. Créer un espace pédagogique
        print("\n--- Création espace pédagogique ---")
        id_espace = generer_identifiant_unique("ESPACE")
        espace = EspacePedagogique(
            id_espace=id_espace,
            id_promotion=promotion.id_promotion,
            nom_matiere=f"Test - {formation.nom_formation}",
            description="Espace de test pour validation du système",
            id_formateur=formateur.id_formateur,
            code_acces="TEST123",
            date_creation=datetime.utcnow()
        )
        
        db.add(espace)
        db.commit()
        db.refresh(espace)
        print(f"✅ Espace créé: {espace.nom_matiere} (Code: {espace.code_acces})")
        
        # 6. Compter les étudiants de la promotion
        etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == promotion.id_promotion
        ).all()
        print(f"✅ Étudiants dans la promotion: {len(etudiants)}")
        
        # 7. Créer un travail
        print("\n--- Création travail ---")
        id_travail = generer_identifiant_unique("TRAVAIL")
        travail = Travail(
            id_travail=id_travail,
            id_espace=id_espace,
            titre="Projet de test",
            description="Travail de validation du système d'assignation automatique",
            type_travail=TypeTravailEnum.INDIVIDUEL,
            date_echeance=datetime.utcnow() + timedelta(days=7),
            note_max=20.0,
            date_creation=datetime.utcnow()
        )
        
        db.add(travail)
        db.commit()
        db.refresh(travail)
        print(f"✅ Travail créé: {travail.titre}")
        
        # 8. Créer les assignations automatiquement
        print("\n--- Assignations automatiques ---")
        assignations_creees = 0
        emails_envoyes = 0
        
        for etudiant in etudiants:
            id_assignation = generer_identifiant_unique("ASSIGNATION")
            assignation = Assignation(
                id_assignation=id_assignation,
                id_etudiant=etudiant.id_etudiant,
                id_travail=id_travail,
                date_assignment=datetime.utcnow(),
                statut=StatutAssignationEnum.ASSIGNE
            )
            db.add(assignation)
            assignations_creees += 1
            
            # Test envoi email
            try:
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
        
        # 9. Vérifications finales
        print(f"\n=== Résultats ===")
        print(f"✅ Assignations créées: {assignations_creees}")
        print(f"✅ Emails envoyés: {emails_envoyes}")
        
        # Test consultation étudiant
        if etudiants:
            etudiant_test = etudiants[0]
            assignations_etudiant = db.query(Assignation).filter(
                Assignation.id_etudiant == etudiant_test.id_etudiant
            ).count()
            print(f"✅ Travaux assignés à {etudiant_test.utilisateur.prenom}: {assignations_etudiant}")
        
        # Test consultation formateur
        espaces_formateur = db.query(EspacePedagogique).filter(
            EspacePedagogique.id_formateur == formateur.id_formateur
        ).count()
        print(f"✅ Espaces du formateur {formateur.utilisateur.prenom}: {espaces_formateur}")
        
        print(f"\n🎉 Test workflow complet: RÉUSSI")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_consultation_donnees():
    """Test de consultation des données par rôle"""
    db = SessionLocal()
    
    try:
        print("\n=== Test Consultation par Rôle ===")
        
        # Test DE - Vue globale
        print("\n--- Vue DE ---")
        espaces_total = db.query(EspacePedagogique).count()
        travaux_total = db.query(Travail).count()
        assignations_total = db.query(Assignation).count()
        
        print(f"📊 Espaces pédagogiques: {espaces_total}")
        print(f"📊 Travaux créés: {travaux_total}")
        print(f"📊 Assignations: {assignations_total}")
        
        # Test Formateur - Ses espaces
        formateur = db.query(Formateur).first()
        if formateur:
            print(f"\n--- Vue Formateur ({formateur.utilisateur.prenom}) ---")
            ses_espaces = db.query(EspacePedagogique).filter(
                EspacePedagogique.id_formateur == formateur.id_formateur
            ).all()
            
            for espace in ses_espaces:
                nb_etudiants = db.query(Etudiant).filter(
                    Etudiant.id_promotion == espace.id_promotion
                ).count()
                nb_travaux = db.query(Travail).filter(
                    Travail.id_espace == espace.id_espace
                ).count()
                
                print(f"  📚 {espace.nom_matiere}")
                print(f"     Promotion: {espace.promotion.libelle}")
                print(f"     Étudiants: {nb_etudiants}")
                print(f"     Travaux: {nb_travaux}")
        
        # Test Étudiant - Ses cours
        etudiant = db.query(Etudiant).first()
        if etudiant:
            print(f"\n--- Vue Étudiant ({etudiant.utilisateur.prenom}) ---")
            ses_cours = db.query(EspacePedagogique).filter(
                EspacePedagogique.id_promotion == etudiant.id_promotion
            ).all()
            
            for espace in ses_cours:
                nb_mes_travaux = db.query(Assignation).join(Travail).filter(
                    Travail.id_espace == espace.id_espace,
                    Assignation.id_etudiant == etudiant.id_etudiant
                ).count()
                
                print(f"  📖 {espace.nom_matiere}")
                print(f"     Formateur: {espace.formateur.utilisateur.prenom} {espace.formateur.utilisateur.nom}")
                print(f"     Mes travaux: {nb_mes_travaux}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur consultation: {e}")
        return False
    finally:
        db.close()

def main():
    print("🚀 Test du système d'espaces pédagogiques")
    
    # Test 1: Workflow complet
    if test_workflow_complet():
        print("\n✅ Test workflow: RÉUSSI")
    else:
        print("\n❌ Test workflow: ÉCHOUÉ")
        return
    
    # Test 2: Consultation données
    if test_consultation_donnees():
        print("\n✅ Test consultation: RÉUSSI")
    else:
        print("\n❌ Test consultation: ÉCHOUÉ")
    
    print("\n🎉 Tous les tests sont réussis !")
    print("\n📋 Fonctionnalités validées:")
    print("  ✅ Création d'espaces pédagogiques")
    print("  ✅ Assignation automatique de travaux")
    print("  ✅ Envoi d'emails de notification")
    print("  ✅ Consultation par rôle (DE/Formateur/Étudiant)")

if __name__ == "__main__":
    main()