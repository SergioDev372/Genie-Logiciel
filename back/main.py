from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
import models  # ensure all models are imported so tables are created
from routes import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes d'authentification
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
def home():
    return {"message": "FastAPI fonctionne 🎉"}
