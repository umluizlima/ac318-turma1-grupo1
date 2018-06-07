import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.model import db, User, Telephone, Email

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        error = None
        username = request.form['username']

        if User.query.filter_by(username=username).first() is not None:
            error = f'Usuário {username} já cadastrado.'

        if error is None:
            user = User(username=username,
                        password=generate_password_hash(request.form['password']),
                        first_name=request.form['firstname'],
                        last_name=request.form['lastname'])
            db.session.add(user)
            user = User.query.filter_by(username=username).first()
            email = Email(tag="main",
                          email=request.form['email'],
                          user_id=user.id)
            db.session.add(email)

            telephone = Telephone(tag="main",
                                  telephone=request.form['telephone'],
                                  user_id=user.id)
            db.session.add(telephone)
            db.session.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/signup.html', title='Cadastrar-se')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        error = None
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Nome de usuário incorreto.'
        elif not check_password_hash(user.password, password):
            error = 'Senha incorreta.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html', title='Entrar')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()
