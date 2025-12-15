from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import secrets

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Enum as SAEnum,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.database import Base


class RoleEnum(str, Enum):
    DE = "DE"
    FORMATEUR = "FORMATEUR"
    ETUDIANT = "ETUDIANT"


class StatutEtudiantEnum(str, Enum):
    ACTIF = "ACTIF"
    SUSPENDU = "SUSPENDU"
    EXCLU = "EXCLU"


class TypeTravailEnum(str, Enum):
    INDIVIDUEL = "INDIVIDUEL"
    COLLECTIF = "COLLECTIF"


class StatutAssignationEnum(str, Enum):
    ASSIGNE = "ASSIGNE"
    EN_COURS = "EN_COURS"
    RENDU = "RENDU"
    NOTE = "NOTE"


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    identifiant = Column(String(100), primary_key=True, nullable=False)  # Clé primaire interne (alphanumérique)
    email = Column(String(191), unique=True, nullable=False, index=True)  # ← Utilisé pour la connexion
    mot_de_passe = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    actif = Column(Boolean, nullable=False, default=True)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    token_activation = Column(String(255), nullable=True)
    date_expiration_token = Column(DateTime, nullable=True)
    mot_de_passe_temporaire = Column(Boolean, nullable=False, default=False)  # ← AJOUTÉ pour gérer le DE

    # Relations : un utilisateur a 0 ou 1 rôle spécifique
    etudiant = relationship("Etudiant", back_populates="utilisateur", uselist=False)
    formateur = relationship("Formateur", back_populates="utilisateur", uselist=False)
    # ⚠️ Le DE n'a PAS de relation vers Formateur ou Etudiant


class Formation(Base):
    __tablename__ = "formation"

    id_formation = Column(String(100), primary_key=True, nullable=False)
    nom_formation = Column(String(191), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)

    promotions = relationship("Promotion", back_populates="formation")


class Promotion(Base):
    __tablename__ = "promotion"

    id_promotion = Column(String(100), primary_key=True, nullable=False)
    id_formation = Column(String(100), ForeignKey("formation.id_formation"), nullable=False)
    annee_academique = Column(String(20), nullable=False)
    libelle = Column(String(255), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("id_formation", "annee_academique", name="uq_promotion_formation_annee"),
    )

    formation = relationship("Formation", back_populates="promotions")
    etudiants = relationship("Etudiant", back_populates="promotion")
    espaces_pedagogiques = relationship("EspacePedagogique", back_populates="promotion")


class Etudiant(Base):
    __tablename__ = "etudiant"

    id_etudiant = Column(String(100), primary_key=True, nullable=False)
    identifiant = Column(String(100), ForeignKey("utilisateur.identifiant"), unique=True, nullable=False)
    matricule = Column(String(100), unique=True, nullable=False)
    id_promotion = Column(String(100), ForeignKey("promotion.id_promotion"), nullable=False)
    date_inscription = Column(Date, nullable=False)
    statut = Column(SAEnum(StatutEtudiantEnum), nullable=False, default=StatutEtudiantEnum.ACTIF)

    utilisateur = relationship("Utilisateur", back_populates="etudiant")
    promotion = relationship("Promotion", back_populates="etudiants")
    assignations = relationship("Assignation", back_populates="etudiant")


class Formateur(Base):
    __tablename__ = "formateur"

    id_formateur = Column(String(100), primary_key=True, nullable=False)
    identifiant = Column(String(100), ForeignKey("utilisateur.identifiant"), unique=True, nullable=False)
    numero_employe = Column(String(100), nullable=True)
    specialite = Column(String(255), nullable=True)

    utilisateur = relationship("Utilisateur", back_populates="formateur")
    espaces_pedagogiques = relationship("EspacePedagogique", back_populates="formateur")


class EspacePedagogique(Base):
    __tablename__ = "espace_pedagogique"

    id_espace = Column(String(100), primary_key=True, nullable=False)
    id_promotion = Column(String(100), ForeignKey("promotion.id_promotion"), nullable=False)
    nom_matiere = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    id_formateur = Column(String(100), ForeignKey("formateur.id_formateur"), nullable=False)
    code_acces = Column(String(100), nullable=True)

    promotion = relationship("Promotion", back_populates="espaces_pedagogiques")
    formateur = relationship("Formateur", back_populates="espaces_pedagogiques")
    travaux = relationship("Travail", back_populates="espace_pedagogique")


class Travail(Base):
    __tablename__ = "travail"

    id_travail = Column(String(100), primary_key=True, nullable=False)
    id_espace = Column(String(100), ForeignKey("espace_pedagogique.id_espace"), nullable=False)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type_travail = Column(SAEnum(TypeTravailEnum), nullable=False)
    date_echeance = Column(DateTime, nullable=False)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    fichier_consigne = Column(String(255), nullable=True)
    note_max = Column(Numeric(3, 1), nullable=False, default=Decimal("20.0"))

    espace_pedagogique = relationship("EspacePedagogique", back_populates="travaux")
    groupes = relationship("GroupeEtudiant", back_populates="travail")
    assignations = relationship("Assignation", back_populates="travail")


class GroupeEtudiant(Base):
    __tablename__ = "groupe_etudiant"

    id_groupe = Column(String(100), primary_key=True, nullable=False)
    id_travail = Column(String(100), ForeignKey("travail.id_travail"), nullable=False)
    nom_groupe = Column(String(255), nullable=False)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)

    travail = relationship("Travail", back_populates="groupes")
    assignations = relationship("Assignation", back_populates="groupe")


class Assignation(Base):
    __tablename__ = "assignation"

    id_assignation = Column(String(100), primary_key=True, nullable=False)
    id_etudiant = Column(String(100), ForeignKey("etudiant.id_etudiant"), nullable=False)
    id_travail = Column(String(100), ForeignKey("travail.id_travail"), nullable=False)
    id_groupe = Column(String(100), ForeignKey("groupe_etudiant.id_groupe"), nullable=True)
    date_assignment = Column(DateTime, nullable=False, default=datetime.utcnow)
    statut = Column(SAEnum(StatutAssignationEnum), nullable=False, default=StatutAssignationEnum.ASSIGNE)

    etudiant = relationship("Etudiant", back_populates="assignations")
    travail = relationship("Travail", back_populates="assignations")
    groupe = relationship("GroupeEtudiant", back_populates="assignations")
    livraisons = relationship("Livraison", back_populates="assignation")


class Livraison(Base):
    __tablename__ = "livraison"

    id_livraison = Column(String(100), primary_key=True, nullable=False)
    id_assignation = Column(String(100), ForeignKey("assignation.id_assignation"), nullable=False)
    chemin_fichier = Column(String(255), nullable=False)
    date_livraison = Column(DateTime, nullable=False, default=datetime.utcnow)
    commentaire = Column(Text, nullable=True)
    note_attribuee = Column(Numeric(3, 1), nullable=True)
    feedback = Column(Text, nullable=True)

    assignation = relationship("Assignation", back_populates="livraisons")


class TentativeConnexion(Base):
    __tablename__ = "tentative_connexion"

    id_tentative = Column(String(100), primary_key=True, nullable=False, default=lambda: secrets.token_urlsafe(16))
    email = Column(String(191), nullable=False)
    date_tentative = Column(DateTime, nullable=False, default=datetime.utcnow)
    succes = Column(Boolean, nullable=False, default=False)