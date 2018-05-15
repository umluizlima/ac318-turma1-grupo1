from flask import (
    Blueprint, render_template, redirect, url_for, session
)

from .auth import login_required
from app.model import User

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    user = User.query.filter_by(id=session.get('user_id')).first()
    return redirect(url_for('user.profile', username=user.username))


@bp.route("/db")
def database():
    return render_template('db.html', users=User.query.all())
