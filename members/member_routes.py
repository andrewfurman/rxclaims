from flask import Blueprint, render_template
from .member_model import Member

members_bp = Blueprint('members', __name__, 
                      template_folder='.')

@members_bp.route('/members')
def members():
    members = Member.query.all()
    return render_template('members/members.html', members=members)

@members_bp.route('/members/<member_id>')
def view_member(member_id):
    member = Member.query.filter_by(member_id=member_id).first_or_404()
    return render_template('members/view_member.html', member=member)