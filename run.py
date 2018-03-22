import os
import sqlite3
from app import app

if not os.path.lexists(os.path.join('database', 'contacts.db')):
    db = sqlite3.connect(os.path.join('database', 'contacts.db'))
    with open(os.path.join('database', 'schema.sql'), mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

app.run(host='0.0.0.0',
    port=5555,
    debug=True)