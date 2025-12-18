#!/usr/bin/env python3
"""
Script pour initialiser des données de test (formations et promotions)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from database.database import SessionLocal
from models import Formation, Promotion
from utils.generators import generer_identifiant_unique

def creer_donnees_test():
    """Crée des formations et promotions de test"""
    db = SessionLocal()
    
    try:
        print("=== Création des données de test ===")
        
        # 1. Créer une formation de test
        formation_id = generer_identifiant_unique("FORMATION")
        formation = Formation(
            id_formation=formation_id,
            nom_formation="Développement Web Full Stack",
            description="Formation complète en développement web moderne",
            date_debut=date(2024, 9, 1),
            date_fin=date(2025, 6, 30)
        )
        
        # Vérifier si la formation existe déjà
        formation_existante = db.query(Formation).filter(
            Formation.nom_formation == formation.nom_formation
        ).first()
        
        if not formation_existante:
            db.add(formation)
            db.commit()
            db.refresh(formation)
            print(f"✅ Formation créée: {formation.nom_formation} (ID: {formation.id_formation})")
        else:
            formation = formation_existante
            print(f"ℹ️  Formation existante: {formation.nom_formation} (ID: {formation.id_formation})")
        
        # 2. Créer une promotion de test
        promotion_id = generer_identifiant_unique("PROMOTION")
        promotion = Promotion(
            id_promotion=promotion_id,
            id_formation=formation.id_formation,
            annee_academique="2024-2025",
            libelle="Promotion 2024-2025 - Développement Web",
            date_debut=date(2024, 9, 1),
            date_fin=date(2025, 6, 30)
        )
        
        # Vérifier si la promotion existe déjà
        promotion_existante = db.query(Promotion).filter(
            Promotion.id_formation == formation.id_formation,
            Promotion.annee_academique == "2024-2025"
        ).first()
        
        if not promotion_existante:
            db.add(promotion)
            db.commit()
            db.refresh(promotion)
            print(f"✅ Promotion créée: {promotion.libelle} (ID: {promotion.id_promotion})")
        else:
            promotion = promotion_existante
            print(f"ℹ️  Promotion existante: {promotion.libelle} (ID: {promotion.id_promotion})")
        
        # 3. Afficher les informations pour les tests
        print("\n=== Informations pour les tests ===")
        print(f"Formation ID: {formation.id_formation}")
        print(f"Promotion ID: {promotion.id_promotion}")
        print(f"Nom formation: {formation.nom_formation}")
        print(f"Libellé promotion: {promotion.libelle}")
        
        # 4. Lister toutes les promotions disponibles
        print("\n=== Toutes les promotions disponibles ===")
        toutes_promotions = db.query(Promotion).all()
        for p in toutes_promotions:
            print(f"- {p.id_promotion}: {p.libelle}")
        
        return {
            "formation_id": formation.id_formation,
            "promotion_id": promotion.id_promotion
        }
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    creer_donnees_test()