import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from utils.generators import (
    generer_identifiant_unique,
    generer_mot_de_passe_aléatoire,
    generer_token_activation,
    generer_matricule_unique,
    generer_numero_employe
)

class TestGenerators:
    """Tests pour les fonctions de génération"""
    
    def test_generer_identifiant_unique_formateur(self):
        """Test génération identifiant formateur"""
        identifiant = generer_identifiant_unique("FORMATEUR")
        
        assert identifiant.startswith("FMT_")
        assert len(identifiant) > 10  # Doit être suffisamment long
        
        # Vérifier que chaque génération est différente
        identifiant2 = generer_identifiant_unique("FORMATEUR")
        assert identifiant != identifiant2
    
    def test_generer_identifiant_unique_etudiant(self):
        """Test génération identifiant étudiant"""
        identifiant = generer_identifiant_unique("ETUDIANT")
        
        assert identifiant.startswith("ETD_")
        assert len(identifiant) > 10
    
    def test_generer_mot_de_passe_aléatoire(self):
        """Test génération mot de passe"""
        mot_de_passe = generer_mot_de_passe_aléatoire()
        
        assert len(mot_de_passe) == 12  # Longueur par défaut
        assert any(c.isupper() for c in mot_de_passe)  # Contient des majuscules
        assert any(c.islower() for c in mot_de_passe)  # Contient des minuscules
        assert any(c.isdigit() for c in mot_de_passe)  # Contient des chiffres
        assert any(c in "!@#$%&*" for c in mot_de_passe)  # Contient des caractères spéciaux
        
        # Vérifier que chaque génération est différente
        mot_de_passe2 = generer_mot_de_passe_aléatoire()
        assert mot_de_passe != mot_de_passe2
    
    def test_generer_mot_de_passe_longueur_personnalisée(self):
        """Test génération mot de passe avec longueur personnalisée"""
        mot_de_passe = generer_mot_de_passe_aléatoire(16)
        assert len(mot_de_passe) == 16
    
    def test_generer_token_activation(self):
        """Test génération token d'activation"""
        token = generer_token_activation()
        
        assert len(token) > 30  # Doit être suffisamment long
        assert isinstance(token, str)
        
        # Vérifier que chaque génération est différente
        token2 = generer_token_activation()
        assert token != token2
    
    def test_generer_matricule_unique(self):
        """Test génération matricule"""
        matricule = generer_matricule_unique()
        
        assert matricule.startswith("MAT")
        assert str(datetime.now().year) in matricule  # Contient l'année actuelle
        assert len(matricule) >= 8  # MAT + année + numéro
        
        # Vérifier que chaque génération est différente
        matricule2 = generer_matricule_unique()
        assert matricule != matricule2
    
    def test_generer_numero_employe(self):
        """Test génération numéro employé"""
        numero = generer_numero_employe()
        
        assert numero.startswith("EMP")
        assert str(datetime.now().year) in numero  # Contient l'année actuelle
        assert len(numero) >= 7  # EMP + année + numéro
        
        # Vérifier que chaque génération est différente
        numero2 = generer_numero_employe()
        assert numero != numero2

class TestEmailServiceIntegration:
    """Tests d'intégration pour le service email"""
    
    @patch('smtplib.SMTP')
    def test_configuration_email_service(self, mock_smtp):
        """Test configuration du service email"""
        from utils.email_service import EmailService
        
        service = EmailService()
        assert service.email_sender == "tfxyesu@gmail.com"
        assert service.smtp_server == "smtp.gmail.com"
        assert service.smtp_port == 587
        
        # Test configuration mot de passe
        service.configurer_mot_de_passe("test_password")
        assert service.email_password == "test_password"
    
    @patch('smtplib.SMTP')
    def test_contenu_email_formateur(self, mock_smtp):
        """Test du contenu de l'email pour formateur"""
        from utils.email_service import EmailService
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        service = EmailService()
        service.configurer_mot_de_passe("test_password")
        
        # Capturer le message envoyé
        sent_messages = []
        def capture_message(message):
            sent_messages.append(message)
        
        mock_server.send_message.side_effect = capture_message
        
        service.envoyer_email_activation_compte(
            destinataire="formateur@test.com",
            prenom="Jean",
            identifiant="FMT_123456",
            mot_de_passe="Pass123!",
            token_activation="token_abc123",
            role="FORMATEUR"
        )
        
        # Vérifier que l'email a été envoyé
        assert len(sent_messages) == 1
        message = sent_messages[0]
        
        # Vérifier le contenu
        assert "Jean" in message.get_body().get_content()
        assert "FMT_123456" in message.get_body().get_content()
        assert "Pass123!" in message.get_body().get_content()
        assert "token_abc123" in message.get_body().get_content()
        assert "formateur" in message.get_body().get_content().lower()

class TestTokenValidation:
    """Tests pour la validation des tokens"""
    
    def test_token_jwt_creation_et_verification(self):
        """Test création et vérification de token JWT"""
        from core.jwt import create_access_token, verify_token
        
        payload = {
            "sub": "test_user",
            "email": "test@test.com",
            "role": "FORMATEUR"
        }
        
        # Créer le token
        token = create_access_token(payload)
        assert isinstance(token, str)
        assert len(token) > 50  # JWT sont généralement longs
        
        # Vérifier le token
        decoded_payload = verify_token(token)
        assert decoded_payload["sub"] == "test_user"
        assert decoded_payload["email"] == "test@test.com"
        assert decoded_payload["role"] == "FORMATEUR"
        assert "exp" in decoded_payload  # Expiration ajoutée automatiquement
    
    def test_token_jwt_expiration(self):
        """Test expiration du token JWT"""
        from core.jwt import create_access_token, verify_token
        from datetime import datetime, timedelta
        import time
        
        payload = {"sub": "test_user"}
        
        # Créer un token expiré
        token_expiré = create_access_token(
            payload, 
            expires_delta=timedelta(seconds=-1)  # Expiré immédiatement
        )
        
        # Attendre un peu pour s'assurer que le token est expiré
        time.sleep(0.1)
        
        # Tenter de vérifier le token expiré
        with pytest.raises(Exception):  # Doit lever une exception
            verify_token(token_expiré)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
