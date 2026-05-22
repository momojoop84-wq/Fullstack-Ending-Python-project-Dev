import sys
import os

# On ajoute le dossier parent au path pour pouvoir importer les services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.json_service import charger_donnees_json

if __name__ == "__main__":
    data = charger_donnees_json()
    if data:
        print(f"Premier étudiant du JSON : {data[0]}")
        print("Lecture JSON OK.")
    else:
        print("Erreur ou fichier vide.")