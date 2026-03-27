CREATE TABLE lemur (
    id INT PRIMARY KEY NOT NULL,
    nom_scientifique VARCHAR(50) NOT NULL UNIQUE,
    nom_commun VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    alimentation TEXT NOT NULL,
    iucn_status VARCHAR (40) NOT NULL CHECK ( iucn_status IN ('VULNERABLE', 'EN VOIE DE DISPARITION', 'EN DANGER CRITIQUE EXTINCTION')),
    est_protege BOOLEAN NOT NULL
);
CREATE INDEX nom_scientifique_index ON lemur (nom_scientifique);
CREATE INDEX nom_commun_index ON lemur (nom_commun);

CREATE TABLE habitation (
    id INT PRIMARY KEY NOT NULL,
    latitude NUMERIC (12, 8) NOT NULL,
    longitude NUMERIC (12, 8) NOT NULL,
    nom_habitation VARCHAR (90) NOT NULL UNIQUE
);

CREATE TABLE lemur_habitation (
    habitation_id INT NOT NULL,
    lemur_id INT NOT NULL,
    FOREIGN KEY (habitation_id) REFERENCES habitation(id),
    FOREIGN KEY (lemur_id) REFERENCES lemur(id),
    UNIQUE (habitation_id, lemur_id)
);