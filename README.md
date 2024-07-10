### Créer un environnement python
```bash
virtualenv -p python3 venv
source venv/bin/activate.fish
```

### Dépendances necessaires pour lancer le serveur

```bash
cd hash2ash
pip install -r requirements.txt
apt install aws-cli terraform bc -y
```
### Lancer le serveur web
```bash
cd hash2ash/app/
python3 run.py
```
### Lancer le listenner de BDD
Dans un 2e terminal:
```bash
cd terraform/
python3 listenner.py
```
### Compte Admin
```
email: admin@demo.com
password: admin
```
### Compte Utilisateur

Pour voir l'expérieur utilisateur créer toi un compte sur la page login


### Si le fichier  hash2ash/app/instance/appdb.db n'existe pas (Attention ça supprime la bdd)
```bash
python3
from src import db, app

with app.app_context():
    db.drop_all()
    db.create_all()
```

