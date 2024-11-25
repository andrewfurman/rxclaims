from flask import Blueprint, render_template
from .claim_model import Claim

claims_bp = Blueprint('claims', __name__, 
                     template_folder='.')  # This allows templates to be found in the claims directory

@claims_bp.route('/claims')
def claims():
    claims = Claim.query.all()
    return render_template('claims.html', claims=claims)