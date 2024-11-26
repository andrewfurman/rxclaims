import os
from flask import Flask, redirect
from members.member_model import db
from members.member_routes import members_bp
from claims.claim_routes import claims_bp
from ncpdp.ncpdp_routes import ncpdp_bp

from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError

app = Flask(__name__, template_folder='.')
# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(app)
# Create retry decorator
def retry_database_operation():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(OperationalError),
        reraise=True
    )
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

# Register blueprints
app.register_blueprint(members_bp)
app.register_blueprint(claims_bp)
app.register_blueprint(ncpdp_bp)

@app.route('/')
def index():
    return redirect('/members')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)