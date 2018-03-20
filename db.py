import dataset

db = dataset.connect('sqlite:///database/contacts.db', ensure_schema=False)