from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
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

    id_utilisateur = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(191), unique=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    actif = Column(Boolean, nullable=False, default=True)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    token_activation = Column(String(255), nullable=True)
    date_expiration_token = Column(DateTime, nullable=True)

    etudiant = relationship("Etudiant", back_populates="utilisateur", uselist=False)
    formateur = relationship("Formateur", back_populates="utilisateur", uselist=False)


class Formation(Base):
    __tablename__ = "formation"

    id_formation = Column(Integer, primary_key=True, autoincrement=True)
    nom_formation = Column(String(191), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)

    promotions = relationship("Promotion", back_populates="formation")


class Promotion(Base):
    __tablename__ = "promotion"

    id_promotion = Column(Integer, primary_key=True, autoincrement=True)
    id_formation = Column(Integer, ForeignKey("formation.id_formation"), nullable=False)
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

    id_etudiant = Column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur = Column(Integer, ForeignKey("utilisateur.id_utilisateur"), unique=True, nullable=False)
    matricule = Column(String(100), unique=True, nullable=False)
    id_promotion = Column(Integer, ForeignKey("promotion.id_promotion"), nullable=False)
    date_inscription = Column(Date, nullable=False)
    statut = Column(SAEnum(StatutEtudiantEnum), nullable=False, default=StatutEtudiantEnum.ACTIF)

    utilisateur = relationship("Utilisateur", back_populates="etudiant")
    promotion = relationship("Promotion", back_populates="etudiants")
    assignations = relationship("Assignation", back_populates="etudiant")


class Formateur(Base):
    __tablename__ = "formateur"

    id_formateur = Column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur = Column(Integer, ForeignKey("utilisateur.id_utilisateur"), unique=True, nullable=False)
    numero_employe = Column(String(100), nullable=True)
    specialite = Column(String(255), nullable=True)

    utilisateur = relationship("Utilisateur", back_populates="formateur")
    espaces_pedagogiques = relationship("EspacePedagogique", back_populates="formateur")


class EspacePedagogique(Base):
    __tablename__ = "espace_pedagogique"

    id_espace = Column(Integer, primary_key=True, autoincrement=True)
    id_promotion = Column(Integer, ForeignKey("promotion.id_promotion"), nullable=False)
    nom_matiere = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)
    id_formateur = Column(Integer, ForeignKey("formateur.id_formateur"), nullable=False)
    code_acces = Column(String(100), nullable=True)

    promotion = relationship("Promotion", back_populates="espaces_pedagogiques")
    formateur = relationship("Formateur", back_populates="espaces_pedagogiques")
    travaux = relationship("Travail", back_populates="espace_pedagogique")


class Travail(Base):
    __tablename__ = "travail"

    id_travail = Column(Integer, primary_key=True, autoincrement=True)
    id_espace = Column(Integer, ForeignKey("espace_pedagogique.id_espace"), nullable=False)
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

    id_groupe = Column(Integer, primary_key=True, autoincrement=True)
    id_travail = Column(Integer, ForeignKey("travail.id_travail"), nullable=False)
    nom_groupe = Column(String(255), nullable=False)
    date_creation = Column(DateTime, nullable=False, default=datetime.utcnow)

    travail = relationship("Travail", back_populates="groupes")
    assignations = relationship("Assignation", back_populates="groupe")


class Assignation(Base):
    __tablename__ = "assignation"

    id_assignation = Column(Integer, primary_key=True, autoincrement=True)
    id_etudiant = Column(Integer, ForeignKey("etudiant.id_etudiant"), nullable=False)
    id_travail = Column(Integer, ForeignKey("travail.id_travail"), nullable=False)
    id_groupe = Column(Integer, ForeignKey("groupe_etudiant.id_groupe"), nullable=True)
    date_assignment = Column(DateTime, nullable=False, default=datetime.utcnow)
    statut = Column(SAEnum(StatutAssignationEnum), nullable=False, default=StatutAssignationEnum.ASSIGNE)

    etudiant = relationship("Etudiant", back_populates="assignations")
    travail = relationship("Travail", back_populates="assignations")
    groupe = relationship("GroupeEtudiant", back_populates="assignations")
    livraisons = relationship("Livraison", back_populates="assignation")


class Livraison(Base):
    __tablename__ = "livraison"

    id_livraison = Column(Integer, primary_key=True, autoincrement=True)
    id_assignation = Column(Integer, ForeignKey("assignation.id_assignation"), nullable=False)
    chemin_fichier = Column(String(255), nullable=False)
    date_livraison = Column(DateTime, nullable=False, default=datetime.utcnow)
    commentaire = Column(Text, nullable=True)
    note_attribuee = Column(Numeric(3, 1), nullable=True)
    feedback = Column(Text, nullable=True)

    assignation = relationship("Assignation", back_populates="livraisons")
