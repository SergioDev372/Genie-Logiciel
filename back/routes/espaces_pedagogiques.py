from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database.database import get_db
from models import (
    Utilisateur, Formateur, Etudiant, Formation, Promotion,
    EspacePedagogique, Travail, Assignation,
    RoleEnum, TypeTravailEnum, StatutAssignationEnum
)
from core.auth import get_current_user
from utils.generators import generer_identifiant_unique
from utils.email_service import email_service
import secrets

router = APIRouter(prefix="/api/espaces-pedagogiques", tags=["Espaces Pédagogiques"])

# ==================== SCHEMAS ====================

class EspacePedagogiqueCreate(BaseModel):
    id_formation: str
    id_promotion: str
    id_formateur: str
    nom_matiere: str
    description: Optional[str] = None

class TravailCreate(BaseModel):
    id_espace: str
    titre: str
    description: str
    type_travail: str  # "INDIVIDUEL" ou "COLLECTIF"
    date_echeance: str  # Format ISO
    note_max: float = 20.0
    etudiants_selectionnes: Optional[List[str]] = []  # Liste des id_etudiant (optionnel)

# ==================== ROUTES DE ====================

@router.post("/creer")
async def creer_espace_pedagogique(
    data: EspacePedagogiqueCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Créer un espace pédagogique (DE uniquement)"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le DE peut créer des espaces pédagogiques"
        )
    
    # Vérifier que la formation existe
    formation = db.query(Formation).filter(Formation.id_formation == data.id_formation).first()
    if not formation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formation non trouvée"
        )
    
    # Vérifier que la promotion existe
    promotion = db.query(Promotion).filter(Promotion.id_promotion == data.id_promotion).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion non trouvée"
        )
    
    # Vérifier que le formateur existe
    formateur = db.query(Formateur).filter(Formateur.id_formateur == data.id_formateur).first()
    if not formateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formateur non trouvé"
        )
    
    # Générer un code d'accès unique
    code_acces = secrets.token_urlsafe(6).upper()
    
    # Créer l'espace pédagogique
    id_espace = generer_identifiant_unique("ESPACE")
    espace = EspacePedagogique(
        id_espace=id_espace,
        id_promotion=data.id_promotion,
        nom_matiere=data.nom_matiere,
        description=data.description,
        id_formateur=data.id_formateur,
        code_acces=code_acces,
        date_creation=datetime.utcnow()
    )
    
    db.add(espace)
    db.commit()
    db.refresh(espace)
    
    # Compter les étudiants de la promotion
    nb_etudiants = db.query(Etudiant).filter(Etudiant.id_promotion == data.id_promotion).count()
    
    return {
        "message": "Espace pédagogique créé avec succès",
        "espace": {
            "id_espace": espace.id_espace,
            "nom_matiere": espace.nom_matiere,
            "description": espace.description,
            "code_acces": espace.code_acces,
            "formation": formation.nom_formation,
            "promotion": promotion.libelle,
            "formateur": f"{formateur.utilisateur.prenom} {formateur.utilisateur.nom}",
            "nb_etudiants": nb_etudiants
        }
    }

@router.get("/liste")
async def lister_espaces_pedagogiques(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lister tous les espaces pédagogiques (DE uniquement)"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé au DE"
        )
    
    espaces = db.query(EspacePedagogique).all()
    
    result = []
    for espace in espaces:
        nb_etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).count()
        
        nb_travaux = db.query(Travail).filter(
            Travail.id_espace == espace.id_espace
        ).count()
        
        result.append({
            "id_espace": espace.id_espace,
            "nom_matiere": espace.nom_matiere,
            "description": espace.description,
            "code_acces": espace.code_acces,
            "promotion": espace.promotion.libelle,
            "formation": espace.promotion.formation.nom_formation,
            "formateur": f"{espace.formateur.utilisateur.prenom} {espace.formateur.utilisateur.nom}",
            "nb_etudiants": nb_etudiants,
            "nb_travaux": nb_travaux,
            "date_creation": espace.date_creation.isoformat()
        })
    
    return {"espaces": result, "total": len(result)}

# ==================== ROUTES FORMATEUR ====================

@router.get("/espace/{id_espace}/etudiants")
async def lister_etudiants_espace(
    id_espace: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lister les étudiants d'un espace pédagogique (Formateur uniquement)"""
    
    if current_user.role != RoleEnum.FORMATEUR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux formateurs"
        )
    
    formateur = db.query(Formateur).filter(
        Formateur.identifiant == current_user.identifiant
    ).first()
    
    # Vérifier que l'espace existe et appartient au formateur
    espace = db.query(EspacePedagogique).filter(
        EspacePedagogique.id_espace == id_espace,
        EspacePedagogique.id_formateur == formateur.id_formateur
    ).first()
    
    if not espace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espace pédagogique non trouvé ou non autorisé"
        )
    
    # Récupérer tous les étudiants de la promotion
    etudiants = db.query(Etudiant).filter(
        Etudiant.id_promotion == espace.id_promotion
    ).all()
    
    result = []
    for etudiant in etudiants:
        # Vérifier si l'utilisateur existe
        if not etudiant.utilisateur:
            print(f"Attention: étudiant {etudiant.id_etudiant} n'a pas d'utilisateur associé")
            continue
            
        # Compter les travaux assignés à cet étudiant dans cet espace
        nb_travaux = db.query(Assignation).join(Travail).filter(
            Travail.id_espace == id_espace,
            Assignation.id_etudiant == etudiant.id_etudiant
        ).count()
        
        result.append({
            "id_etudiant": etudiant.id_etudiant,
            "nom": etudiant.utilisateur.nom,
            "prenom": etudiant.utilisateur.prenom,
            "matricule": etudiant.matricule,
            "email": etudiant.utilisateur.email,
            "statut": etudiant.statut,
            "nb_travaux_assignes": nb_travaux
        })
    
    return {
        "espace": {
            "id_espace": espace.id_espace,
            "nom_matiere": espace.nom_matiere,
            "promotion": espace.promotion.libelle
        },
        "etudiants": result,
        "total": len(result)
    }

@router.get("/mes-espaces")
async def mes_espaces_formateur(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lister les espaces du formateur connecté"""
    
    if current_user.role != RoleEnum.FORMATEUR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux formateurs"
        )
    
    formateur = db.query(Formateur).filter(
        Formateur.identifiant == current_user.identifiant
    ).first()
    
    if not formateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil formateur non trouvé"
        )
    
    espaces = db.query(EspacePedagogique).filter(
        EspacePedagogique.id_formateur == formateur.id_formateur
    ).all()
    
    result = []
    for espace in espaces:
        etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).all()
        
        nb_travaux = db.query(Travail).filter(
            Travail.id_espace == espace.id_espace
        ).count()
        
        result.append({
            "id_espace": espace.id_espace,
            "nom_matiere": espace.nom_matiere,
            "description": espace.description,
            "code_acces": espace.code_acces,
            "promotion": espace.promotion.libelle,
            "formation": espace.promotion.formation.nom_formation,
            "nb_etudiants": len(etudiants),
            "nb_travaux": nb_travaux,
            "etudiants": [
                {
                    "id_etudiant": e.id_etudiant,
                    "nom": e.utilisateur.nom if e.utilisateur else "N/A",
                    "prenom": e.utilisateur.prenom if e.utilisateur else "N/A",
                    "matricule": e.matricule,
                    "email": e.utilisateur.email if e.utilisateur else "N/A"
                } for e in etudiants
            ]
        })
    
    return {"espaces": result, "total": len(result)}

# ==================== ROUTES ETUDIANT ====================

@router.get("/mes-cours")
async def mes_cours_etudiant(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lister les cours de l'étudiant connecté"""
    
    if current_user.role != RoleEnum.ETUDIANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux étudiants"
        )
    
    etudiant = db.query(Etudiant).filter(
        Etudiant.identifiant == current_user.identifiant
    ).first()
    
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil étudiant non trouvé"
        )
    
    # Récupérer tous les espaces de la promotion de l'étudiant
    espaces = db.query(EspacePedagogique).filter(
        EspacePedagogique.id_promotion == etudiant.id_promotion
    ).all()
    
    result = []
    for espace in espaces:
        # Compter les travaux de cet espace
        nb_travaux = db.query(Travail).filter(
            Travail.id_espace == espace.id_espace
        ).count()
        
        # Compter les travaux assignés à cet étudiant dans cet espace
        nb_mes_travaux = db.query(Assignation).join(Travail).filter(
            Travail.id_espace == espace.id_espace,
            Assignation.id_etudiant == etudiant.id_etudiant
        ).count()
        
        result.append({
            "id_espace": espace.id_espace,
            "nom_matiere": espace.nom_matiere,
            "description": espace.description,
            "code_acces": espace.code_acces,
            "formation": espace.promotion.formation.nom_formation,
            "formateur": {
                "nom": espace.formateur.utilisateur.nom,
                "prenom": espace.formateur.utilisateur.prenom,
                "email": espace.formateur.utilisateur.email
            },
            "nb_travaux_total": nb_travaux,
            "nb_mes_travaux": nb_mes_travaux
        })
    
    return {"cours": result, "total": len(result)}

# ==================== ROUTES TRAVAUX ====================

@router.post("/travaux/creer")
async def creer_travail(
    data: TravailCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Créer un travail et l'assigner automatiquement (Formateur uniquement)"""
    
    if current_user.role != RoleEnum.FORMATEUR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les formateurs peuvent créer des travaux"
        )
    
    formateur = db.query(Formateur).filter(
        Formateur.identifiant == current_user.identifiant
    ).first()
    
    # Vérifier que l'espace existe et appartient au formateur
    espace = db.query(EspacePedagogique).filter(
        EspacePedagogique.id_espace == data.id_espace,
        EspacePedagogique.id_formateur == formateur.id_formateur
    ).first()
    
    if not espace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Espace pédagogique non trouvé ou non autorisé"
        )
    
    # Créer le travail
    id_travail = generer_identifiant_unique("TRAVAIL")
    travail = Travail(
        id_travail=id_travail,
        id_espace=data.id_espace,
        titre=data.titre,
        description=data.description,
        type_travail=TypeTravailEnum(data.type_travail),
        date_echeance=datetime.fromisoformat(data.date_echeance),
        note_max=data.note_max,
        date_creation=datetime.utcnow()
    )
    
    db.add(travail)
    db.commit()
    db.refresh(travail)
    
    # Déterminer les étudiants à assigner
    if data.etudiants_selectionnes and len(data.etudiants_selectionnes) > 0:
        # Assignation à des étudiants spécifiques
        etudiants = db.query(Etudiant).filter(
            Etudiant.id_etudiant.in_(data.etudiants_selectionnes),
            Etudiant.id_promotion == espace.id_promotion  # Sécurité : vérifier qu'ils sont dans la bonne promotion
        ).all()
        print(f"Assignation individuelle à {len(etudiants)} étudiant(s) sélectionné(s)")
    else:
        # Assignation à toute la promotion (comportement par défaut)
        etudiants = db.query(Etudiant).filter(
            Etudiant.id_promotion == espace.id_promotion
        ).all()
        print(f"Assignation globale à {len(etudiants)} étudiant(s) de la promotion")
    
    # Créer les assignations
    assignations_creees = []
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
        assignations_creees.append(assignation)
        
        # Envoyer email de notification
        try:
            email_service.envoyer_email_assignation_travail(
                destinataire=etudiant.utilisateur.email,
                prenom=etudiant.utilisateur.prenom,
                titre_travail=travail.titre,
                nom_matiere=espace.nom_matiere,
                formateur=f"{formateur.utilisateur.prenom} {formateur.utilisateur.nom}",
                date_echeance=travail.date_echeance.strftime("%d/%m/%Y à %H:%M"),
                description=travail.description
            )
        except Exception as e:
            print(f"Erreur envoi email à {etudiant.utilisateur.email}: {e}")
    
    db.commit()
    
    return {
        "message": "Travail créé et assigné avec succès",
        "travail": {
            "id_travail": travail.id_travail,
            "titre": travail.titre,
            "type_travail": travail.type_travail,
            "date_echeance": travail.date_echeance.isoformat(),
            "nb_assignations": len(assignations_creees)
        }
    }

@router.get("/travaux/mes-travaux")
async def mes_travaux_etudiant(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lister les travaux assignés à l'étudiant"""
    
    if current_user.role != RoleEnum.ETUDIANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux étudiants"
        )
    
    etudiant = db.query(Etudiant).filter(
        Etudiant.identifiant == current_user.identifiant
    ).first()
    
    assignations = db.query(Assignation).filter(
        Assignation.id_etudiant == etudiant.id_etudiant
    ).all()
    
    result = []
    for assignation in assignations:
        travail = assignation.travail
        espace = travail.espace_pedagogique
        
        result.append({
            "id_assignation": assignation.id_assignation,
            "statut": assignation.statut,
            "date_assignment": assignation.date_assignment.isoformat(),
            "travail": {
                "id_travail": travail.id_travail,
                "titre": travail.titre,
                "description": travail.description,
                "type_travail": travail.type_travail,
                "date_echeance": travail.date_echeance.isoformat(),
                "note_max": float(travail.note_max)
            },
            "espace": {
                "nom_matiere": espace.nom_matiere,
                "formateur": f"{espace.formateur.utilisateur.prenom} {espace.formateur.utilisateur.nom}"
            }
        })
    
    return {"travaux": result, "total": len(result)}