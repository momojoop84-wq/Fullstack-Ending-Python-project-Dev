from core.database import get_connection
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

@app.get("/stats")
def get_stats():
    """
    Retourne les statistiques globales pour le Dashboard.
    """
    conn = get_connection()
    if not conn:
        return {"error": "Pas de connexion"}
    
    cursor = conn.cursor()
    stats = {}

    try:
        # 1. Nombre d'étudiants en DB
        cursor.execute("SELECT COUNT(*) FROM etudiant WHERE archive = FALSE")
        stats["total_db"] = cursor.fetchone()[0]

        # 2. Nombre d'étudiants dans le JSON (on lit le fichier)
        from services.json_service import charger_donnees_json
        json_data = charger_donnees_json()
        stats["total_json"] = len(json_data)

        # 3. Répartition par Classe (depuis la BDD)
        cursor.execute("""
            SELECT c.nom_classe, COUNT(e.id) as count 
            FROM etudiant e
            JOIN classe c ON e.classe_id = c.id
            WHERE e.archive = FALSE
            GROUP BY c.nom_classe
            ORDER BY count DESC
        """)
        classes = cursor.fetchall()
        stats["repartition_classe"] = [{"classe": row[0], "count": row[1]} for row in classes]

        # 4. Moyenne générale par classe
        cursor.execute("""
            SELECT c.nom_classe, AVG(e.moyenne_generale) as moy 
            FROM etudiant e
            JOIN classe c ON e.classe_id = c.id
            WHERE e.archive = FALSE
            GROUP BY c.nom_classe
            ORDER BY moy DESC
        """)
        moyennes = cursor.fetchall()
        stats["moyenne_par_classe"] = [{"classe": row[0], "moyenne": round(row[1], 2)} for row in moyennes]

    except Exception as e:
        print(f"Erreur stats : {e}")
    finally:
        cursor.close()
        conn.close()
        
    return stats