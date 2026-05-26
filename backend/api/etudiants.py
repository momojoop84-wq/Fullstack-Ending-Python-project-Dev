from fastapi import APIRouter, Query
from models.schemas import EtudiantListResponse
from services.etudiant_service import get_etudiants_hybride
from pydantic import BaseModel
from typing import List 
from core.database import get_connection

router = APIRouter()

@router.get("/etudiants", response_model=EtudiantListResponse)
def lire_etudiants(
    page: int = Query(1, ge=1, description="Numéro de la page"),
    limit: int = Query(5, ge=1, le=100, description="Nombre d'éléments par page")
):
    """
    Endpoint principal pour récupérer la liste des étudiants.
    Fusionne les données de la Base de Données et du fichier JSON.
    """
    resultats = get_etudiants_hybride(page=page, limit=limit)
    
    return resultats

# --- Endpoint pour importer les étudiants depuis le JSON vers la BDD ---
class ImportRequest(BaseModel):
    numeros: List[str]  # Liste des numéros d'étudiants à importer depuis le JSON

@router.post("/importer") 
def importer_etudiants(request: ImportRequest):
    """
    Importe une liste d'étudiants depuis le JSON vers la BDD.
    Vérifie les doublons via le champ 'numero'.
    """
    from services.import_service import importer_json_vers_bdd
    
    resultat = importer_json_vers_bdd(request.numeros)
    
    return {
        "message": f"Importation terminée.",
        "details": resultat
    }