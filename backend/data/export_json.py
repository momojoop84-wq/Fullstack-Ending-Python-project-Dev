import csv
import json
import os
from datetime import datetime

# --- COPIE DE TES CLASSES ET MÉTHODES DE VALIDATION ---

class Etudiant:
    def __init__(self, nom, prenom, code, date_naiss, classe, age, numero):
        self.nom = nom
        self.prenom = prenom
        self.code = code
        self.date_naiss = date_naiss
        self.notes = {} 
        self.classe = classe 
        self.age = age
        self.numero = numero # Important pour le nouveau projet

    def to_dict(self):
        """Convertit l'objet en dictionnaire pour le JSON"""
        return {
            "code": self.code,
            "numero": self.numero,
            "prenom": self.prenom,
            "nom": self.nom,
            "date_naissance": self.date_naiss,
            "classe": self.classe,
            "matieres": self.notes, # Pour simplifier, on stocke les notes ici
            "moyenne_generale": round(sum(self.notes.values()) / len(self.notes), 2) if self.notes else 0
        }

class GestionDonnees:
    def __init__(self):
        self.liste_valides = []
        self.liste_invalides = []

    # --- (Je reprends tes briques de validation ici pour faire fonctionner le script) ---
    def code_est_valide(self, code):
        return len(code) == 6 and code[:3].isalpha() and code[:3].isupper() and code[3:].isnumeric()

    def identite_est_valide(self, nom, prenom):
        return len(nom) >= 2 and nom[0].isalpha() and len(prenom) >= 3 and prenom[0].isalpha()

    def classe_est_valide(self, classe):
        c = classe.upper().replace(" ", "")
        if len(c) < 2: return False
        propre = c[0] + c[-1]
        if propre[0] in "6543" and propre[1] in "ABCD": return propre
        return False
    
    def parser_notes(self, chaine_globale):
        dictionnaire_moyennes = {}
        matieres = chaine_globale.split("#")
        for m in matieres:
            if "[" in m and "]" in m:
                nom_matiere, reste = m.split("[")
                notes_brutes = reste.replace("]", "")
                parties = notes_brutes.split(":")
                if len(parties) == 2:
                    dev_str = parties[0].split("|")
                    ex_str = parties[1]
                    try:
                        devoirs = [float(d.replace(",", ".")) for d in dev_str]
                        examen = float(ex_str.replace(",", "."))
                        if 0 <= examen <= 20 and all(0 <= d <= 20 for d in devoirs):
                            moy_dev = sum(devoirs) / len(devoirs)
                            moyenne_finale = (moy_dev + 2 * examen) / 3
                            dictionnaire_moyennes[nom_matiere] = round(moyenne_finale, 2)
                    except ValueError: continue
        return dictionnaire_moyennes

    def date_est_valide(self, date_brute):
        for sep in [" ", "-", ".", ":", "_",",","|"]: date_brute = date_brute.replace(sep, "/")
        parties = date_brute.split("/")
        if len(parties) != 3: return False
        try:
            mois_dict = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
            m_saisi = parties[1].lower()
            m = mois_dict[m_saisi] if m_saisi in mois_dict else int(parties[1])
            j = int(parties[0])
            a = int(parties[2])
            if a < 100: a += 1900 if a > 25 else 2000
            if not (1 <= m <= 12 and 1900 <= a <= 2025): return False
            jours_max = 31
            if m in [4, 6, 9, 11]: jours_max = 30
            elif m == 2: jours_max = 29 if (a % 4 == 0 and a % 100 != 0) or (a % 400 == 0) else 28
            if 1 <= j <= jours_max: return f"{j:02d}/{m:02d}/{a}"
            return False
        except ValueError: return False

    def calculer_age(self, date_propre):
        return datetime.now().year - int(date_propre.split("/")[2])

    # --- MÉTHODE DE CHARGEMENT ---

    def charger_fichier(self, chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as file:
                lecteur = csv.DictReader(file, delimiter=';')
                for index, ligne in enumerate(lecteur):
                    # On génère un numéro unique basé sur l'index du CSV si pas présent
                    numero = ligne.get('Numero', str(index + 1)) 
                    
                    res_date = self.date_est_valide(ligne['Date de naissance'])
                    res_classe = self.classe_est_valide(ligne['Classe'])
                    code_ok = self.code_est_valide(ligne['CODE'])
                    moyennes_dict = self.parser_notes(ligne['Note'])
                    nom_ok = self.identite_est_valide(ligne['Nom'], ligne['Prénom'])
                    
                    if all([res_date, res_classe, code_ok, moyennes_dict, nom_ok]):
                        age_calcule = self.calculer_age(res_date) 
                        nouv_etu = Etudiant(ligne['Nom'], ligne['Prénom'], ligne['CODE'], res_date, res_classe, age_calcule, numero)
                        nouv_etu.notes = moyennes_dict
                        self.liste_valides.append(nouv_etu)
                    else:
                        # Pour l'invalides.json, on garde le format dictionnaire
                        ligne['numero'] = numero
                        self.liste_invalides.append(ligne)
            print(f"✅ Analyse terminée : {len(self.liste_valides)} valides, {len(self.liste_invalides)} invalides.")
        except FileNotFoundError:
            print("❌ Erreur : Fichier CSV introuvable.")

# --- NOUVELLE FONCTION D'EXPORT ---

def exporter_json(gestion):
    # 1. Export Valides
    valides_dict = [e.to_dict() for e in gestion.liste_valides]
    with open("valides.json", "w", encoding="utf-8") as f:
        json.dump(valides_dict, f, indent=4, ensure_ascii=False)
    print("📄 Fichier 'valides.json' créé.")

    # 2. Export Invalides
    with open("invalides.json", "w", encoding="utf-8") as f:
        json.dump(gestion.liste_invalides, f, indent=4, ensure_ascii=False)
    print("📄 Fichier 'invalides.json' créé.")

# --- EXÉCUTION ---
if __name__ == "__main__":
    gestion = GestionDonnees()
    
    # CHANGE LE NOM DU FICHIER CI-DESSOUS si le tien est différent
    nom_csv = "Donnees_Projet_Python_Dev_Data.csv" 
    
    if os.path.exists(nom_csv):
        gestion.charger_fichier(nom_csv)
        exporter_json(gestion)
    else:
        print(f"⚠️ Le fichier {nom_csv} n'existe pas dans ce dossier.")