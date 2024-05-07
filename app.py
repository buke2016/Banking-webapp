from flask import Flask, render_template, redirect, url_for, session, request, flash, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from account_service import AccountService
from user_service import UserService
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField
from wtforms.validators import InputRequired, Length, Email, NumberRange


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'bfg28y7efg238re7r6t32gfo23vfy7237yibdyo238do2v3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

account_service = AccountService()
user_service = UserService()

def get_user(username):
    # This function should query your database
    # For this example, we're using a mockup
    if username == "admin":
        return {"username": "admin", "password": "$pbkdf2-sha256$29000$..."}
    
# Dummy user data for demonstration
users = {"user1": "password1"}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, message="Password must be at least 6 characters long")])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])

class TransferForm(FlaskForm):
    from_account = StringField('From Account', validators=[InputRequired()])
    to_account = StringField('To Account', validators=[InputRequired()])
    amount = DecimalField('Amount', validators=[InputRequired(), NumberRange(min=0.01, message="Amount must be greater than zero")])

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/error.html', error=e), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error=str(error)), 500

def get_user_with_credentials(username, password):
    # Simulate database check
    if username == 'admin' and password == 'secret':
        return {'email': 'admin@example.com', 'token': 'fake-jwt-token'}
    return None

def generate_csrf():
    # Generate a CSRF token
    return 'secure_random_csrf_token'

def validate_csrf(token):
    # Validate the CSRF token
    return token == 'secure_random_csrf_token'

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(e):
    return render_template('errors/error.html', error=e), e.code

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # Validate username and password
        if username in users and users[username] == password:
            session['user'] = username  # Store username in session
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid credentials. Please try again.')  # Show error message
    # Render login template with form
    return render_template('login.html', form=form)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = user_service.get_user_by_email(email)
        if user:
            # Here should go the logic to send a reset password email
            flash('Password reset instructions have been sent to your email.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No user found with the provided email.', 'error')
            return render_template('forgot_password.html', form=form), 404
    return render_template('forgot_password.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome to the Dashboard, {session['user']}!"
    else:
        return redirect(url_for('login'))

@app.route('/details/<account_id>')
def details(account_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    account = account_service.get_account_by_id(account_id)
    return render_template('details.html', account=account)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))
    form = TransferForm()
    if form.validate_on_submit():
        from_account = form.from_account.data
        to_account = form.to_account.data
        amount = form.amount.data
        try:
            account_service.transfer_funds(from_account, to_account, amount)
            flash('Transfer successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(str(e), 'error')
    return render_template('transfer.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('auth_token')
    return response

if __name__ == '__main__':
    app.run(debug=True)
