from flask import abort, render_template, redirect, request, session, url_for, send_file

import vobject
from db import db
from app import app

# Se logado, mostra seu próprio perfil. Senão mostra a tela de login.
@app.route("/")
def index():
    print("index()")
    if session.get('logged_in'):
        return redirect(url_for('user', username=read_logged_user()['username']))
    return redirect(url_for('login'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    print("signup()")
    error = None
    if request.method == "POST":
        data = request.form.to_dict()
        if create(data):
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
        user = db['users'].find_one(username=data['username'])
        if user:
            if user['password'] == data['password']:
                session['logged_in'] = user['id']
                return redirect(url_for('index'))
            else:
                error = "Senha incorreta."
        else:
            error = "Nome de usuário incorreto."
    if session.get('logged_in'):
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error=error)

# Mostra o perfil de <username>. Se for seu próprio, terá o botão Editar. Se não existir mostra 404.
@app.route("/<username>", methods=["GET"])
def user(username):
    print("user(%s)" %username)
    user = read(username)
    if user:
        return render_template('profile.html', user=user)
    abort(404)

# Se logado, tela de edição de perfil, senão login.
@app.route("/settings", methods=["GET", "POST"])
def settings():
    print("settings()")
    if session.get('logged_in'):
        if request.method == "GET":
            return render_template('settings.html', user=read_logged_user())
        if request.method == "POST":
            data = request.form.to_dict()
            if 'delete' in data:
                delete(session.get('logged_in'))
                logout()
            if 'update' in data:
                update(data)
            return redirect(url_for('settings'))
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    print("logout()")
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/db")
def database():
    print("database()")
    return render_template('db.html', db=db)

''' CRUD de usuario'''

def create(data):
    print("create(data)")
    user = None
    routes = ''.join([rule.rule.strip('/') for rule in app.url_map.iter_rules()])
    if not db['users'].find_one(username=data['username']) and data['username'] not in routes:
        user_id = db['users'].insert(data)
        data['userId'] = user_id
        data['tag'] = 'Main'
        db['names'].insert(data)
        db['emails'].insert(data)
        db['phones'].insert(data)
        user = read(data['username'])
    return user

def read(username):
    print("read(%s)" %username)
    user = None
    query = db['users'].find_one(username=username)
    if query:
        user = {'id': query['id']}
        user['username'] = query['username']
        query = db['names'].find_one(userId=user['id'])
        user['firstname'] = query['firstname']
        user['lastname'] = query['lastname']
        user['emails'] = dict()
        for query in db['emails'].find(userId=user['id']):
            user['emails'][query['tag']] = query['email']
        user['phones'] = dict()
        for query in db['phones'].find(userId=user['id']):
            user['phones'][query['tag']] = query['phone']
    return user

def update(data):
    print("update(data)")
    user = read_logged_user()
    new_name = dict(userId=user['id'], firstname=data['firstname'], lastname=data['lastname'])
    db['names'].update(new_name, ['userId'])
    new_email = dict(userId=user['id'], email=data['email'])
    db['emails'].update(new_email, ['userId'])
    new_phone = dict(userId=user['id'], phone=data['phone'])
    db['phones'].update(new_phone, ['userId'])
    return read_logged_user()

def delete(id):
    print("delete()")
    db['users'].delete(id=id)
    db['names'].delete(userId=id)
    db['emails'].delete(userId=id)
    db['phones'].delete(userId=id)

def read_logged_user():
    print("read_logged_user()")
    user = None
    id = session.get('logged_in')
    if id:
        user = read(db['users'].find_one(id=id)['username'])
    return user

@app.route("/download/<username>")
def download(username):
    print("download(%s)" %username)
    return send_file(parse_vcard(read(username)))

def parse_vcard(user):
    print("parse_vcard()")
    vcard = vobject.vCard()
    name = vcard.add('fn')
    name.value = user['firstname'] + ' ' + user['lastname']
    name = vcard.add('n')
    name.value = vobject.vcard.Name(family=user['lastname'], given=user['firstname'])
    for tag in user['emails']:
        e = vcard.add('email')
        e.value = user['emails'][tag]
        e.type_param = tag
    for tag in user['phones']:
        t = vcard.add('tel')
        t.value = user['phones'][tag]
        t.type_param = tag
    filepath = '_'.join(['vcf/' + user['firstname'], user['lastname'], 'contact.vcf'])
    with open(filepath, 'w+') as f:
        f.write(vcard.serialize())
    return filepath