from flask import (
    Blueprint, redirect, url_for, session
)

from .auth import login_required
from app.model import User

bp = Blueprint('main', __name__, url_prefix='')


@bp.route('/')
@login_required
def index():
    user = User.query.filter_by(id=session.get('user_id')).first()
    return redirect(url_for('user.profile', username=user.username))
