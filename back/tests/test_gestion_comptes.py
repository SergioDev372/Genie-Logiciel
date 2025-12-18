import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from main import app
from database.database import get_db
from models import Utilisateur, Formateur, Etudiant, RoleEnum, StatutEtudiantEnum
from core.jwt import create_access_token, verify_token

# Client de test
client = TestClient(app)

# Mock de la base de données
def mock_get_db():
    """Mock pour la session de base de données"""
    pass

@pytest.fixture
def mock_db_session():
    """Fixture pour mocker la session de base de données"""
    session = MagicMock(spec=Session)
    return session

@pytest.fixture
def de_user():
    """Fixture pour créer un utilisateur DE de test"""
    return Utilisateur(
        identifiant="de_test",
        email="de@test.com",
        nom="Directeur",
        prenom="Test",
        role=RoleEnum.DE,
        actif=True,
        mot_de_passe_temporaire=False
    )

@pytest.fixture
def de_token(de_user):
    """Fixture pour générer un token JWT pour le DE"""
    return create_access_token({
        "sub": de_user.identifiant,
        "email": de_user.email,
        "role": de_user.role,
        "nom": de_user.nom,
        "prenom": de_user.prenom
    })

class TestCreationCompteFormateur:
    """Tests pour la création de compte formateur par le DE"""
    
    @patch('routes.gestion_comptes.get_db')
    @patch('routes.gestion_comptes.email_service')
    def test_creer_formateur_success(self, mock_email, mock_db, de_user, de_token):
        """Test création réussie d'un compte formateur"""
        # Configuration des mocks
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        # Mock pour get_current_user
        with patch('routes.gestion_comptes.get_current_user', return_value=de_user):
            # Mock vérification email existant
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            # Mock sauvegarde en base
            mock_session.add = MagicMock()
            mock_session.commit = MagicMock()
            mock_session.refresh = MagicMock()
            
            # Mock email service
            mock_email.envoyer_email_activation_compte.return_value = True
            
            # Données de test
            formateur_data = {
                "email": "formateur@test.com",
                "nom": "Dupont",
                "prenom": "Jean",
                "specialite": "Mathématiques"
            }
            
            # Appel de l'API
            response = client.post(
                "/api/gestion-comptes/creer-formateur",
                json=formateur_data,
                headers={"Authorization": f"Bearer {de_token}"}
            )
            
            # Vérifications
            assert response.status_code == 201
            data = response.json()
            assert data["message"] == "Compte formateur créé avec succès"
            assert data["email_envoye"] == True
            assert "identifiant" in data
            assert "id_formateur" in data
            
            # Vérifier que l'email a été envoyé
            mock_email.envoyer_email_activation_compte.assert_called_once()
            
            # Vérifier la sauvegarde en base
            assert mock_session.add.call_count == 2  # utilisateur + formateur
            mock_session.commit.assert_called_once()

    @patch('routes.gestion_comptes.get_db')
    def test_creer_formateur_email_deja_utilise(self, mock_db, de_user, de_token):
        """Test échec si email déjà utilisé"""
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        with patch('routes.gestion_comptes.get_current_user', return_value=de_user):
            # Mock email existant
            existing_user = Utilisateur(email="formateur@test.com")
            mock_session.query.return_value.filter.return_value.first.return_value = existing_user
            
            formateur_data = {
                "email": "formateur@test.com",
                "nom": "Dupont",
                "prenom": "Jean"
            }
            
            response = client.post(
                "/api/gestion-comptes/creer-formateur",
                json=formateur_data,
                headers={"Authorization": f"Bearer {de_token}"}
            )
            
            assert response.status_code == 400
            assert "Cet email est déjà utilisé" in response.json()["detail"]

    def test_creer_formateur_sans_auth(self):
        """Test échec sans authentification"""
        formateur_data = {
            "email": "formateur@test.com",
            "nom": "Dupont",
            "prenom": "Jean"
        }
        
        response = client.post(
            "/api/gestion-comptes/creer-formateur",
            json=formateur_data
        )
        
        assert response.status_code == 401

class TestCreationCompteEtudiant:
    """Tests pour la création de compte étudiant par le DE"""
    
    @patch('routes.gestion_comptes.get_db')
    @patch('routes.gestion_comptes.email_service')
    def test_creer_etudiant_success(self, mock_email, mock_db, de_user, de_token):
        """Test création réussie d'un compte étudiant"""
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        with patch('routes.gestion_comptes.get_current_user', return_value=de_user):
            # Mock vérifications
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            # Mock sauvegarde
            mock_session.add = MagicMock()
            mock_session.commit = MagicMock()
            mock_session.refresh = MagicMock()
            
            # Mock email
            mock_email.envoyer_email_activation_compte.return_value = True
            
            etudiant_data = {
                "email": "etudiant@test.com",
                "nom": "Martin",
                "prenom": "Sophie",
                "id_promotion": "PROMO_2024"
            }
            
            response = client.post(
                "/api/gestion-comptes/creer-etudiant",
                json=etudiant_data,
                headers={"Authorization": f"Bearer {de_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["message"] == "Compte étudiant créé avec succès"
            assert "matricule" in data
            assert "identifiant" in data

class TestActivationCompte:
    """Tests pour l'activation de compte"""
    
    @patch('routes.gestion_comptes.get_db')
    def test_activation_compte_success(self, mock_db):
        """Test activation réussie d'un compte"""
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        # Créer un utilisateur inactif avec token valide
        utilisateur_inactif = Utilisateur(
            identifiant="test_user",
            email="test@test.com",
            actif=False,
            token_activation="token_123",
            date_expiration_token=datetime.utcnow() + timedelta(days=1),
            mot_de_passe_temporaire=True
        )
        
        mock_session.query.return_value.filter.return_value.first.return_value = utilisateur_inactif
        mock_session.commit = MagicMock()
        
        response = client.get("/api/gestion-comptes/activation/token_123")
        
        assert response.status_code == 200
        data = response.json()
        assert "Compte activé avec succès" in data["message"]
        
        # Vérifier que l'utilisateur a été activé
        assert utilisateur_inactif.actif == True
        assert utilisateur_inactif.token_activation is None
        assert utilisateur_inactif.date_expiration_token is None
        mock_session.commit.assert_called_once()

    @patch('routes.gestion_comptes.get_db')
    def test_activation_token_invalide(self, mock_db):
        """Test échec activation avec token invalide"""
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        # Aucun utilisateur trouvé
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        response = client.get("/api/gestion-comptes/activation/token_invalide")
        
        assert response.status_code == 400
        assert "Token d'activation invalide" in response.json()["detail"]

    @patch('routes.gestion_comptes.get_db')
    def test_activation_token_expiré(self, mock_db):
        """Test échec activation avec token expiré"""
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        # Utilisateur avec token expiré
        utilisateur_expiré = Utilisateur(
            identifiant="test_user",
            token_activation="token_expiré",
            date_expiration_token=datetime.utcnow() - timedelta(days=1)  # Expiré
        )
        
        mock_session.query.return_value.filter.return_value.first.return_value = utilisateur_expiré
        
        response = client.get("/api/gestion-comptes/activation/token_expiré")
        
        assert response.status_code == 400
        assert "Token d'activation expiré" in response.json()["detail"]

class TestEmailService:
    """Tests pour le service email"""
    
    @patch('smtplib.SMTP')
    def test_envoi_email_success(self, mock_smtp):
        """Test envoi réussi d'email"""
        from utils.email_service import EmailService
        
        # Configuration du mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        service = EmailService()
        service.configurer_mot_de_passe("test_password")
        
        result = service.envoyer_email_activation_compte(
            destinataire="test@test.com",
            prenom="Test",
            identifiant="TEST_123",
            mot_de_passe="Pass123!",
            token_activation="token_123",
            role="FORMATEUR"
        )
        
        assert result == True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    def test_envoi_email_sans_mot_de_passe(self):
        """Test envoi email sans mot de passe configuré"""
        from utils.email_service import EmailService
        
        service = EmailService()
        # Ne pas configurer le mot de passe
        
        result = service.envoyer_email_activation_compte(
            destinataire="test@test.com",
            prenom="Test",
            identifiant="TEST_123",
            mot_de_passe="Pass123!",
            token_activation="token_123",
            role="FORMATEUR"
        )
        
        assert result == False

class TestWorkflowComplet:
    """Test du workflow complet de création → activation"""
    
    @patch('routes.gestion_comptes.get_db')
    @patch('routes.gestion_comptes.email_service')
    def test_workflow_complet_formateur(self, mock_email, mock_db, de_user, de_token):
        """Test workflow complet pour formateur"""
        mock_session = MagicMock(spec=Session)
        mock_db.return_value = mock_session
        
        with patch('routes.gestion_comptes.get_current_user', return_value=de_user):
            # Étape 1: Création du compte
            mock_session.query.return_value.filter.return_value.first.return_value = None
            mock_session.add = MagicMock()
            mock_session.commit = MagicMock()
            mock_session.refresh = MagicMock()
            mock_email.envoyer_email_activation_compte.return_value = True
            
            formateur_data = {
                "email": "formateur@test.com",
                "nom": "Dupont",
                "prenom": "Jean",
                "specialite": "Mathématiques"
            }
            
            creation_response = client.post(
                "/api/gestion-comptes/creer-formateur",
                json=formateur_data,
                headers={"Authorization": f"Bearer {de_token}"}
            )
            
            assert creation_response.status_code == 201
            creation_data = creation_response.json()
            identifiant = creation_data["identifiant"]
            
            # Étape 2: Simulation de l'activation
            # Créer l'utilisateur qui serait en base
            utilisateur_cree = Utilisateur(
                identifiant=identifiant,
                email="formateur@test.com",
                actif=False,
                token_activation="token_workflow",
                date_expiration_token=datetime.utcnow() + timedelta(days=1),
                mot_de_passe_temporaire=True
            )
            
            mock_session.query.return_value.filter.return_value.first.return_value = utilisateur_cree
            
            # Étape 3: Activation du compte
            activation_response = client.get("/api/gestion-comptes/activation/token_workflow")
            
            assert activation_response.status_code == 200
            assert utilisateur_cree.actif == True
            assert utilisateur_cree.token_activation is None
            
            # Vérifier le workflow complet
            assert mock_email.envoyer_email_activation_compte.call_count == 1
            assert mock_session.commit.call_count == 2  # création + activation

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
