import os
import sqlite3
from flask import Flask, g, render_template, request

DATABASE = 'database/contacts.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    db = sqlite3.connect(DATABASE)
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

def close_db():
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    return render_template('index.html')

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
