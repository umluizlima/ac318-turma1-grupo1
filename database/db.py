import os
import sqlite3
import dataset

db = dataset.connect('sqlite:///database/contacts.db', ensure_schema=False)

if __name__ == "__main__":
    if not os.path.lexists(os.path.join('database', 'contacts.db')):
        db = sqlite3.connect(os.path.join('database', 'contacts.db'))
        with open(os.path.join('database', 'schema.sql'), mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()