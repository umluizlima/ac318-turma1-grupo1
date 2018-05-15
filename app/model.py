import os
import vobject
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


class User(db.Model):
    """
    CREATE: db.session.add(item) -> db.session.commit()
    READ: Item.query.all() or Item.query.filter_by(key=value).first()
    UPDATE: item = Item.query.filter_by(key=value).first() -> item.key = value\
    -> db.session.commit()
    DELETE: db.session.delete(item) -> db.session.commit()
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    emails = db.relationship('Email', cascade='delete', backref='user')
    telephones = db.relationship('Telephone', cascade='delete', backref='user')

    def to_dict(self):
        user = {'id': self.id,
                'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'full_name': f'{self.first_name} {self.last_name}',
                'emails': [email.to_dict() for email in Email.query.filter_by(user_id=self.id).all()],
                'telephones': [phone.to_dict() for phone in Telephone.query.filter_by(user_id=self.id).all()]}
        return user

    def to_vcard(self):
        vcard = vobject.vCard()
        user = self.to_dict()

        name = vcard.add('fn')
        name.value = user['full_name']
        name = vcard.add('n')
        name.value = vobject.vcard.Name(family=user['last_name'],
                                        given=user['first_name'])

        for email in user['emails']:
            e = vcard.add('email')
            e.value = email['email']
            e.type_param = email['tag']

        for telephone in user['telephones']:
            t = vcard.add('tel')
            t.value = telephone['telephone']
            t.type_param = telephone['tag']

        filename = '_'.join([self.first_name, self.last_name, 'contact.vcf'])
        filepath = os.path.join(os.path.abspath(''), 'instance', 'vcf', filename)
        with open(filepath, 'w+') as f:
            f.write(vcard.serialize())
        return filename

    def __repr__(self):
        return f"<User {self.username}>"


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        email = {'id': self.id,
                 'tag': self.tag,
                 'email': self.email}
        return email

    def __repr__(self):
        return f"'<Email {self.email}>"


class Telephone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Text, nullable=True)
    telephone = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        telephone = {'id': self.id,
                     'tag': self.tag,
                     'telephone': self.telephone}
        return telephone

    def __repr__(self):
        return f"<Telephone {self.telephone}>"
