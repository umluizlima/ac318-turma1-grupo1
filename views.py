from flask import abort, render_template, redirect, request, session, url_for, send_file

import vobject
from db import db
from app import app

@app.route("/")
def index():
    if session.get('logged_in'):
        return redirect(url_for('user', username=db['users'].find_one(id=session.get('logged_in'))['username']))
    return redirect(url_for('login'))

@app.route("/<username>", methods=["GET", "POST"])
def user(username):
    message = None
    if request.method == "POST":
        data = request.form
        print(data['delete'])
        if data['delete'] is not None:
            return redirect(url_for('delete', username=username))
        if data['update'] is not None:
            return redirect(url_for('update', username=username, user=data))
    user = get_user(username)
    if user:
        if user['id'] == session.get('logged_in'):
            return render_template('myprofile.html', user=user)
        else:
            return render_template('profile.html', user=user)
    else:
        abort(404)
    print("Passou pelo /username")
    return render_template('profile.html', message=message)

@app.route("/delete/<username>", methods=["POST"])
def delete(username):
    user = get_user(username)
    db['users'].delete(id=user['id'])
    db['names'].delete(userId=user['id'])
    db['emails'].delete(userId=user['id'])
    db['phones'].delete(userId=user['id'])
    return redirect(url_for('logout'))

@app.route("/update/<username>", methods=["POST"])
def update(username):
    user = get_user(username)
    new_user = request.form
    new_name = dict(userId=user['id'], firstname=new_user['firstname'], lastname=new_user['lastname'])
    db['names'].update(new_name, ['userId'])
    new_email = dict(userId=user['id'], email=new_user['email'])
    db['emails'].update(new_email, ['userId'])
    new_phone = dict(userId=user['id'], phone=new_user['phone'])
    db['phones'].update(new_phone, ['userId'])
    return redirect(url_for('user', username=username))

@app.route("/download/<username>")
def download(username):
    return send_file(parse_vcard(get_user(username)))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        data = request.form.to_dict()
        print(data)
        if not db['users'].find_one(username=data['username']):
            user_id = db['users'].insert(data)
            data['userId'] = user_id
            data['tag'] = 'Main'
            db['names'].insert(data)
            db['emails'].insert(data)
            db['phones'].insert(data)
            return redirect(url_for('user', username=data['username']))
        else:
            error = "Username already exists!"
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('signup.html', error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
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

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/db")
def database():
    return render_template('db.html', db=db)

def get_user(username):
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
    return None

def parse_vcard(user):
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