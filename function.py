import os
import sqlite3

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from flask import g
from flask import url_for
from tensorflow.keras import layers, Model, Input
from tensorflow.keras import preprocessing  # ou PIL si image

from static import PIXEL_IMAGE, CHEMIN_POIDS, CHEMIN_IMAGE, DOSSIER_ENTRAINEMENT, URL_PRE_TRAINED_MODEL, DATABASE, \
    DOSSIER_IMAGE


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # sqlite3. Row permet d'accéder aux colonnes par leur nom comme un dictionnaire
        db = g._database = sqlite3.connect(DATABASE)
        db.text_factory = str  # C'est le comportement par défaut (UTF-8)
        db.row_factory = sqlite3.Row
    return db

def remove_file_uploaded(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        print("Fichier supprimé.")
    else:
        print("Le fichier n'existe pas.")

def get_detail_lemur_by_predict(filepath, db):
    nom_scientifique = predict(filepath)
    print(nom_scientifique)
    lemur = get_lemur_by_nom_scientifique(nom_scientifique, db)
    lemur = get_habitation_by_lemur(lemur, db)
    remove_file_uploaded(filepath)
    return populate_images_lemur(lemur)

def get_lemur_by_nom_scientifique(nom_scientifique, db):
    cur = db.execute("""
        SELECT lem.*
        FROM lemur lem
        WHERE lem.nom_scientifique = ? COLLATE NOCASE
    """, (nom_scientifique,))
    lemur = cur.fetchone()
    if lemur is None:
        raise Exception("Lémurien non trouvé")
    return dict(lemur)

def get_lemur_by_id(lemur_id, db):
    cur = db.execute("""
        SELECT lem.*
        FROM lemur lem
        WHERE lem.id = ?
    """, (lemur_id,))
    lemur = cur.fetchone()
    if lemur is None:
        raise Exception("Lémurien non trouvé")
    return dict(lemur)

def get_detail_lemur_by_id(lemur_id, db):
    lemur = get_lemur_by_id(lemur_id, db)
    lemur = get_habitation_by_lemur(lemur, db)
    return populate_images_lemur(lemur)

def populate_images_lemur(lemur):
    images = get_images_from_nom_lemur(lemur)
    lemur["images"] = images[0:6]
    return lemur

def get_habitation_by_lemur(lemur, database):
    cur = database.execute("""
        SELECT hab.nom_habitation, hab.latitude, hab.longitude FROM habitation hab
        LEFT JOIN main.lemur_habitation lh on hab.id = lh.habitation_id
        WHERE lh.lemur_id = ?
    """, (lemur["id"],))
    rows = cur.fetchall()
    if rows:
        lemur["habitations"] = [dict(row) for row in rows]
    return lemur


def populate_image_lemurs(lemurs):
    for lemur in lemurs:
        lemur["image"] = get_one_image_from_nom_lemur(lemur)
    return lemurs

def get_one_image_from_nom_lemur(lemur):
    images = get_images_from_nom_lemur(lemur)
    return images[0] if images else None

def get_images_from_nom_lemur(lemur):
    nom_scientifique = str(lemur["nom_scientifique"]).lower()
    chemin_dossier_lemur = os.path.join("static", DOSSIER_IMAGE, nom_scientifique)
    # Vérifie si le dossier existe avant de lister les fichiers
    if os.path.exists(chemin_dossier_lemur):
        return [ url_for('static', filename=f"{DOSSIER_IMAGE}/{nom_scientifique}/{fichier}", _external=True) for fichier in os.listdir(chemin_dossier_lemur) ]
    return None

def get_classes():
    dossiers_bruts = [d for d in os.listdir(DOSSIER_ENTRAINEMENT) if os.path.isdir(os.path.join(DOSSIER_ENTRAINEMENT, d))]
    return sorted(dossiers_bruts)

def create_model():  # Récrée le modèle complet
    base_model = hub.KerasLayer(URL_PRE_TRAINED_MODEL, trainable=False)
    NOMBRE_DE_CLASSES = len(get_classes())

    @tf.keras.saving.register_keras_serializable()
    def hub_wrapper(inputs):
        return base_model(inputs, training=False)

    # 1. On définit le tenseur d'entrée X
    entrees = Input(shape=(PIXEL_IMAGE, PIXEL_IMAGE, 3), dtype="float32")

    # 2. On applique les fonctions mathématiques f(X) successivement
    x = layers.RandomFlip("horizontal")(entrees)
    x = layers.RandomRotation(0.2)(x)
    x = layers.RandomContrast(0.2)(x)
    x = layers.RandomBrightness(0.2)(x)
    # ... autres augmentations ...
    x = layers.GaussianNoise(0.1)(x)
    x = layers.Rescaling(1. / 127.5, offset=-1)(x)
    # importation du modèle pré-entrainé
    x = layers.Lambda(hub_wrapper)(x)
    # x = GlobalAveragePooling2D()(x) # Indispensable pour aplatir les tenseurs 3D en 1D
    x = layers.Dropout(0.2)(x)

    # 3. La sortie Y
    sorties = layers.Dense(NOMBRE_DE_CLASSES, activation='softmax')(x)

    # 4. On scelle le modèle
    model = Model(inputs=entrees, outputs=sorties)

    # Charge UNIQUEMENT les poids (pas l'architecture)
    model.load_weights(CHEMIN_POIDS)  # Sauvegarde model.save_weights("poids.h5") dans Colab
    return model

def predict(img_path):
    noms_classes = get_classes()
    model = create_model()  # Récrée à chaque fois
    img = preprocessing.image.load_img(img_path, target_size=(PIXEL_IMAGE, PIXEL_IMAGE))
    img_array = preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    predictions = model.predict(img_array)
    index_gagnant = np.argmax(predictions[0])
    pourcentage_confiance = predictions[0][index_gagnant] * 100
    classe_predite = noms_classes[index_gagnant]
    print(f"\n🐒 Résultat de l'IA : C'est un '{classe_predite}' à {pourcentage_confiance:.2f}%")
    return classe_predite


