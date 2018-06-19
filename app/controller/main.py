from flask import (
    Blueprint, redirect, url_for, session, render_template, request, flash
)

from app.model import User

bp = Blueprint('main', __name__, url_prefix='')


@bp.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form.to_dict()
        if 'username' in data.keys():
            return redirect(url_for('user.profile', username=data['username']))
        flash('Nome de usuário inválido.')
    return render_template('main/index.html', title="Início")
