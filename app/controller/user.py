from flask import (
    Blueprint, render_template, abort, send_from_directory, request, session,
    jsonify, current_app, redirect, url_for, flash
)

from app.model import db, User, Email, Telephone
from .auth import login_required

bp = Blueprint('user', __name__, url_prefix='')


@bp.route("/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('user/profile.html', user=user.to_dict(),
                               title=user.username)
    flash('Nome de usuário inválido.')
    return redirect(url_for('main.index'))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = User.query.filter_by(id=session.get('user_id')).first()
    if request.method == "POST":
        data = request.form.to_dict()
        if 'delete' in data:
            db.session.delete(user)
            db.session.commit()
        if 'update' in data:
            print('Tentou editar!!!')
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            email = Email.query.filter_by(id=data['email_id']).first()
            email.email = data['email']
            telephone = Telephone.query.filter_by(id=data['telephone_id']).first()
            telephone.telephone = data['telephone']
            db.session.commit()
        return redirect(url_for('user.profile', username=user.username))
    return render_template('user/settings.html', user=user.to_dict(),
                           title='Editar')


@bp.route("/download/<username>")
def download(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return send_from_directory(current_app.config['VCARD_FOLDER'],
                                   user.to_vcard(),
                                   as_attachment=True)
    abort(404)
