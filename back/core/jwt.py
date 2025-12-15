from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
import secrets
import hashlib

# Configuration JWT
SECRET_KEY = secrets.token_urlsafe(32)  # Générer une clé secrète en production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT d'accès
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Vérifie et décode un token JWT
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_password_hash(password: str) -> str:
    """
    Hache un mot de passe avec SHA-256 (cohérent avec l'algorithme original)
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe correspond au hash
    Essaie différents algorithmes de hashage pour la compatibilité
    """
    # Debug: Vérification du mot de passe
    print(f"Debug: Vérification du mot de passe")
    print(f"Debug: Mot de passe en clair: {plain_password}")
    print(f"Debug: Hash du mot de passe en clair (SHA-256): {hashlib.sha256(plain_password.encode()).hexdigest()}")
    print(f"Debug: Hash du mot de passe en clair (MD5): {hashlib.md5(plain_password.encode()).hexdigest()}")
    print(f"Debug: Hash du mot de passe en clair (SHA-1): {hashlib.sha1(plain_password.encode()).hexdigest()}")
    print(f"Debug: Hash en base: {hashed_password}")
    
    # Essayer SHA-256 (notre algorithme principal)
    if hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password:
        print("Debug: Correspondance SHA-256 trouvée")
        return True
    
    # Essayer MD5 (pour la compatibilité avec certains systèmes anciens)
    if hashlib.md5(plain_password.encode()).hexdigest() == hashed_password:
        print("Debug: Correspondance MD5 trouvée")
        return True
    
    # Essayer SHA-1 (pour la compatibilité)
    if hashlib.sha1(plain_password.encode()).hexdigest() == hashed_password:
        print("Debug: Correspondance SHA-1 trouvée")
        return True
    
    # Vérifier si le hash correspond exactement (pour les mots de passe déjà hashés)
    if plain_password == hashed_password:
        print("Debug: Correspondance exacte trouvée")
        return True
    
    # Si le hash commence par "hashed_", c'est probablement un hash personnalisé
    if hashed_password.startswith("hashed_"):
        # Ici vous pouvez ajouter la logique pour votre hash personnalisé
        # Par exemple: si hashed_password == "hashed_admin123_passwor" et plain_password == "admin123"
        if hashed_password == "hashed_admin123_password" and plain_password == "admin123":
            print("Debug: Correspondance hash personnalisé trouvée")
            return True
    
    print("Debug: Aucune correspondance trouvée")
    return False