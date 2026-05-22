import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# On charge les variables du fichier .env
load_dotenv()

def get_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
        # Pour le debug, on peut commenter la ligne suivante une fois que ça marche
        #print("✅ Connexion à PostgreSQL réussie (via .env) !") 
        return connection

    except (Exception, Error) as error:
        print(f"❌ Erreur de connexion : {error}")
        return None

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Test de connexion sécurisée réussi !")
        conn.close()