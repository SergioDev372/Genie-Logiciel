import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Optional

def generer_identifiant_unique(role: str) -> str:
    """Génère un identifiant unique basé sur le rôle"""
    prefixe = ""
    if role == "FORMATEUR":
        prefixe = "FMT"
    elif role == "ETUDIANT":
        prefixe = "ETD"
    else:
        prefixe = "USR"
    
    timestamp = str(int(time.time()))
    aleatoire = str(secrets.randbelow(9000) + 1000)
    
    return f"{prefixe}_{timestamp}_{aleatoire}"

def generer_mot_de_passe_aleatoire(longueur: int = 8) -> str:
    """Génère un mot de passe simple avec lettres majuscules et chiffres uniquement"""
    caracteres = string.ascii_uppercase + string.digits  # A-Z + 0-9 seulement
    mot_de_passe = ''.join(secrets.choice(caracteres) for _ in range(longueur))
    return mot_de_passe

def generer_token_activation() -> str:
    """Génère un token d'activation sécurisé"""
    return secrets.token_urlsafe(32)

def generer_matricule_unique() -> str:
    """Génère un matricule unique pour étudiant"""
    annee = datetime.now().year
    # En pratique, on devrait récupérer le dernier numéro depuis la base
    numero = secrets.randbelow(9000) + 1000
    return f"MAT{annee}{str(numero).zfill(4)}"

def generer_numero_employe() -> str:
    """Génère un numéro d'employé unique"""
    annee = datetime.now().year
    numero = secrets.randbelow(900) + 100
    return f"EMP{annee}{str(numero).zfill(3)}"
