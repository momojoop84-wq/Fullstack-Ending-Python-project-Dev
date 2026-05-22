import json
import os
from typing import List, Dict

# Chemin vers le fichier JSON
# On remonte de 'backend/services' vers 'backend/data'
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "valides.json")

def charger_donnees_json() -> List[Dict]:
    """
    Charge toutes les données du fichier valides.json en mémoire.
    Retourne une liste de dictionnaires.
    """
    if not os.path.exists(JSON_FILE_PATH):
        print(f"⚠️ Fichier JSON introuvable : {JSON_FILE_PATH}")
        return []
    
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            donnees = json.load(f)
        print(f"✅ {len(donnees)} étudiants chargés depuis le JSON.")
        return donnees
    except Exception as e:
        print(f"❌ Erreur lecture JSON : {e}")
        return []

def filtrer_json_par_page(donnees: List[Dict], page: int, page_size: int, offset_db: int):
    """
    Logique de découpage du JSON.
    
    :param donnees: La liste complète du JSON
    :param page: La page demandée par l'utilisateur
    :param page_size: Le nombre de lignes par page
    :param offset_db: Le nombre d'éléments que la BDD a déjà fourni pour cette page
    :return: Une sous-liste du JSON et les métadonnées
    """
    
    # On calcule combien d'éléments il nous manque pour remplir la page
    manquants = page_size - offset_db
    
    if manquants <= 0:
        return [], 0 # La BDD a déjà tout rempli
    
    # Logique simple : On prend le début du JSON pour l'instant
    # (Note : Pour une vraie pagination infinie JSON + DB, c'est complexe.
    # Ici, pour le projet, on va considérer que le JSON est un "complément" initial)
    
    debut_slice = 0
    fin_slice = manquants
    
    donnees_slice = donnees[debut_slice:fin_slice]
    
    return donnees_slice, len(donnees_slice)