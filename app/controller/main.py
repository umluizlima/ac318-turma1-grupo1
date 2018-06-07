from flask import (
    Blueprint, redirect, url_for, session, send_from_directory, render_template
)

from .auth import login_required
from app.model import User

bp = Blueprint('main', __name__, url_prefix='')


@bp.route('/')
@login_required
def index():
    user = User.query.filter_by(id=session.get('user_id')).first()
    return redirect(url_for('user.profile', username=user.username))


@bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@bp.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')
