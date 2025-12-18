import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import os

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_sender = "tfxyesu@gmail.com"
        # Pour Gmail, il faut utiliser un "App Password" pas le mot de passe normal
        self.email_password = "ybbc zyld mxbj olui"  # Mot de passe d'application Gmail
    
    def configurer_mot_de_passe(self, mot_de_passe: str):
        """Configure le mot de passe pour l'envoi d'emails"""
        self.email_password = mot_de_passe
    
    def envoyer_email_creation_compte(self, destinataire: str, prenom: str, 
                                     email: str, mot_de_passe: str, role: str) -> bool:
        """Envoie un email de création de compte avec identifiants"""
        try:
            # Création du message
            message = MIMEMultipart()
            message["From"] = self.email_sender
            message["To"] = destinataire
            message["Subject"] = f"Création de votre compte {role.lower()}"
            
            # Corps du message
            corps_message = f"""
Bonjour {prenom},

Votre compte {role.lower()} a été créé par le Directeur d'Établissement.

Voici vos informations de connexion :
• Email : {email}
• Mot de passe : {mot_de_passe}
• Rôle : {role}

🔗 Pour vous connecter :
Rendez-vous sur le site et connectez-vous avec ces identifiants.

⚠️ Important :
- Lors de votre première connexion, vous devrez obligatoirement changer votre mot de passe
- Conservez ces informations en sécurité

Si vous n'avez pas demandé la création de ce compte, veuillez ignorer cet email.

Cordialement,
L'équipe administrative
            """
            
            message.attach(MIMEText(corps_message, "plain", "utf-8"))
            
            # Envoi de l'email
            if self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(message)
                server.quit()
                return True
            else:
                print("⚠️ Mot de passe email non configuré - Email non envoyé")
                print(f"Destinataire: {destinataire}")
                print(f"Email: {email}")
                print(f"Mot de passe: {mot_de_passe}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False

    def envoyer_email_activation_compte(self, destinataire: str, prenom: str, 
                                       identifiant: str, mot_de_passe: str, 
                                       token_activation: str, role: str) -> bool:
        """Ancienne méthode - conservée pour compatibilité"""
        return self.envoyer_email_creation_compte(destinataire, prenom, destinataire, mot_de_passe, role)

    def envoyer_email_assignation_travail(self, destinataire: str, prenom: str,
                                         titre_travail: str, nom_matiere: str,
                                         formateur: str, date_echeance: str,
                                         description: str) -> bool:
        """Envoie un email de notification d'assignation de travail"""
        try:
            # Création du message
            message = MIMEMultipart()
            message["From"] = self.email_sender
            message["To"] = destinataire
            message["Subject"] = f"Nouveau travail assigné : {titre_travail}"
            
            # Corps du message
            corps_message = f"""
Bonjour {prenom},

Un nouveau travail vous a été assigné dans le cours {nom_matiere}.

📋 Détails du travail :
• Titre : {titre_travail}
• Matière : {nom_matiere}
• Formateur : {formateur}
• Date d'échéance : {date_echeance}

📝 Description :
{description}

🔗 Pour consulter et soumettre votre travail :
Connectez-vous à votre espace étudiant sur la plateforme.

⚠️ Important :
- Respectez la date d'échéance
- Consultez régulièrement vos travaux assignés
- Contactez votre formateur en cas de questions

Bon travail !

L'équipe pédagogique
            """
            
            message.attach(MIMEText(corps_message, "plain", "utf-8"))
            
            # Envoi de l'email
            if self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(message)
                server.quit()
                return True
            else:
                print("⚠️ Mot de passe email non configuré - Email non envoyé")
                print(f"Destinataire: {destinataire}")
                print(f"Travail: {titre_travail}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email d'assignation: {e}")
            return False
    
    def envoyer_email_test(self) -> bool:
        """Envoie un email de test pour vérifier la configuration"""
        return self.envoyer_email_activation_compte(
            destinataire="test@example.com",
            prenom="Test",
            identifiant="TEST_123",
            mot_de_passe="TestPass123!",
            token_activation="test_token_123",
            role="TEST"
        )

# Instance globale du service email
email_service = EmailService()
