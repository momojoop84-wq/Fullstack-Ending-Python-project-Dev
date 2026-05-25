from fastapi import APIRouter, Query
from models.schemas import EtudiantListResponse
from services.etudiant_service import get_etudiants_hybride

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