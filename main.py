import os, psycopg2
from auth_config import oauth, auth0, requires_auth
from flask import Flask, redirect, url_for, session
from members.member_model import db
from members.member_routes import members_bp
from claims.claim_routes import claims_bp
from ncpdp.ncpdp_routes import ncpdp_bp

from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError


app = Flask(__name__, template_folder='.')
# Configure database and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.secret_key = os.getenv("AUTH0_CLIENT_SECRET")  # Required for Auth0 sessions
# Initialize extensions
db.init_app(app)
oauth.init_app(app)  # Initialize OAuth with app

# Near the top of main.py, after app creation
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Auth routes

@app.route('/login')
def login():
    callback_url = url_for('callback', _external=True, _scheme='https')
    print(f"Callback URL being used: {callback_url}")
    # Generate and store state parameter
    return auth0.authorize_redirect(
        redirect_uri=callback_url,
        audience=f'https://{os.getenv("AUTH0_DOMAIN")}/userinfo'  # Add this line
    )

@app.route('/callback')
def callback():
    try:
        token = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        session['user'] = userinfo
        return redirect('/')
    except Exception as e:
        print(f"Auth error: {str(e)}")
        return redirect('/login')

def retry_database_operation():
    def decorator(f):
        @wraps(f)
        @retry(
            stop=stop_after_attempt(5),  # Increased attempts
            wait=wait_exponential(multiplier=1, min=4, max=30),  # Adjusted wait times
            retry=(
                retry_if_exception_type(OperationalError) |
                retry_if_exception_type(psycopg2.OperationalError)
            ),
            reraise=True
        )
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (OperationalError, psycopg2.OperationalError):
                # Ensure connection is closed and cleaned up
                db.session.remove()
                # Create new connection
                db.session.configure(bind=db.engine)
                # Re-raise to trigger retry
                raise
        return wrapped
    return decorator
    
# Create middleware to apply retry logic to all routes
class RetryMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        @retry_database_operation()
        def _retry_app(*args, **kwargs):
            return self.app(environ, start_response)
        return _retry_app()
# Apply middleware
app.wsgi_app = RetryMiddleware(app.wsgi_app)

# Add this decorator function before your route definitions
def route_retry():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(OperationalError) |
            retry_if_exception_type(psycopg2.OperationalError)
        )
    )

# Register blueprints
app.register_blueprint(members_bp)
app.register_blueprint(claims_bp)
app.register_blueprint(ncpdp_bp)

# Then modify your index route to use it
@app.route('/')
@route_retry()
def index():
    return redirect('/members')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)