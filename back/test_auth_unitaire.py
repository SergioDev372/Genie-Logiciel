#!/usr/bin/env python3
"""
Tests unitaires pour le système d'authentification
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app
from database.database import get_db, Base
from models import Utilisateur, TentativeConnexion, RoleEnum

# Créer une base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Remplacer la dépendance de base de données
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestAuthentification:
    
    def test_initialiser_compte_de(self, test_db):
        """Test de l'initialisation du compte DE"""
        response = client.post("/api/auth/login", json={
            "email": "de@genielogiciel.com",
            "mot_de_passe": "admin123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["statut"] == "CHANGEMENT_MOT_DE_PASSE_REQUIS"
        assert "token" in data
        assert data["utilisateur"]["email"] == "de@genielogiciel.com"
        assert data["utilisateur"]["role"] == "DE"
    
    def test_login_succes(self, test_db):
        """Test de connexion réussie après changement de mot de passe"""
        # D'abord changer le mot de passe
        token_change = client.post("/api/auth/login", json={
            "email": "de@genielogiciel.com",
            "mot_de_passe": "admin123"
        }).json()["token"]
        
        response_change = client.post("/api/auth/changer-mot-de-passe", json={
            "token": token_change,
            "nouveau_mot_de_passe": "nouveau_mot_de_passe_123",
            "confirmation_mot_de_passe": "nouveau_mot_de_passe_123"
        })
        
        assert response_change.status_code == 200
        
        # Maintenant tester la connexion avec le nouveau mot de passe
        response_login = client.post("/api/auth/login", json={
            "email": "de@genielogiciel.com",
            "mot_de_passe": "nouveau_mot_de_passe_123"
        })
        
        assert response_login.status_code == 200
        data = response_login.json()
        assert data["statut"] == "SUCCESS"
        assert "token" in data
    
    def test_login_echoue_mauvais_mot_de_passe(self, test_db):
        """Test de connexion avec un mauvais mot de passe"""
        response = client.post("/api/auth/login", json={
            "email": "de@genielogiciel.com",
            "mot_de_passe": "mauvais_mot_de_passe"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "AUTH_01"
    
    def test_login_echoue_email_inexistant(self, test_db):
        """Test de connexion avec un email inexistant"""
        response = client.post("/api/auth/login", json={
            "email": "inexistant@test.com",
            "mot_de_passe": "admin123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "AUTH_01"
    
    def test_trop_de_tentatives(self, test_db):
        """Test du blocage après trop de tentatives"""
        email = "test_tentatives@test.com"
        
        # Créer un utilisateur pour le test
        db = TestingSessionLocal()
        utilisateur = Utilisateur(
            identifiant="test_user",
            email=email,
            mot_de_passe="$2b$12$N9qo8uLOickgx2ZMRZoMy.Mrqz7l3I5J4A8s6KYZ6J6K8F5m3vJ6K",  # hash de "password"
            nom="Test",
            prenom="User",
            role=RoleEnum.ETUDIANT,
            actif=True
        )
        db.add(utilisateur)
        db.commit()
        db.close()
        
        # Faire 5 tentatives échouées
        for i in range(5):
            response = client.post("/api/auth/login", json={
                "email": email,
                "mot_de_passe": "mauvais_mot_de_passe"
            })
            assert response.status_code == 401
        
        # La 6ème tentative devrait être bloquée
        response = client.post("/api/auth/login", json={
            "email": email,
            "mot_de_passe": "mauvais_mot_de_passe"
        })
        
        assert response.status_code == 429
        data = response.json()
        assert "Trop de tentatives" in data["detail"]["message"]
    
    def test_changer_mot_de_passe_token_invalide(self, test_db):
        """Test du changement de mot de passe avec un token invalide"""
        response = client.post("/api/auth/changer-mot-de-passe", json={
            "token": "token_invalide",
            "nouveau_mot_de_passe": "nouveau_mot_de_passe",
            "confirmation_mot_de_passe": "nouveau_mot_de_passe"
        })
        
        assert response.status_code == 400
        assert "Token invalide ou expiré" in response.json()["detail"]
    
    def test_activer_compte(self, test_db):
        """Test de l'activation d'un compte"""
        # Créer un utilisateur inactif avec token d'activation
        db = TestingSessionLocal()
        utilisateur = Utilisateur(
            identifiant="etudiant_test",
            email="etudiant@test.com",
            mot_de_passe="$2b$12$N9qo8uLOickgx2ZMRZoMy.Mrqz7l3I5J4A8s6KYZ6J6K8F5m3vJ6K",
            nom="Etudiant",
            prenom="Test",
            role=RoleEnum.ETUDIANT,
            actif=False,
            token_activation="token_activation_test",
            date_expiration_token=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(utilisateur)
        db.commit()
        db.close()
        
        response = client.post("/api/auth/activer-compte", json={
            "token": "token_activation_test",
            "mot_de_passe": "mot_de_passe_etudiant",
            "confirmation_mot_de_passe": "mot_de_passe_etudiant"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["statut"] == "SUCCESS"
        assert "token" in data
    
    def test_activer_compte_deja_actif(self, test_db):
        """Test de l'activation d'un compte déjà actif"""
        db = TestingSessionLocal()
        utilisateur = Utilisateur(
            identifiant="deja_actif",
            email="deja_actif@test.com",
            mot_de_passe="$2b$12$N9qo8uLOickgx2ZMRZoMy.Mrqz7l3I5J4A8s6KYZ6J6K8F5m3vJ6K",
            nom="Test",
            prenom="DejaActif",
            role=RoleEnum.ETUDIANT,
            actif=True,
            token_activation="token_activation_test",
            date_expiration_token=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(utilisateur)
        db.commit()
        db.close()
        
        response = client.post("/api/auth/activer-compte", json={
            "token": "token_activation_test",
            "mot_de_passe": "mot_de_passe",
            "confirmation_mot_de_passe": "mot_de_passe"
        })
        
        assert response.status_code == 400
        assert "Compte déjà activé" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])