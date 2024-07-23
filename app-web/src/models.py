from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # Importation de la classe Serializer pour générer des tokens
from src import db, login_manager, app # Importation de l'instance de la base de données et de l'instance de login_manager
from flask_login import UserMixin   # Importation de la classe UserMixin qui contient les méthodes de base pour gérer les utilisateurs

@login_manager.user_loader # Fonction pour charger un utilisateur 
def get_user(id_user):
    return Users.query.get(int(id_user))

class Users(db.Model, UserMixin):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    hashes = db.relationship('Hashes', backref='user', lazy=True) 

    def get_reset_token(self, expires_sec=1800): # Méthode pour générer un token de réinitialisation de mot de passe qui expire dans 1800 secondes = 30 minutes
        s = Serializer(app.config['SECRET_KEY'], expires_sec)  
        return s.dumps({'user_id': self.id_user}).decode('utf-8') # Retourne le token encodé en utf-8

    
    @staticmethod
    def verify_reset_token(token): # Méthode pour vérifier le token de réinitialisation de mot de passe
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)
    
    def __repr__(self):
        return f"Users('{self.username}', '{self.email}', '{self.role}')"
    def get_id(self):
        return str(self.id_user)
    
class Instances(db.Model):
    id_instance = db.Column(db.Integer, primary_key=True)
    type_instance = db.Column(db.String(50), nullable=False)
    id_arch = db.Column(db.String(50), nullable=True) ## id_provider
    price_hash2ash = db.Column(db.Float, nullable=False)
    date_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_shutdown = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    price_total = db.Column(db.Float, nullable=True)
    fk_id_hash = db.Column(db.Integer, nullable=True)
    ip = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"instances('{self.type_instance}', '{self.id_arch}', '{self.price_provider}', '{self.date_start}', '{self.date_shutdown}','{self.price_hash2ash}', '{self.status}', '{self.price_total}')"
    
class Hashes(db.Model):
    id_hash = db.Column(db.Integer, primary_key=True)
    fk_id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    fk_id_instance = db.Column(db.Integer, db.ForeignKey('instances.id_instance', use_alter=True), nullable=True)
    date_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(60), nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    power = db.Column(db.String(20), nullable=False)
    wordlist = db.Column(db.String(140), nullable=True)
    custom_wordlist = db.Column(db.String(140), nullable=True)
    algorithm = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(140), nullable=True) ## Hash déchiffré
    status = db.Column(db.String(20), nullable=False)
    provider = db.Column(db.String(20), nullable=False)
    progress = db.Column(db.String(50), nullable=True, default='0/0 (0.0%)')
    price = db.Column(db.Float, nullable=False)
    time_estimated = db.Column(db.String(60), nullable=True)
    hash_per_second = db.Column(db.String(20), nullable=True, default='0 H/s')
    price_limit = db.Column(db.Float, nullable=True)


    def __repr__(self):
        return f"Hashes('{self.name}', '{self.hash}', '{self.power}', '{self.wordlist}', '{self.custom_wordlist}', '{self.algorithm}', '{self.result}', '{self.status}', '{self.progress}', '{self.price}', '{self.time_estimated}', '{self.hash_per_second}', '{self.price_limit}', '{self.provider}')"

class Conf_instance(db.Model):
    id_conf = db.Column(db.Integer, primary_key=True)
    power = db.Column(db.String(20), nullable=False)
    type_provider = db.Column(db.String(20), nullable=False)
    provider = db.Column(db.String(20), nullable=True)
    price_provider = db.Column(db.Float, nullable=True)
    price_hash2ash = db.Column(db.Float, nullable=True)
    profit_percentage = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Conf_instance('{self.power}', '{self.type_provider}', '{self.provider}', '{self.price_provider}', '{self.price_hash2ash}', '{self.profit_percentage}')"
