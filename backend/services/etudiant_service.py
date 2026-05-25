from typing import List, Tuple
from models.schemas import EtudiantResponse
from core.database import get_connection
from services.json_service import charger_donnees_json
import psycopg2

def get_etudiants_hybride(page: int = 1, limit: int = 5) -> dict:
    """
    Récupère les étudiants en mélangeant BDD (Source Principale) et JSON (Source Secondaire).
    """
    conn = get_connection()
    if not conn:
        return {"total": 0, "page": page, "page_size": limit, "data": []}
    
    cursor = conn.cursor()
    donnees_finale = []
    source_tags = []

    try:
        # --- 1. Calcul de l'offset (Le Pointeur) ---
        offset = (page - 1) * limit

        # --- 2. Récupération depuis la BDD (Source Principale) ---
        # On essaie de prendre 'limit' éléments à partir de l'offset
        query = """
            SELECT e.id, e.numero, e.code, e.nom, e.prenom, e.date_naissance, c.nom_classe as classe, e.moyenne_generale 
            FROM etudiant e
            LEFT JOIN classe c ON e.classe_id = c.id
            WHERE e.archive = FALSE 
            ORDER BY e.id 
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, offset))
        rows_db = cursor.fetchall()
        
        # On récupère les noms de colonnes pour créer un dictionnaire propre
        col_names = [desc[0] for desc in cursor.description]

        # Conversion des lignes SQL en dictionnaires
        db_results = []
        for row in rows_db:
            db_dict = dict(zip(col_names, row))
            # On ajoute la source
            db_dict['source'] = 'DB'
            db_dict['date_naissance'] = str(db_dict['date_naissance'])  # Convertir la date en string pour la compatibilité JSON
            # On ajoute les matières (vide pour l'instant dans la BDD simple, on pourrait les joindre)
            db_dict['matieres'] = {} 
            db_results.append(EtudiantResponse(**db_dict))

        donnees_finale.extend(db_results)
        nb_recup_db = len(db_results)

        # --- 3. Logique de Complément (Le JSON) ---
        # Si la BDD n'a pas donné assez de lignes pour remplir la page
        if nb_recup_db < limit:
            manquants = limit - nb_recup_db
            
            # Calcul de l'index de départ dans le JSON
            # Formule : (Page * Limit) - (Total BDD déjà pris)
            # Mais pour simplifier : on prend le JSON à partir de l'offset global si on suppose que le JSON suit la BDD
            # Pour ce projet, on va dire que le JSON complète "à la suite".
            
            # On charge tout le JSON (pour l'instant, c'est acceptable pour un petit fichier)
            json_data = charger_donnees_json()
            
            # Calcul où on en est dans le flux global
            global_index_end = page * limit
            global_index_start = global_index_end - limit
            
            # Si on est dans la zone où la BDD est vide, on doit "sauter" la partie BDD
            # Ici, on fait une hypothèse simple : le JSON est utilisé quand la BDD est vide ou en fin de liste.
            
            # Logique simplifiée pour le projet :
            # On prend les premiers éléments du JSON qui n'ont pas encore été "virtuellement" affichés.
            # Comme on n'a pas de base de données qui stocke "où on en est dans le JSON", 
            # on va simuler en disant : Le JSON commence là où la BDD s'arrête.
            
            # On récupère le total d'élèves en BDD (non archivés)
            cursor.execute("SELECT COUNT(*) FROM etudiant WHERE archive = FALSE")
            total_db_count = cursor.fetchone()[0]
            
            # Calcul de l'index de départ dans la liste JSON
            # Si on est à la page 1 (index 0-4) et que la BDD a 2 élèves.
            # On a pris 2 en BDD. Il nous en manque 3.
            # On prend les 3 premiers du JSON.
            
            # Si on est à la page 2 (index 5-9) et que la BDD a 2 élèves.
            # La page 1 a pris [DB0, DB1, JSON0, JSON1, JSON2].
            # La page 2 doit prendre [JSON3, JSON4, JSON5, JSON6, JSON7].
            # Formule : index_json_debut = (Page * Limit) - total_db_count - (Limit - nb_recup_db_page_prec)
            # C'est complexe sans état (stateless).
            
            # APPROCHE SIMPLIFIÉE POUR VALIDER LE SUJET :
            # Si la BDD ne renvoie rien (ou pas assez), on complète avec le JSON
            # en se basant sur l'index global.
            
            start_json = global_index_start - total_db_count
            
            if start_json < 0:
                # On est dans une page "mixte" (partie BDD, partie JSON)
                start_json = 0 
                # Dans ce cas, on a déjà pris la partie BDD au-dessus.
                # On doit prendre 'manquants' éléments dans le JSON.
                json_slice = json_data[start_json : start_json + manquants]
            else:
                # On est dans une page "Pure JSON" (la BDD est finie)
                # On doit prendre 'limit' éléments dans le JSON
                json_slice = json_data[start_json : start_json + limit]

            # Conversion des données JSON
            for item in json_slice:
                item['source'] = 'JSON' # On TAG la source
                # Pour la compatibilité avec le modèle Pydantic, on s'assure que les champs correspondent
                item['moyenne_generale'] = item.get('moyenne_generale', 0)
                donnees_finale.append(EtudiantResponse(**item))

    except Exception as e:
        print(f"Erreur service étudiant : {e}")
    finally:
        cursor.close()
        conn.close()

    return {
        "total": len(donnees_finale) + (limit if len(donnees_finale) >= limit else 0), # Estimation
        "page": page,
        "page_size": limit,
        "data": donnees_finale
    }