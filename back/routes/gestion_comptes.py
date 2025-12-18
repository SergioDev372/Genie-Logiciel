from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from database.database import get_db
from models import Utilisateur, Formateur, Etudiant, Promotion, Formation, RoleEnum, StatutEtudiantEnum
from core.auth import get_password_hash as hash_password, get_current_user
from utils.generators import (
    generer_identifiant_unique, 
    generer_mot_de_passe_aleatoire, 
    generer_token_activation,
    generer_matricule_unique,
    generer_numero_employe
)
from utils.email_service import email_service
from utils.promotion_generator import (
    generer_promotion_automatique,
    valider_annee_academique,
    lister_annees_disponibles,
    lister_promotions_existantes
)

router = APIRouter(prefix="/api/gestion-comptes", tags=["Gestion des comptes"])

# Schémas Pydantic pour la validation
from pydantic import BaseModel, EmailStr

class FormateurCreate(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    specialite: str = None

class EtudiantCreate(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    annee_academique: str  # Format: "2024-2025"

class ActivationResponse(BaseModel):
    message: str

@router.post("/creer-formateur", status_code=status.HTTP_201_CREATED)
async def creer_compte_formateur(
    formateur_data: FormateurCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Route pour créer un compte formateur (réservée au DE)"""
    
    # Vérifier que l'utilisateur actuel est un DE
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un Directeur d'Établissement peut créer des comptes formateurs"
        )
    
    # 1. Validation des données
    # Vérifier si l'email existe déjà
    email_existant = db.query(Utilisateur).filter(Utilisateur.email == formateur_data.email).first()
    if email_existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # 2. Génération automatique
    identifiant = generer_identifiant_unique("FORMATEUR")
    mot_de_passe = generer_mot_de_passe_aleatoire()  # Mot de passe simple A-Z + 0-9
    id_formateur = generer_identifiant_unique("FORMATEUR")  # Utiliser la même fonction
    numero_employe = generer_numero_employe()
    # Plus besoin de token d'activation
    
    # 3. Création utilisateur (actif avec mot de passe temporaire)
    nouvel_utilisateur = Utilisateur(
        identifiant=identifiant,
        email=formateur_data.email,
        mot_de_passe=hash_password(mot_de_passe),
        nom=formateur_data.nom,
        prenom=formateur_data.prenom,
        role=RoleEnum.FORMATEUR,
        actif=True,  # Compte actif dès la création
        token_activation=None,  # Pas de token d'activation
        date_expiration_token=None,  # Pas d'expiration
        mot_de_passe_temporaire=True  # Doit changer le mot de passe à la première connexion
    )
    
    # 4. Création formateur
    nouveau_formateur = Formateur(
        id_formateur=id_formateur,
        identifiant=identifiant,
        numero_employe=numero_employe,
        specialite=formateur_data.specialite
    )
    
    # 5. Sauvegarde en base
    try:
        db.add(nouvel_utilisateur)
        db.add(nouveau_formateur)
        db.commit()
        db.refresh(nouvel_utilisateur)
        db.refresh(nouveau_formateur)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )
    
    # 6. Envoi email avec identifiants
    email_envoye = email_service.envoyer_email_creation_compte(
        destinataire=formateur_data.email,
        prenom=formateur_data.prenom,
        email=formateur_data.email,
        mot_de_passe=mot_de_passe,
        role="FORMATEUR"
    )
    
    return {
        "message": "Compte formateur créé avec succès",
        "email_envoye": email_envoye,
        "identifiant": identifiant,
        "id_formateur": id_formateur
    }

@router.post("/creer-etudiant", status_code=status.HTTP_201_CREATED)
async def creer_compte_etudiant(
    etudiant_data: EtudiantCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Route pour créer un compte étudiant (réservée au DE)"""
    
    # Vérifier que l'utilisateur actuel est un DE
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un Directeur d'Établissement peut créer des comptes étudiants"
        )
    
    # 1. Validation des données
    # Vérifier si l'email existe déjà
    email_existant = db.query(Utilisateur).filter(Utilisateur.email == etudiant_data.email).first()
    if email_existant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Valider le format de l'année académique
    if not valider_annee_academique(etudiant_data.annee_academique):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'année académique invalide. Utilisez le format YYYY-YYYY (ex: 2024-2025)"
        )
    
    # Générer automatiquement la promotion pour cette année
    try:
        promotion = generer_promotion_automatique(db, etudiant_data.annee_academique)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de la promotion: {str(e)}"
        )
    
    # 2. Génération automatique
    identifiant = generer_identifiant_unique("ETUDIANT")
    mot_de_passe = generer_mot_de_passe_aleatoire()  # Mot de passe simple A-Z + 0-9
    id_etudiant = generer_identifiant_unique("ETUDIANT")  # Utiliser la même fonction
    matricule = generer_matricule_unique()
    # Plus besoin de token d'activation
    
    # 3. Création utilisateur (actif avec mot de passe temporaire)
    nouvel_utilisateur = Utilisateur(
        identifiant=identifiant,
        email=etudiant_data.email,
        mot_de_passe=hash_password(mot_de_passe),
        nom=etudiant_data.nom,
        prenom=etudiant_data.prenom,
        role=RoleEnum.ETUDIANT,
        actif=True,  # Compte actif dès la création
        token_activation=None,  # Pas de token d'activation
        date_expiration_token=None,  # Pas d'expiration
        mot_de_passe_temporaire=True  # Doit changer le mot de passe à la première connexion
    )
    
    # 4. Création étudiant
    nouvel_etudiant = Etudiant(
        id_etudiant=id_etudiant,
        identifiant=identifiant,  # Ce champ lie à Utilisateur.identifiant
        matricule=matricule,
        id_promotion=promotion.id_promotion,
        date_inscription=datetime.utcnow().date(),
        statut=StatutEtudiantEnum.ACTIF
    )
    
    # 5. Sauvegarde en base
    try:
        db.add(nouvel_utilisateur)
        db.add(nouvel_etudiant)
        db.commit()
        db.refresh(nouvel_utilisateur)
        db.refresh(nouvel_etudiant)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )
    
    # 6. Envoi email avec identifiants
    email_envoye = email_service.envoyer_email_creation_compte(
        destinataire=etudiant_data.email,
        prenom=etudiant_data.prenom,
        email=etudiant_data.email,
        mot_de_passe=mot_de_passe,
        role="ETUDIANT"
    )
    
    return {
        "message": "Compte étudiant créé avec succès",
        "email_envoye": email_envoye,
        "identifiant": identifiant,
        "id_etudiant": id_etudiant,
        "matricule": matricule
    }

# Route d'activation supprimée - plus nécessaire avec la nouvelle logique

@router.get("/annees-academiques")
async def lister_annees_academiques(
    current_user: Utilisateur = Depends(get_current_user)
):
    """Liste les années académiques disponibles pour la création d'étudiants"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un DE peut accéder à cette information"
        )
    
    annees = lister_annees_disponibles()
    
    return {
        "annees_disponibles": annees,
        "format": "YYYY-YYYY",
        "exemple": "2024-2025"
    }

@router.get("/promotions")
async def lister_promotions(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Liste toutes les promotions existantes"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un DE peut accéder à cette information"
        )
    
    promotions = lister_promotions_existantes(db)
    
    return {
        "promotions": promotions,
        "total": len(promotions)
    }

@router.get("/formations")
async def lister_formations(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Liste toutes les formations disponibles"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un DE peut accéder à cette information"
        )
    
    formations = db.query(Formation).all()
    
    return {
        "formations": [
            {
                "id_formation": f.id_formation,
                "nom_formation": f.nom_formation,
                "description": f.description
            } for f in formations
        ]
    }

@router.get("/formateurs")
async def lister_formateurs(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Liste tous les formateurs disponibles"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un DE peut accéder à cette information"
        )
    
    formateurs = db.query(Formateur).join(Utilisateur).all()
    
    return {
        "formateurs": [
            {
                "id_formateur": f.id_formateur,
                "nom": f.utilisateur.nom,
                "prenom": f.utilisateur.prenom,
                "email": f.utilisateur.email,
                "specialite": f.specialite,
                "numero_employe": f.numero_employe
            } for f in formateurs
        ]
    }

@router.post("/configurer-email")
async def configurer_email_service(
    mot_de_passe: str,
    current_user: Utilisateur = Depends(get_current_user)
):
    """Configure le mot de passe pour le service email (réservé au DE)"""
    
    if current_user.role != RoleEnum.DE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un DE peut configurer le service email"
        )
    
    email_service.configurer_mot_de_passe(mot_de_passe)
    
    return {"message": "Service email configuré avec succès"}
