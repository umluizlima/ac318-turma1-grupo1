# -*- coding: utf-8 -*-
import os
import sqlite3
from flask import flash, Flask, g, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database', 'contatcs.db'),
    SECRET_KEY='secret'
))

def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    return db

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_db(error):
    # Fecha o BD no fim do request
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    # Se estiver logado, vai para o perfil
    if session.get('logged_in'):
        return render_template('index.html')
    # Senão, vai para a página de cadastro
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Post cadastra os dados dos campos no bd
    error = None
    if request.method == 'POST':
        db = get_db()
        user = request.form
        print(user)
        if len(db.execute('select username from users where username like (?)', [user['username']]).fetchall()) == 0:
            db.execute('insert into users (username, password) \
                                    values (?, ?)', [user['username'], user['password']])
            userId = db.execute('select id from users where username like (?)', [user['username']]).fetchall()[0][0]
            db.execute('insert into names (userId, firstname, lastname) \
                                    values (?, ?, ?)', [userId, user['firstname'], user['lastname']])
            db.execute('insert into emails (userId, tag, email) \
                                    values (?, ?, ?)', [userId, 'Main', user['email']])
            db.commit()
            return redirect(url_for('login'))
        else:
            error = 'Nome de usuário já existe.'
    # Get retorna a página de cadastro
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Post compara os dados dos campos com o bd, se bater redireciona para o perfil
    error = None    
    if request.method == 'POST':
        db = get_db()
        user = db.execute('select username, password from users where username like (?)', [request.form['username']]).fetchall()
        #print(user)
        if len(user) == 1:
            username = user[0][0]
            password = user[0][1]
            if password == request.form['password']:
                session['logged_in'] = True
                session['user'] = username
                flash('You were logged in')
                return redirect(url_for('index'))
            else:
                error = 'Senha incorreta.'
        else:
            error = 'Nome de usuário inválido.'
    # Get retorna a página de login
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    # Faz logout e redireciona para o login
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/<username>', methods=['GET', 'POST'])
def user(username):
    if  request.method == 'GET':
        db = get_db()
        cur = db.cursor()
        cur.execute("select * from users where username == (?)", [username])
        # print(cur.fetchall())
    return '<h1>Vc tentou encontrar %s</h1>' %username

if __name__ == '__main__':
    app.run(host='127.0.0.1',
            port=5555,
            debug=True)
