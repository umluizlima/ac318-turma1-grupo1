import os
import vobject
from database.db import db

def create(data):
    print("create(data)")
    user = None
    if not db['users'].find_one(username=data['username']):
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

def read_by_id(id):
    print("read_by_id()")
    return read(db['users'].find_one(id=id)['username'])

def read_login(username, password):
    login = {'id' : None, 'password': None}
    user = db['users'].find_one(username=username)
    if user:
        login['id'] = user['id']
        if password == user['password']:
            login['password'] = True
    return login

def update(id, data):
    print("update(data)")
    # user = read_logged_user()
    new_name = dict(userId=id, firstname=data['firstname'], lastname=data['lastname'])
    db['names'].update(new_name, ['userId'])
    new_email = dict(userId=id, email=data['email'])
    db['emails'].update(new_email, ['userId'])
    new_phone = dict(userId=id, phone=data['phone'])
    db['phones'].update(new_phone, ['userId'])
    return read_by_id(id)

def delete(id):
    print("delete()")
    db['users'].delete(id=id)
    db['names'].delete(userId=id)
    db['emails'].delete(userId=id)
    db['phones'].delete(userId=id)

def to_vcard(username):
    print("to_vcard(%s)" %username)
    user = read(username)
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
    filename = '_'.join([user['firstname'], user['lastname'], 'contact.vcf'])
    filepath = os.path.join('vcf', filename)
    with open(filepath, 'w+') as f:
        f.write(vcard.serialize())
    return filepath