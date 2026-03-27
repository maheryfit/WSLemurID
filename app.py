import os

from flask import Flask, g, abort, request
from flask_restx import Api, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from function import get_db, populate_image_lemurs, get_detail_lemur_by_id, get_detail_lemur_by_predict
from static import UPLOAD_FOLDER

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Swagger API config
api = Api(app,
          version='1.0',
          title='Lemur API - Dictionnaire Lémuriens Madagascar',
          description='API pour rechercher et consulter les lémuriens de Madagascar (nom commun, habitat, alimentation, statut IUCN, images)',
          doc='/swagger'  # Swagger UI ici
         )

# Namespace pour organiser
ns_lemurs = api.namespace('lemurs', description='Endpoints lémuriens')

# Modèle réponse lemurien simple (liste)
lemur_simple = ns_lemurs.model('LemurSimple', {
    'id': fields.Integer(description='ID unique'),
    'nom_scientifique': fields.String(required=True, description='Nom scientifique'),
    'nom_commun': fields.String(required=True, description='Nom commun à Madagascar'),
    'iucn_status': fields.String(description='Statut IUCN')
})

# Déclaration du parser pour l'upload dans Swagger
upload_parser = ns_lemurs.parser()
upload_parser.add_argument('lemur', location="files",
                           type=FileStorage, required=True,
                           help='Fichier image (.png, .jpg, .jpeg)')

# Modèle lemurien détaillé (détail)
lemur_detail = ns_lemurs.model('LemurDetail', {
    'id': fields.Integer,
    'nom_scientifique': fields.String(required=True),
    'nom_commun': fields.String(required=True),
    'description': fields.String(description='Description enrichie: activité, sociabilité, taille, poids...'),
    'alimentation': fields.String(description='Régime alimentaire détaillé'),
    'iucn_status': fields.String(description='Statut IUCN: VULNERABLE, EN VOIE DE DISPARITION, EN DANGER CRITIQUE EXTINCTION'),
    'est_protege': fields.Boolean(description='Espèce protégée légalement'),
    'habitations': fields.List(fields.String, description='Noms des habitats/parcs typiques'),
    'images': fields.List(fields.String, description='Chemins des images disponibles')
})

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@ns_lemurs.route('')
@ns_lemurs.response(200, 'Liste des lémuriens', lemur_simple)
@ns_lemurs.param('q', 'Recherche par nom scientifique ou commun', _in='query')
class LemursList(Resource):
    def get(self):
        """Recherche de lémuriens (recherche libre avec ?q=)"""
        db = get_db()
        query_param = request.args.get('q')
        if query_param:
            search = f"%{query_param}%"
            cur = db.execute("""
                SELECT id, nom_scientifique, nom_commun, iucn_status FROM lemur 
                WHERE nom_scientifique LIKE ? OR nom_commun LIKE ?
            """, (search, search))
        else:
            cur = db.execute('SELECT id, nom_scientifique, nom_commun, iucn_status FROM lemur')
        rows = cur.fetchall()
        if rows:
            lemurs = [dict(row) for row in rows]
            return populate_image_lemurs(lemurs=lemurs)
        return [], 200  # Pas d'erreur 200 comme avant

@ns_lemurs.route('/<int:lemur_id>')
@ns_lemurs.response(200, 'Lémurien trouvé', lemur_detail)
@ns_lemurs.response(404, 'Lémurien non trouvé')
class LemurDetail(Resource):
    def get(self, lemur_id):
        """Détail d'un lémurien par ID (habitat, images, description complète)"""
        db = get_db()
        try:
            return get_detail_lemur_by_id(lemur_id, db)
        except Exception as e:
            abort(404, str(e))

@ns_lemurs.route('/predict')
@ns_lemurs.expect(upload_parser)  # Affiche le bouton "Upload" dans Swagger
@ns_lemurs.response(200, 'Image uploadée avec succès')
@ns_lemurs.response(400, 'Fichier manquant ou invalide')
class LemurPredictImage(Resource):
    def post(self):
        """Ajouter une image à un lémurien spécifique et le classer"""
        if 'lemur' not in request.files:
            abort(400, "Image de lémurien introuvable")
        args = upload_parser.parse_args()
        file = args['lemur']
        db = get_db()
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return get_detail_lemur_by_predict(filepath, db)

if __name__ == '__main__':
    print("Routes disponibles:")
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, rule)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
