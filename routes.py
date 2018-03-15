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
    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Post cadastra os dados dos campos no bd
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('insert into users (username, password) values (?, ?)', [request.form['username'], request.form['password']])
        db.commit()
        return 'Usuario cadastrado %s, %s' %(request.form['username'], request.form['password'])
    # Get retorna a página de cadastro
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Post compara os dados dos campos com o bd, se bater redireciona para o perfil
    error = None    
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select username, password from users where username like (?)', [request.form['username']])
        user, password = cur.fetchall()[0]
        print(user)
        if user:
            if password == request.form['password']:
                session['logged_in'] = True
                session['user'] = user
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
        print(cur.fetchall())
    return '<h1>Vc tentou encontrar %s</h1>' %username

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5555,
            debug=True)
