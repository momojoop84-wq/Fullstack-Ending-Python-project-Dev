from fastapi import FastAPI
from api.etudiants import router as etudiant_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API DevData Projet", version="1.0.0") 
# On configure le CORS pour autoriser les requêtes depuis n'importe quelle origine (utile pour le développement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise tous les origines (pour le dev)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

# On inclut le routeur des étudiants
app.include_router(etudiant_router, tags=["Etudiants"]) 

@app.get("/")
def racine():
    return {"message": "Bienvenue sur l'API DevData. Allez voir /docs pour l'interface Swagger."}

@app.get("/health")
def health_check():
    return {"status": "OK"}