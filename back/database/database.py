from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# TODO: Remplacez par votre chaîne de connexion MySQL
# Format: mysql+pymysql://utilisateur:motdepasse@hote/nom_base_de_donnees
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/genie_logiciel"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
