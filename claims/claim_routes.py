from flask import Blueprint, render_template, request, jsonify
from .claim_model import Claim
from .create_claim_gpt import create_claim_gpt

claims_bp = Blueprint('claims', __name__, 
                     template_folder='.')

@claims_bp.route('/claims')
def claims():
    claims = Claim.query.all()
    return render_template('claims.html', claims=claims)

@claims_bp.route('/claims/create-gpt', methods=['POST'])
def create_claim_gpt_route():
    try:
        member_database_id = request.args.get('member_database_id', type=int)
        prompt = request.args.get('prompt', '')
        
        result = create_claim_gpt(member_database_id, prompt)
        return jsonify({"success": True, "claim": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400