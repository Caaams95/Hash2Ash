from flask import render_template, url_for, flash, redirect, request, abort
from hash2ash import app, db, bcrypt
from hash2ash.models import Users, Instances, Hashes
from hash2ash.forms import RegistrationForm, LoginForm, CrackStationForm, UpdateAccountForm, AdminUpdateAccountForm   # Importation des classes RegistrationForm et LoginForm depuis forms.py
from flask_login import login_user, current_user, logout_user, login_required



### Routes
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

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

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/crackstation', methods=['GET', 'POST'])            # Route pour la page de test de hash
@login_required
def crackstation():
    form = CrackStationForm()
    if form.validate_on_submit():
        #flash(f'Form validated', 'info') # Pour debbuger le formulaire
        if current_user.is_authenticated:
            hash = Hashes(hash=form.hash.data, mask=form.mask.data, name=form.name.data ,algorithm=form.algorithm.data, power=form.power.data, provider=form.provider.data, status='In Queue', progress=0, price=0, fk_id_user=current_user.id_user)
            db.session.add(hash)
            db.session.commit()
            #flash(f'Hash added to database', 'info') # Pour debbuger le formulaire
            flash(f'Your hash crack has been added to the queue', 'success')
            return redirect(url_for('crackstation'))
        else:
            flash(f'You must be logged in to use Crack Station', 'danger')
            return redirect(url_for('login'))
####Pour debbuger le formulaire    
    # flash(f'Form not validated', 'danger')        
    # for field, errors in form.errors.items():
    #     for error in errors:
    #         flash(f"Error in the {getattr(form, field).label.text} field - {error}")
####Fin pour debbuger le formulaire    

    return render_template('crackstation.html', title='Crack Station', form=form)

@app.route('/account', methods=['GET', 'POST'])
@app.route('/account/myhashes', methods=['GET', 'POST'])
@login_required
def account():
    hashes = Hashes.query.filter_by(fk_id_user=current_user.id_user).all()
    return render_template('accountMyhashes.html', title='My Hashes', hashes=hashes)

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