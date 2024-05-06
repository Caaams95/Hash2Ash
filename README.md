### Dépendances necessaires

```bash
pip install flask
pip install flask-wtf
pip install email_validator
pip install flask-sqlalchemy
pip install flask-bcrypt
pip install flask-login
```
### Lancer le serveur web
```bash
cd hash2ash/app/
python3 run.py
```
### Compte Admin

email: admin@demo.com
password: admin

### Compte Utilisateur

Pour voir l'expérieur utilisateur créer toi un compte sur la page login


### Si le fichier  hash2ash/app/instance/appdb.db n'existe pas (Attention ça supprime la bdd)
```bash
python3
from run.py import db, app

with app.app_context():
    db.drop_all()
    db.create_all()
```

