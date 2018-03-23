from flask import abort, redirect, request, render_template, send_file, session, url_for

from database.db import db
from models import user
from app import app

@app.route("/")
def index():
    print("index()")
    id = session.get('logged_in')
    if id:
        return redirect(url_for('profile', username=user.read_by_id(id)['username']))
    return redirect(url_for('login'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    print("signup()")
    error = None
    if request.method == "POST":
        data = request.form.to_dict()
        if user.create(data):
            return redirect(url_for('login'))
        else:
            error = "Username already exists!"
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('signup.html', error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    print("login()")
    error = None
    if request.method == "POST":
        data = request.form.to_dict()
        usr = user.read(data['username'])
        if usr:
            if usr['password'] == data['password']:
                session['logged_in'] = usr['id']
                return redirect(url_for('index'))
            else:
                error = "Senha incorreta."
        else:
            error = "Nome de usuário incorreto."
    if session.get('logged_in'):
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error=error)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    print("settings()")
    id = session.get('logged_in')
    if id:
        if request.method == "GET":
            return render_template('settings.html', user=user.read_by_id(id))
        if request.method == "POST":
            data = request.form.to_dict()
            if 'delete' in data:
                user.delete(id)
                logout()
            if 'update' in data:
                user.update(id, data)
            return redirect(url_for('settings'))
    return redirect(url_for('index'))

@app.route("/<username>")
def profile(username):
    print("user(%s)" %username)
    usr = user.read(username)
    if usr:
        return render_template('profile.html', user=usr)
    abort(404)

@app.route("/download/<username>")
def download(username):
    print("download(%s)" %username)
    return send_file(user.to_vcard(username), as_attachment=True)

@app.route("/logout")
def logout():
    print("logout()")
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route("/db")
def database():
    print("database()")
    return render_template('db.html', db=db)