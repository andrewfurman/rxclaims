import os
from flask import Flask, redirect
from members.member_model import db
from members.member_routes import members_bp
from claims.claim_routes import claims_bp

app = Flask(__name__, template_folder='.')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(app)

# Register blueprints
app.register_blueprint(members_bp)
app.register_blueprint(claims_bp)

@app.route('/')
def index():
    return redirect('/members')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)