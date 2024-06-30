from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField , PasswordField, SubmitField, BooleanField, SelectField, FileField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from hash2ash.models import Users, Instances, Hashes
from flask_wtf.file import FileAllowed, FileRequired

HASHCAT_ALGORITHMS = [
    ('', 'Choice ...'),
    ('0', 'MD5'),
    ('100', 'SHA1'),
    ('400', 'phpass, WordPress (MD5), Joomla (MD5)'),
    ('1400', 'SHA-256'),
    ('1700', 'SHA-512'),
    ('1800', 'sha512crypt $6$, SHA-512 (Unix)'),
    ('3200', 'bcrypt $2*$, Blowfish (Unix)'),
    ('1000', 'NTLM'),
    ('2100', 'Domain Cached Credentials (DCC), MS Cache'),
    ('2400', 'Cisco ASA MD5'),
    ('2500', 'WPA-EAPOL-PBKDF2 (WPA/WPA2)'),
    ('2501', 'WPA-EAPOL-PMK (WPA/WPA2)'),
    ('5600', 'NetNTLMv2'),
    ('5500', 'NetNTLMv1'),
    ('1500', 'descrypt, DES (Unix), Traditional DES'),
    ('3000', 'LM'),
    ('13100', 'Kerberos 5 AS-REQ Pre-Auth etype 23'),
    ('7500', 'Kerberos 5 TGS-REP etype 23'),
    ('131', 'MSCHAPv2'),
    ('6800', 'LastPass + LastPass sniffed'),
    ('7100', 'macOS v10.8+ (PBKDF2-SHA512)'),
    ('11600', '7-Zip'),
    ('12500', 'RAR3-hp'),
    ('13000', 'RAR5'),
    ('13200', 'AxCrypt'),
    ('13300', 'AxCrypt in-memory SHA1'),
    ('15300', 'DPAPI masterkey file v1'),
    ('15900', 'DPAPI masterkey file v2'),
    ('16500', 'Apple Secure Notes'),
    ('18400', 'Open Document Format (ODF) 1.2 (SHA-256)'),
    ('7400', 'SHA-1(Base64), nsldap, Netscape LDAP SHA'),
    ('8900', 'SipHash'),
    ('9100', 'Lotus Notes/Domino 8.5+'),
    ('9200', 'Cisco-IOS $1$ (MD5)'),
    ('9300', 'Cisco-IOS $4$ (PBKDF2-SHA256)'),
    ('9400', 'Cisco-IOS $8$ (PBKDF2-SHA256)'),
    ('9500', 'Cisco-IOS $9$ (scrypt)'),
    ('9600', 'MS Office 2007'),
    ('9800', 'MS Office 2010'),
    ('9900', 'MS Office 2013'),
    ('10000', 'MS Office 2016'),
    ('10400', 'PDF 1.4 - 1.6 (Acrobat 5 - 8)'),
    ('10500', 'PDF 1.7 Level 3 (Acrobat 9)'),
    ('10700', 'PDF 1.7 Level 8 (Acrobat 10 - 11)'),
    ('14700', 'iTunes backup <= 10.6 (PBKDF2-HMAC-SHA1)'),
    ('14800', 'iTunes backup >= 10.7 (PBKDF2-HMAC-SHA256 & AES-256-CBC)'),
    ('14900', '3DES (ECB)'),
    ('16200', 'Apple Secure Notes'),
    ('16800', 'WPA-PMKID-PBKDF2 (WPA/WPA2)'),
    ('16900', 'Ansible Vault'),
    ('17400', 'SipHash'),
    ('17500', 'Kerberos 5 TGS-REP etype 23'),
]
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

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
    
def file_size_limit(max_size):
    max_bytes = max_size * 1024 * 1024
    def _file_size_limit(form, field):
        if field.data:
            if len(field.data.read()) > max_bytes:
                raise ValidationError(f'File size must be less than {max_size} MB')
            field.data.seek(0)  # reset file pointer to beginning after reading
    return _file_size_limit

class CrackStationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=60)], render_kw={'placeholder': 'MyHash'})
    hash = FileField('Hash File (Max size: 200MB)', validators=[DataRequired(), FileAllowed(['txt'], 'TXT files only!')])
    wordlist = MultiCheckboxField(
        'Wordlist',
        choices=[
            ('rockyou', 'rockyou'), 
            ('common-passwords-win', 'common-passwords-win'), 
            ('10k-most-common', '10k-most-common'),
            ('active-directory-wordlists', 'active-directory-wordlists'),
            ('richelieu-top1000', 'richelieu-top1000')
        ],
        validators=[Optional()]  # Use Optional because actual requirement is checked in a custom validator
    )
    use_custom_wordlist = BooleanField('Use Custom Wordlist')
    custom_wordlist = FileField('Custom Wordlist', validators=[FileAllowed(['txt'], 'TXT files only!'), Optional()])
    algorithm = SelectField(
        'Algorithm',
        choices=HASHCAT_ALGORITHMS,
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
    submit = SubmitField('Crack It!')

    def validate_wordlist(self, field):
        if not field.data and not (self.use_custom_wordlist.data and self.custom_wordlist.data and self.custom_wordlist.data.filename):
            raise ValidationError('Please select at least one wordlist or upload a custom wordlist.')



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
        
