from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models import Utilisateur, TentativeConnexion, RoleEnum
from database.database import get_db
from core.jwt import create_access_token, get_password_hash, verify_password
import secrets


def generer_token_unique(longueur: int = 32) -> str:
    """Génère un token unique sécurisé"""
    return secrets.token_urlsafe(longueur)


def initialiser_compte_de(db: Session) -> Optional[Dict[str, Any]]:
    """
    Initialise le compte DE s'il n'existe pas déjà
    Retourne le compte DE existant ou le nouveau compte créé
    """
    # Vérifier si un compte DE existe déjà
    de_existant = db.query(Utilisateur).filter(Utilisateur.role == RoleEnum.DE).first()
    
    if de_existant:
        print(f"Debug: Compte DE existant trouvé: {de_existant.email}")
        return {
            "identifiant": de_existant.identifiant,
            "email": de_existant.email,
            "nom": de_existant.nom,
            "prenom": de_existant.prenom,
            "role": de_existant.role,
            "actif": de_existant.actif,
            "mot_de_passe_temporaire": de_existant.mot_de_passe_temporaire,
            "date_creation": de_existant.date_creation
        }
    
    # Créer un nouveau compte DE
    print("Debug: Création d'un nouveau compte DE")
    nouveau_de = {
        "identifiant": "de_principal",
        "email": "de@genielogiciel.com",
        "mot_de_passe": get_password_hash("admin123"),
        "nom": "Directeur",
        "prenom": "Établissement",
        "role": RoleEnum.DE,
        "actif": True,
        "mot_de_passe_temporaire": True,
        "date_creation": datetime.utcnow(),
        "token_activation": None,
        "date_expiration_token": None
    }
    
    # Créer l'entité utilisateur
    utilisateur = Utilisateur(**nouveau_de)
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    
    return {
        "identifiant": utilisateur.identifiant,
        "email": utilisateur.email,
        "nom": utilisateur.nom,
        "prenom": utilisateur.prenom,
        "role": utilisateur.role,
        "actif": utilisateur.actif,
        "mot_de_passe_temporaire": utilisateur.mot_de_passe_temporaire,
        "date_creation": utilisateur.date_creation
    }


def verifier_tentatives_connexion(db: Session, email: str) -> Optional[Dict[str, str]]:
    """
    Vérifie si l'utilisateur a dépassé le nombre de tentatives de connexion
    Retourne une erreur si trop de tentatives, sinon None
    """
    # Debug: Vérification des tentatives de connexion
    print(f"Debug: Vérification des tentatives pour l'email: {email}")
    
    # Calculer la date il y a 15 minutes
    date_limite = datetime.utcnow() - timedelta(minutes=15)
    
    # Compter les tentatives échouées dans les dernières 15 minutes
    tentatives_recentes = db.query(TentativeConnexion).filter(
        and_(
            TentativeConnexion.email == email,
            TentativeConnexion.succes == False,
            TentativeConnexion.date_tentative > date_limite
        )
    ).count()
    
    print(f"Debug: Nombre de tentatives échouées dans les 15 dernières minutes: {tentatives_recentes}")
    
    if tentatives_recentes >= 5:
        print("Debug: Trop de tentatives - blocage activé")
        return {
            "code": "AUTH_04",
            "message": "Trop de tentatives. Veuillez attendre 15 minutes."
        }
    
    print("Debug: Nombre de tentatives acceptable - pas de blocage")
    return None


def generer_token_jwt(utilisateur: Dict[str, Any]) -> str:
    """Génère un token JWT"""
    payload = {
        "sub": utilisateur["identifiant"],
        "email": utilisateur["email"],
        "role": utilisateur["role"],
        "nom": utilisateur["nom"],
        "prenom": utilisateur["prenom"]
    }
    return create_access_token(data=payload)