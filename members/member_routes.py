from flask import Blueprint, render_template, request, jsonify
from .create_member_gpt import create_member_gpt
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

@members_bp.route('/members/create-gpt', methods=['POST'])
def create_member_with_gpt():
    prompt = request.json.get('prompt', '')
    try:
        result = create_member_gpt(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500