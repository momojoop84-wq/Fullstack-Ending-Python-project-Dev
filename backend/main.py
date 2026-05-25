from fastapi import FastAPI
from api.etudiants import router as etudiant_router

app = FastAPI(title="API DevData Projet", version="1.0.0")

# On inclut le routeur des étudiants
app.include_router(etudiant_router, tags=["Etudiants"])

@app.get("/")
def racine():
    return {"message": "Bienvenue sur l'API DevData. Allez voir /docs pour l'interface Swagger."}

@app.get("/health")
def health_check():
    return {"status": "OK"}