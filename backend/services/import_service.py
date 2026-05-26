from core.database import get_connection
from services.json_service import charger_donnees_json
from datetime import datetime

def importer_json_vers_bdd(liste_numeros):
    conn = get_connection()
    if not conn:
        return {"error": "Pas de connexion BDD"}
    
    cursor = conn.cursor()
    json_data = charger_donnees_json()
    
    # On crée un dictionnaire rapide pour accéder aux données via le numero
    map_json = {item['numero']: item for item in json_data}
    
    importes = 0
    doublons = 0
    erreurs = 0
    
    try:
        for numero in liste_numeros:
            if numero not in map_json:
                erreurs += 1
                continue
            
            # 1. Vérifier les doublons en BDD
            cursor.execute("SELECT id FROM etudiant WHERE numero = %s", (numero,))
            if cursor.fetchone():
                doublons += 1
                continue
            
            # 2. Récupérer les données du JSON
            data = map_json[numero]
            
            # --- CORRECTION DATE : Convertir JJ/MM/AAAA -> AAAA-MM-JJ ---
            date_str = data.get('date_naissance', '01/01/2000')
            try:
                # On transforme "15/05/2010" en objet date, puis en string "2010-05-10"
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                date_sql = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                date_sql = None # Si la date est invalide, on met NULL
            
            # --- CORRECTION CLASSE : Trouver l'ID de la classe ---
            nom_classe = data.get('classe', 'Inconnu')
            classe_id = None
            
            cursor.execute("SELECT id FROM classe WHERE nom_classe = %s", (nom_classe,))
            classe_row = cursor.fetchone()
            
            if classe_row:
                # La classe existe, on prend son ID
                classe_id = classe_row[0]
            else:
                # La classe n'existe pas encore en BDD, on la crée
                cursor.execute("INSERT INTO classe (nom_classe) VALUES (%s) RETURNING id", (nom_classe,))
                classe_id = cursor.fetchone()[0]
            
            # 3. Insérer l'étudiant
            query_insert = """
                INSERT INTO etudiant (numero, code, nom, prenom, date_naissance, classe_id, moyenne_generale, archive)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            """
            
            cursor.execute(query_insert, (
                data['numero'],
                data['code'],
                data['nom'],
                data['prenom'],
                date_sql,                 # Date au bon format 
                classe_id,                 # ID de la classe (nombre entier)
                data.get('moyenne_generale', 0)
            ))
            
            importes += 1
            
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Erreur import : {e}")
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()
        
    return {
        "importes": importes,
        "doublons": doublons,
        "erreurs": erreurs
    }