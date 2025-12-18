import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, get_db
from main import app

# Base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    """Crée la base de données de test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db):
    """Session de base de données pour les tests"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    """Client de test avec base de données mockée"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_formateur_data():
    """Données de test pour création formateur Mandatory"""
    return {
        "email": "formateur.test@example.com",
        "nom": "Dupont",
        "prenom": "Jean",
        "specialite": "Mathématiques"
    }

@pytest.fixture
def sample_etudiant_data():
    """Données de test pour création étudiant"""
    return {
        "email": "etudiant.test@example.com",
        "nom": "Martin",
        "prenom": "Sophie",
        "id_promotion": "PROMO_2024"
    }

@pytest.fixture
def sample_de_user():
    """Utilisateur DE de test"""
    from models import Utilisateur, RoleEnum
    
    return {
        "identifiant": "de_principal",
        "email": "de@genielogiciel.com",
        "nom": "Directeur",
        "prenom": "Établissement",
        "role": RoleEnum.DE,
        "actif": True,
        "mot_de_passe_temporaire": False
    }
