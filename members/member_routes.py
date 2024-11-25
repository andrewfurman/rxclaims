from flask import Blueprint, render_template
from .member_model import Member

members_bp = Blueprint('members', __name__, 
                      template_folder='.')

@members_bp.route('/members')
def members():
    members = Member.query.all()
    return render_template('members/members.html', members=members)