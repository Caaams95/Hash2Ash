from flask import render_template, url_for, flash, redirect, request, abort
from src import app, db, bcrypt, mail, s3
from src.models import Users, Instances, Hashes
from hash2ash.forms import RegistrationForm, LoginForm, CrackStationForm, UpdateAccountForm, AdminUpdateAccountForm, RequestResetForm, ResetPasswordForm   # Importation des classes RegistrationForm et LoginForm depuis forms.py
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from werkzeug.utils import secure_filename
import os
import tempfile
import json


### Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

# Route pour l'inscription de l'utilisateur
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('crackstation'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created !', 'success') ## Si c'est vrai on redirige vers la fonction home
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Route pour la connexion de l'utilisateur
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('crackstation'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash(f'Login Successful. Welcome {user.username} !', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('crackstation'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Route pour la déconnexion de l'utilisateur
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_and_upload_file(file, user_id, file_type):
    """
    Sauvegarde un fichier temporairement et l'upload sur S3.
    
    :param file: Le fichier à sauvegarder et uploader.
    :param user_id: L'identifiant de l'utilisateur, utilisé pour nommer le fichier.
    :param file_type: Le type de fichier ('hash' ou 'custom_wordlist').
    :return: L'url du fichier sauvegardé.
    """
    file_name = secure_filename(f"{secrets.token_bytes(10).hex()}_{user_id}_{file_type}.txt")
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file_name)
    file.save(temp_path)
    s3.upload_file(temp_path, app.config['BUCKET_NAME'], file_name)  # Utiliser le chemin temporaire pour l'upload
    # Nettoyer le fichier temporaire après l'upload
    os.remove(temp_path)
    os.rmdir(temp_dir)
    file_url = f"https://{app.config['BUCKET_NAME']}.s3.{app.config['AWS_REGION_NAME']}.amazonaws.com/{file_name}"
    return file_url

# Route pour le formulaire de enregistrement d'un hash
@app.route('/crackstation', methods=['GET', 'POST'])            # Route pour la page de test de hash
@login_required
def crackstation():
    form = CrackStationForm()
    if form.validate_on_submit():
        #flash(f'form.wordlist.data', 'info') # Pour debbuger le formulaire
        if current_user.is_authenticated:
            
            url_hash = save_and_upload_file(form.hash.data, current_user.id_user, 'hash')

            form.wordlist.data = None if not form.wordlist.data else json.dumps(form.wordlist.data)
            if form.custom_wordlist.data:
                url_custom_wordlist = save_and_upload_file(form.custom_wordlist.data, current_user.id_user, 'custom_wordlist')
            else:
                url_custom_wordlist = None
            
            hash = Hashes(hash=url_hash, name=form.name.data ,algorithm=form.algorithm.data, wordlist=form.wordlist.data, custom_wordlist=url_custom_wordlist ,power=form.power.data, provider=form.provider.data, status='In Queue', progress=0, price=0, fk_id_user=current_user.id_user)
            db.session.add(hash)
            db.session.commit()
            #flash(f'Hash added to database', 'info') # Pour debbuger le formulaire
            flash(f'Your hash crack has been added to the queue', 'success')
            return redirect(url_for('crackstation'))
        else:
            flash(f'You must be logged in to use Crack Station', 'danger')
            return redirect(url_for('login')) 

    return render_template('crackstation.html', title='Crack Station', form=form)


# Route pour la page profil avec les hashes de l'utilisateur
@app.route('/account', methods=['GET', 'POST'])
@app.route('/account/myhashes', methods=['GET', 'POST'])
@login_required
def account():
    hashes = Hashes.query.filter_by(fk_id_user=current_user.id_user).all()
    return render_template('accountMyhashes.html', title='My Hashes', hashes=hashes)

# Route pour la mise à jour des infos du compte utilisateur
@app.route('/account/info', methods=['GET', 'POST'])
def accountInfo():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data 
        db.session.commit()
        flash(f'Your account has been updated !', 'success')
        return redirect(url_for('accountInfo'))
    elif request.method == 'GET': 
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('accountInfo.html', title='My Info', form=form)

# Route pour la mise à jour du mot de passe en etant admin
@app.route('/adminpanel', methods=['GET', 'POST'])
@login_required
def adminpanel():
    if current_user.role != 'admin':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('home'))
    user_count = Users.query.count()

    form = AdminUpdateAccountForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(id_user=form.user_id.data).first()
        if user:
            user.username = form.username.data
            user.email = form.email.data
            if form.role.data == 'admin' or form.role.data == 'user':
                user.role = form.role.data
            db.session.commit()
            flash(f'The user account has been updated successfully!', 'success')
            return redirect(url_for('adminpanel', page=request.args.get('page', 1, type=int)))
        else:
            flash(f'The user account has NOT been updated ! ' + form.user_id.data, 'warning')
    page = request.args.get('page', 1, type=int)
    users = Users.query.order_by(Users.id_user.desc()).paginate(page=page, per_page=10)
    return render_template('adminpanel.html', title='Admin Panel', form=form, users=users, user_count=user_count)

# Route pour afficher les hashes d'un utilisateur en etant admin
@app.route('/adminpanel/user_<int:id_user>/hashes')
@login_required
def adminpanelUserHashes(id_user):
    if current_user.role != 'admin':
        flash('You are not authorized to access this page', 'danger')
        return redirect(url_for('home'))
    user = Users.query.get_or_404(id_user)
    username = user.username
    hashes = Hashes.query.filter_by(fk_id_user=user.id_user).all()
    return render_template('adminpanelUserHashes.html', title='User Hashes', hashes=hashes, username=username)

# Route pour la suppression d'un hash
@app.route('/adminpanel/hash_<int:id_hash>/delete', methods=['POST'])
@login_required
def delete_hash(id_hash):
    hash = Hashes.query.get_or_404(id_hash)
    if current_user.role != 'admin' and current_user.id_user != hash.fk_id_user:
        abort(403)
    db.session.delete(hash)
    db.session.commit()
    flash('The hash has been deleted!', 'success')
    if request.referrer.endswith('/account/myhashes'):
        return redirect(url_for('account'))
    else:
        return redirect(url_for('adminpanelUserHashes', id_user=hash.fk_id_user))
    
# Route pour la suppression d'un utilisateur
@app.route('/adminpanel/user_<int:id_user>/delete', methods=['POST'])
@login_required
def delete_user(id_user):
    user = Users.query.get_or_404(id_user)
    if current_user.role != 'admin':
        abort(403)
    userhashes = Hashes.query.filter_by(fk_id_user=user.id_user).all()
    for hash in userhashes:
        db.session.delete(hash)
    db.session.delete(user)
    db.session.commit()
    flash(f'The user '+ user.username + ' has been deleted!', 'success')
    return redirect(url_for('adminpanel'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = MIMEMultipart()
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = user.email
    msg['Subject'] = 'Password Reset Request'
    body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    msg.attach(MIMEText(body, 'plain'))
    # Connexion au serveur SMTP
    server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
    server.starttls()  # Sécuriser la connexion
    server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    server.sendmail(app.config['MAIL_USERNAME'], user.email, msg.as_string())
    server.quit()

# Route pour la réinitialisation du mot de passe
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('resetPassword.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated !', 'success') ## Si c'est vrai on redirige vers la fonction home
        return redirect(url_for('login'))
    return render_template('resetToken.html', title='Reset Password', form=form)