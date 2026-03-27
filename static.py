import os

UPLOAD_FOLDER = 'static/images_lemuriens_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DOSSIER_ENTRAINEMENT = os.path.join("static", "dataset_lemuriens_reduce")
DOSSIER_IMAGE = "dataset_lemuriens_reduce"
DATABASE = os.path.join("database", "database.db")
CHEMIN_MODELE = os.path.join("model", "model_classification_lemur.keras")
CHEMIN_IMAGE = "217cff35-3e42-41d6-b640-111a516619e9.jpg"
PIXEL_IMAGE = 299
CHEMIN_POIDS = os.path.join("model", "model.weights.h5")
URL_PRE_TRAINED_MODEL = "https://www.kaggle.com/models/google/inception-v3/TensorFlow2/inaturalist-inception-v3-feature-vector/2"