from pydantic import BaseModel, Field
from typing import Dict, Optional, List

# --- Modèle pour une Matière et sa Note ---
class MatiereNote(BaseModel):
    nom_matiere: str
    moyenne: float = Field(..., ge=0, le=20) # La note doit être entre 0 et 20

# --- Modèle Étudiant (Le cœur du système) ---
class EtudiantBase(BaseModel):
    """Structure de base d'un étudiant, commune à l'affichage et la création"""
    numero: str = Field(..., description="Numéro unique de l'étudiant")
    code: str = Field(..., min_length=6, max_length=6, description="Code unique (ex: ABC123)")
    nom: str
    prenom: str
    date_naissance: str # On le garde en string "JJ/MM/AAAA" comme dans le JSON pour l'instant
    classe: str
    matieres: Dict[str, float] = {} # Dictionnaire { "Maths": 12.5, "Français": 14 }
    moyenne_generale: float

# --- Modèle pour la Création (Hérite de Base) ---
class EtudiantCreate(EtudiantBase):
    """Utilisé quand on reçoit des données pour créer un étudiant"""
    pass

# --- Modèle pour la Réponse (Hérite de Base) ---
class EtudiantResponse(EtudiantBase):
    """Utilisé quand on envoie des données au Frontend"""
    id: Optional[int] = None # L'ID est généré par la BDD (PostgreSQL), donc il est optionnel ici
    source: str = "DB" # Par défaut, on vient de la BDD
    
    class Config:
        # Permet de convertir les objets de la BDD (qui sont des tuples ou dicts) en ces modèles Pydantic
        from_attributes = True 

# --- Modèle pour la Pagination ---
class EtudiantListResponse(BaseModel):
    """Structure de la réponse paginée"""
    total: int        # Nombre total d'étudiants disponibles (DB + JSON)
    page: int         # Page actuelle
    page_size: int    # Nombre d'éléments par page
    data: List[EtudiantResponse] # La liste des étudiants