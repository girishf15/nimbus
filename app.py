from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from passlib.context import CryptContext
import psycopg2
import os
import requests
from dotenv import load_dotenv
import config

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(HERE, 'templates')
STATIC_DIR = os.path.join(HERE, 'static')

# Use local templates/static so Nimbus is self-contained
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)

# Secret key from config
app.secret_key = config.SECRET_KEY


def get_db_conn():
    return psycopg2.connect(config.DATABASE_URL)

app.get_db_conn = get_db_conn
app.pwd_context = pwd_context


def verify_user(username: str, password: str):
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return None
    user_id, user, pw_hash, role = row
    try:
        if pwd_context.verify(password, pw_hash):
            return {"id": user_id, "username": user, "role": role}
    except Exception:
        return None
    return None


@app.route('/', methods=['GET'])
def login_get():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = verify_user(username, password)
    if user:
        # Store username as `username` to match vulnerability-scanner templates
        session.clear()
        session['logged_in'] = True
        session['username'] = user['username']
        session['nimbus_user'] = user['username']
        session['role'] = user.get('role')
        from datetime import datetime
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = session['login_time']
        session.permanent = True
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Invalid credentials')


@app.route('/dashboard')
def dashboard():
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))
    return render_template('dashboard.html', username=username)



# user management routes moved to `apps.users` blueprint


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('nimbus_user'):
            flash('Please log in', 'error')
            return redirect(url_for('login_get'))
        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login_wrapper():
    # Provide an endpoint named 'login' so templates using url_for('login') work
    if request.method == 'GET':
        return login_get()
    return login_post()



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_get'))


@app.route('/refresh_session', methods=['POST'])
def refresh_session_endpoint():
    """Refresh session timestamps on activity and return JSON status."""
    if not session.get('logged_in'):
        return {'status': 'error', 'message': 'not logged in'}, 401
    try:
        from datetime import datetime
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = session['login_time']
        session.permanent = True
        return {'status': 'success', 'message': 'Session extended'}, 200
    except Exception as e:
        app.logger.exception('Failed to refresh session')
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/api/session-check', methods=['GET'])
def session_check():
    """Check if the current session is valid."""
    if not session.get('logged_in'):
        return {'valid': False, 'message': 'not logged in'}, 401
    
    username = session.get('nimbus_user')
    if not username:
        return {'valid': False, 'message': 'no user in session'}, 401
    
    return {'valid': True, 'username': username}, 200


from apps.chat import chat_bp
app.register_blueprint(chat_bp)

from apps.users import users_bp
app.register_blueprint(users_bp)
 
from apps.documents import documents_bp
app.register_blueprint(documents_bp)

if __name__ == '__main__':
    app.run(host=config.APP_HOST, port=config.APP_PORT, debug=config.FLASK_DEBUG)

