import os
from flask import Flask, render_template
from members.member_model import Member, db

app = Flask(__name__, 
           template_folder='.')  # This allows templates to be found in subfolders

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(app)

@app.route('/')
def index():
    return 'HELLO RxClaims'

@app.route('/members')
def members():
    members = Member.query.all()
    return render_template('members/members.html', members=members)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)