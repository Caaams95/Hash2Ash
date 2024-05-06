from datetime import datetime
from hash2ash import db, login_manager # Importation de l'instance de la base de données et de l'instance de login_manager
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

    def __repr__(self):
        return f"Users('{self.username}', '{self.email}', '{self.role}')"
    def get_id(self):
        return str(self.id_user)
    
class Instances(db.Model):
    id_instance = db.Column(db.Integer, primary_key=True)
    type_instance = db.Column(db.String(50), nullable=False)
    id_arch = db.Column(db.String(50), nullable=True)
    price_provider = db.Column(db.Float, nullable=False)
    price_hash2ash = db.Column(db.Float, nullable=False)
    hashes = db.relationship('Hashes', backref='instance', lazy=True)

    def __repr__(self):
        return f"instances('{self.type_instance}', '{self.id_arch}', '{self.price_provider}', '{self.price_hash2ash}')"
    
class Hashes(db.Model):
    id_hash = db.Column(db.Integer, primary_key=True)
    fk_id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    fk_id_instance = db.Column(db.Integer, db.ForeignKey('instances.id_instance'), nullable=True)
    date_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(60), nullable=False)
    hash = db.Column(db.String(140), nullable=False)
    power = db.Column(db.String(20), nullable=False)
    mask = db.Column(db.String(140), nullable=False)
    algorithm = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(140), nullable=True) ## Hash déchiffré
    status = db.Column(db.String(20), nullable=False)
    provider = db.Column(db.String(20), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


    def __repr__(self):
        return f"Hashes('{self.fk_id_user}', '{self.fk_id_instance}', '{self.date_start}', '{self.date_end}', '{self.name}', '{self.hash}', '{self.algorithm}', '{self.result}', '{self.status}', '{self.provider}', '{self.progress}', '{self.price}')"
