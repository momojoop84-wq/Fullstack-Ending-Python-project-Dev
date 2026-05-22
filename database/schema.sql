-- 1. Suppression des tables si elles existent (pour pouvoir relancer le script sans erreur)
DROP TABLE IF EXISTS devoir;
DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS etudiant;
DROP TABLE IF EXISTS classe;
DROP TABLE IF EXISTS matiere;

-- 2. Création de la table CLASSE
CREATE TABLE classe (
    id SERIAL PRIMARY KEY,             -- ID unique généré automatiquement (1, 2, 3...)
    nom_classe VARCHAR(10) UNIQUE NOT NULL -- Ex: '6A', '3B'. UNIQUE interdit les doublons de classes.
);

-- 3. Création de la table MATIERE
CREATE TABLE matiere (
    id SERIAL PRIMARY KEY,
    nom_matiere VARCHAR(50) UNIQUE NOT NULL -- Ex: 'Mathématiques', 'Histoire'
);

-- 4. Création de la table ETUDIANT (La plus importante)
CREATE TABLE etudiant (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) UNIQUE NOT NULL, -- Le numéro unique identifiant l'élève (Clé métier)
    code VARCHAR(6),                   -- Ex: ABC123
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE,
    classe_id INTEGER,                  -- Clé étrangère vers la table classe
    archive BOOLEAN DEFAULT FALSE,      -- FALSE = actif, TRUE = archivé
    FOREIGN KEY (classe_id) REFERENCES classe(id) -- Lien entre l'élève et sa classe
);

-- 5. Création de la table NOTE (Liaison Étudiant - Matière)
CREATE TABLE note (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER NOT NULL,
    matiere_id INTEGER NOT NULL,
    moyenne_generale DECIMAL(4,2),     -- La moyenne calculée (ex: 14.50)
    FOREIGN KEY (etudiant_id) REFERENCES etudiant(id) ON DELETE CASCADE, -- Si on supprime l'élève, on supprime ses notes
    FOREIGN KEY (matiere_id) REFERENCES matiere(id)
);

-- 6. Création de la table DEVOIR (Détail des notes)
CREATE TABLE devoir (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL,
    valeur DECIMAL(4,2),               -- La note chiffrée
    type_devoir VARCHAR(20)            -- 'devoir' ou 'examen'
);