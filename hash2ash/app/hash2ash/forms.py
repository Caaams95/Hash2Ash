from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField , PasswordField, SubmitField, BooleanField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from hash2ash.models import Users, Instances, Hashes

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already in use. Please choose another one.')
         
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already in use. Please choose another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CrackStationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=60)], render_kw={'placeholder':'MyHash'})
    hash = StringField('Hash (MAX LEGNTH = 130)', validators=[DataRequired(), Length(min=3, max=130)], render_kw={'placeholder':'6f66ea07a56b056be5fd28ad6fbbdada'})
    mask = StringField('Mask', validators=[Length(max=130)])
    algorithm = SelectField(
        'Algorithm',
        choices=[('', 'Choice ...'), ('SHA1', 'SHA1'), ('SHA-256', 'SHA-256'), ('NTLM', 'NTLM')],
        validators=[DataRequired()],
    )
    provider = SelectField(
        'Provider',
        choices=[('', 'Choice ...'), ('AWS', 'AWS'), ('AZURE', 'AZURE'), ('GCP', 'GCP')],
        validators=[DataRequired()],
    )
    power = SelectField(
        'Instance Performance',
        choices=[('', 'Choice ...'), ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        validators=[DataRequired()],
    )
    submit = SubmitField('Crack It !')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Account')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already in use. Please choose another one.')
         
    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is already in use. Please choose another one.')
            
class AdminUpdateAccountForm(FlaskForm):
    user_id=StringField('User ID')
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField(
        'Role',
        choices=[('', 'Change role'), ('user', 'User'), ('admin', 'Admin')]
    )
    submit = SubmitField('Saves Changes')

    def validate_username(self, username):
        user = Users.query.get(self.user_id.data)
        if user and username.data != user.username:
            user_with_same_username = Users.query.filter_by(username=username.data).first()
            if user_with_same_username:
                raise ValidationError('This username is already in use. Please choose another one.')
         
    def validate_email(self, email):
        user = Users.query.get(self.user_id.data)
        if user and email.data != user.email:
            user_with_same_email = Users.query.filter_by(email=email.data).first()
            if user_with_same_email:
                raise ValidationError('This email is already in use. Please choose another one.')
            

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
        
