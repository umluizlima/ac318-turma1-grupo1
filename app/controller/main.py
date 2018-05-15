from flask import (
    Blueprint, render_template
)

from .auth import login_required
from app.model import User

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    return render_template('main/index.html')


@bp.route("/db")
def database():
    return render_template('db.html', users=User.query.all())
