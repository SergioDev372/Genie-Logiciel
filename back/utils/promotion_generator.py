#!/usr/bin/env python3
"""
Générateur automatique de promotions
"""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from models import Formation, Promotion
from utils.generators import generer_identifiant_unique


def generer_annee_academique(annee: int) -> str:
    """Génère une année académique au format YYYY-YYYY"""
    return f"{annee}-{annee + 1}"


def lister_annees_disponibles() -> List[str]:
    """Liste les années académiques disponibles (passée, courante, future)"""
    annee_courante = datetime.now().year
    
    # Si on est après juin, on considère qu'on est dans l'année suivante
    if datetime.now().month >= 7:  # Juillet = début nouvelle année académique
        annee_courante += 1
    
    annees = []
    for i in range(-1, 3):  # 4 années: précédente, courante, +1, +2
        annee = annee_courante + i
        annees.append(generer_annee_academique(annee))
    
    return annees


def obtenir_formation_par_defaut(db: Session) -> Formation:
    """Obtient ou crée la formation par défaut"""
    
    # Chercher une formation existante
    formation = db.query(Formation).first()
    
    if formation:
        return formation
    
    # Créer une formation par défaut
    formation_id = generer_identifiant_unique("FORMATION")
    formation = Formation(
        id_formation=formation_id,
        nom_formation="Formation Générale",
        description="Formation générale pour tous les étudiants",
        date_debut=date(2024, 9, 1),
        date_fin=None  # Formation permanente
    )
    
    db.add(formation)
    db.commit()
    db.refresh(formation)
    
    return formation


def generer_promotion_automatique(db: Session, annee_academique: str) -> Promotion:
    """
    Génère automatiquement une promotion pour une année académique donnée
    
    Args:
        db: Session de base de données
        annee_academique: Format "YYYY-YYYY" (ex: "2024-2025")
    
    Returns:
        Promotion: La promotion créée ou existante
    """
    
    # 1. Vérifier si la promotion existe déjà
    promotion_existante = db.query(Promotion).filter(
        Promotion.annee_academique == annee_academique
    ).first()
    
    if promotion_existante:
        return promotion_existante
    
    # 2. Obtenir la formation par défaut
    formation = obtenir_formation_par_defaut(db)
    
    # 3. Extraire les années de l'année académique
    try:
        annee_debut, annee_fin = annee_academique.split("-")
        annee_debut = int(annee_debut)
        annee_fin = int(annee_fin)
    except ValueError:
        raise ValueError(f"Format d'année académique invalide: {annee_academique}. Utilisez YYYY-YYYY")
    
    # 4. Générer les dates
    date_debut = date(annee_debut, 9, 1)  # 1er septembre
    date_fin = date(annee_fin, 6, 30)     # 30 juin
    
    # 5. Créer la promotion
    promotion_id = generer_identifiant_unique("PROMOTION")
    promotion = Promotion(
        id_promotion=promotion_id,
        id_formation=formation.id_formation,
        annee_academique=annee_academique,
        libelle=f"Promotion {annee_academique}",
        date_debut=date_debut,
        date_fin=date_fin
    )
    
    # 6. Sauvegarder
    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    
    return promotion


def valider_annee_academique(annee_academique: str) -> bool:
    """Valide le format d'une année académique"""
    try:
        annee_debut, annee_fin = annee_academique.split("-")
        annee_debut = int(annee_debut)
        annee_fin = int(annee_fin)
        
        # Vérifier que l'année de fin est l'année de début + 1
        if annee_fin != annee_debut + 1:
            return False
        
        # Vérifier que les années sont raisonnables (entre 2020 et 2050)
        if annee_debut < 2020 or annee_debut > 2050:
            return False
        
        return True
    except (ValueError, AttributeError):
        return False


def lister_promotions_existantes(db: Session) -> List[dict]:
    """Liste toutes les promotions existantes avec leurs informations"""
    promotions = db.query(Promotion).order_by(Promotion.annee_academique.desc()).all()
    
    result = []
    for promotion in promotions:
        result.append({
            "id_promotion": promotion.id_promotion,
            "annee_academique": promotion.annee_academique,
            "libelle": promotion.libelle,
            "date_debut": promotion.date_debut.isoformat(),
            "date_fin": promotion.date_fin.isoformat(),
            "formation": promotion.formation.nom_formation if promotion.formation else "N/A"
        })
    
    return result