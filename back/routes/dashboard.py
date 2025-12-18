from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
from datetime import datetime, date

from database.database import get_db
from models import (
    Utilisateur, Formateur, Etudiant, Promotion, Formation, 
    EspacePedagogique, Travail, Assignation, Livraison,
    RoleEnum, StatutEtudiantEnum, StatutAssignationEnum
)
from core.auth import get_current_user
from utils.promotion_generator import lister_annees_disponibles

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# ==================== DASHBOARD DE ====================

@router.get("/de")
async def dashboard_de(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Dashboard du Directeur d'Établissement"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au Directeur d'Établissement"
        )
    
    # Statistiques globales
    total_formateurs = db.query(Formateur).count()
    total_etudiants = db.query(Etudiant).count()
    total_promotions = db.query(Promotion).count()
    total_formations = db.query(Formation).count()
    
    # Étudiants par statut
    etudiants_actifs = db.query(Etudiant).filter(Etudiant.statut == StatutEtudiantEnum.ACTIF).count()
    etudiants_suspendus = db.query(Etudiant).filter(Etudiant.statut == StatutEtudiantEnum.SUSPENDU).count()
    
    # Promotions récentes
    promotions_recentes = db.query(Promotion).order_by(desc(Promotion.date_debut)).limit(5).all()
    
    # Années académiques disponibles
    annees_disponibles = lister_annees_disponibles()
    
    # Activité récente (derniers comptes créés)
    comptes_recents = db.query(Utilisateur).filter(
        Utilisateur.role.in_([RoleEnum.FORMATEUR, RoleEnum.ETUDIANT])
    ).order_by(desc(Utilisateur.date_creation)).limit(10).all()
    
    return {
        "role": "DE",
        "utilisateur": {
            "nom": current_user.nom,
            "prenom": current_user.prenom,
            "email": current_user.email
        },
        "statistiques": {
            "total_formateurs": total_formateurs,
            "total_etudiants": total_etudiants,
            "total_promotions": total_promotions,
            "total_formations": total_formations,
            "etudiants_actifs": etudiants_actifs,
            "etudiants_suspendus": etudiants_suspendus
        },
        "promotions_recentes": [
            {
                "id_promotion": p.id_promotion,
                "libelle": p.libelle,
                "annee_academique": p.annee_academique,
                "date_debut": p.date_debut.isoformat(),
                "date_fin": p.date_fin.isoformat()
            } for p in promotions_recentes
        ],
        "annees_disponibles": annees_disponibles,
        "comptes_recents": [
            {
                "identifiant": u.identifiant,
                "nom": u.nom,
                "prenom": u.prenom,
                "email": u.email,
                "role": u.role,
                "date_creation": u.date_creation.isoformat(),
                "actif": u.actif
            } for u in comptes_recents
        ],
        "actions_disponibles": [
            "creer_formateur",
            "creer_etudiant",
            "gerer_promotions",
            "voir_statistiques",
            "configurer_systeme"
        ]
    }

# ==================== DASHBOARD FORMATEUR ====================

@router.get("/formateur")
async def dashboard_formateur(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Dashboard du Formateur"""
    
    if current_user.role != RoleEnum.FORMATEUR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux formateurs"
        )
    
    # Récupérer le profil formateur
    formateur = db.query(Formateur).filter(Formateur.identifiant == current_user.identifiant).first()
    if not formateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil formateur non trouvé"
        )
    
    # Mes espaces pédagogiques
    espaces = db.query(EspacePedagogique).filter(
        EspacePedagogique.id_formateur == formateur.id_formateur
    ).all()
    
    # Statistiques des espaces
    total_espaces = len(espaces)
    total_travaux = 0
    total_etudiants = set()
    
    espaces_data = []
    for espace in espaces:
        # Compter les travaux de cet espace
        travaux_espace = db.query(Travail).filter(Travail.id_espace == espace.id_espace).count()
        total_travaux += travaux_espace
        
        # Compter les étudiants de la promotion
        etudiants_promotion = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).all()
        
        for etudiant in etudiants_promotion:
            total_etudiants.add(etudiant.id_etudiant)
        
        espaces_data.append({
            "id_espace": espace.id_espace,
            "nom_matiere": espace.nom_matiere,
            "description": espace.description,
            "promotion": espace.promotion.libelle if espace.promotion else "N/A",
            "nombre_travaux": travaux_espace,
            "nombre_etudiants": len(etudiants_promotion),
            "code_acces": espace.code_acces,
            "date_creation": espace.date_creation.isoformat()
        })
    
    # Travaux récents
    travaux_recents = db.query(Travail).join(EspacePedagogique).filter(
        EspacePedagogique.id_formateur == formateur.id_formateur
    ).order_by(desc(Travail.date_creation)).limit(5).all()
    
    # Assignations en attente de correction
    assignations_a_corriger = db.query(Assignation).join(Travail).join(EspacePedagogique).filter(
        EspacePedagogique.id_formateur == formateur.id_formateur,
        Assignation.statut == StatutAssignationEnum.RENDU
    ).count()
    
    return {
        "role": "FORMATEUR",
        "utilisateur": {
            "nom": current_user.nom,
            "prenom": current_user.prenom,
            "email": current_user.email,
            "numero_employe": formateur.numero_employe,
            "specialite": formateur.specialite
        },
        "statistiques": {
            "total_espaces": total_espaces,
            "total_travaux": total_travaux,
            "total_etudiants": len(total_etudiants),
            "assignations_a_corriger": assignations_a_corriger
        },
        "espaces_pedagogiques": espaces_data,
        "travaux_recents": [
            {
                "id_travail": t.id_travail,
                "titre": t.titre,
                "type_travail": t.type_travail,
                "date_echeance": t.date_echeance.isoformat(),
                "espace": t.espace_pedagogique.nom_matiere,
                "date_creation": t.date_creation.isoformat()
            } for t in travaux_recents
        ],
        "actions_disponibles": [
            "creer_espace_pedagogique",
            "creer_travail",
            "corriger_travaux",
            "gerer_etudiants",
            "voir_statistiques"
        ]
    }

# ==================== DASHBOARD ETUDIANT ====================

@router.get("/etudiant")
async def dashboard_etudiant(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Dashboard de l'Étudiant"""
    
    if current_user.role != RoleEnum.ETUDIANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux étudiants"
        )
    
    # Récupérer le profil étudiant
    etudiant = db.query(Etudiant).filter(Etudiant.identifiant == current_user.identifiant).first()
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil étudiant non trouvé"
        )
    
    # Mes assignations (travaux)
    assignations = db.query(Assignation).filter(
        Assignation.id_etudiant == etudiant.id_etudiant
    ).all()
    
    # Statistiques des travaux
    total_travaux = len(assignations)
    travaux_termines = len([a for a in assignations if a.statut == StatutAssignationEnum.RENDU])
    travaux_notes = len([a for a in assignations if a.statut == StatutAssignationEnum.NOTE])
    travaux_en_cours = len([a for a in assignations if a.statut == StatutAssignationEnum.EN_COURS])
    travaux_en_retard = 0
    
    # Mes espaces pédagogiques (cours)
    espaces = db.query(EspacePedagogique).filter(
        EspacePedagogique.id_promotion == etudiant.id_promotion
    ).all()
    
    # Travaux récents et à venir
    travaux_data = []
    for assignation in assignations:
        travail = assignation.travail
        
        # Vérifier si en retard
        if travail.date_echeance < datetime.now() and assignation.statut != StatutAssignationEnum.RENDU:
            travaux_en_retard += 1
        
        # Récupérer la note si disponible
        note = None
        if assignation.livraisons:
            derniere_livraison = max(assignation.livraisons, key=lambda l: l.date_livraison)
            note = derniere_livraison.note_attribuee
        
        travaux_data.append({
            "id_assignation": assignation.id_assignation,
            "titre": travail.titre,
            "description": travail.description,
            "type_travail": travail.type_travail,
            "date_echeance": travail.date_echeance.isoformat(),
            "statut": assignation.statut,
            "espace": travail.espace_pedagogique.nom_matiere,
            "formateur": f"{travail.espace_pedagogique.formateur.utilisateur.prenom} {travail.espace_pedagogique.formateur.utilisateur.nom}",
            "note": float(note) if note else None,
            "note_max": float(travail.note_max),
            "en_retard": travail.date_echeance < datetime.now() and assignation.statut != StatutAssignationEnum.RENDU
        })
    
    # Trier par date d'échéance
    travaux_data.sort(key=lambda x: x["date_echeance"])
    
    # Mes notes (moyenne)
    notes = [t["note"] for t in travaux_data if t["note"] is not None]
    moyenne = sum(notes) / len(notes) if notes else None
    
    return {
        "role": "ETUDIANT",
        "utilisateur": {
            "nom": current_user.nom,
            "prenom": current_user.prenom,
            "email": current_user.email,
            "matricule": etudiant.matricule,
            "statut": etudiant.statut,
            "date_inscription": etudiant.date_inscription.isoformat()
        },
        "promotion": {
            "libelle": etudiant.promotion.libelle,
            "annee_academique": etudiant.promotion.annee_academique,
            "formation": etudiant.promotion.formation.nom_formation
        },
        "statistiques": {
            "total_travaux": total_travaux,
            "travaux_termines": travaux_termines,
            "travaux_notes": travaux_notes,
            "travaux_en_cours": travaux_en_cours,
            "travaux_en_retard": travaux_en_retard,
            "moyenne_generale": round(moyenne, 2) if moyenne else None
        },
        "espaces_pedagogiques": [
            {
                "id_espace": e.id_espace,
                "nom_matiere": e.nom_matiere,
                "description": e.description,
                "formateur": f"{e.formateur.utilisateur.prenom} {e.formateur.utilisateur.nom}" if e.formateur and e.formateur.utilisateur else "Non assigné",
                "code_acces": e.code_acces
            } for e in espaces
        ],
        "travaux": travaux_data[:10],  # Les 10 plus récents
        "actions_disponibles": [
            "voir_travaux",
            "rendre_travail",
            "consulter_notes",
            "modifier_profil"
        ]
    }

# ==================== ROUTE GÉNÉRIQUE ====================

@router.get("/")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Route générique qui redirige vers le bon dashboard selon le rôle"""
    
    if current_user.role == RoleEnum.DE:
        return await dashboard_de(db, current_user)
    elif current_user.role == RoleEnum.FORMATEUR:
        return await dashboard_formateur(db, current_user)
    elif current_user.role == RoleEnum.ETUDIANT:
        return await dashboard_etudiant(db, current_user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rôle utilisateur non reconnu"
        )