import datetime

from flask import Flask,render_template,session,request, jsonify, Response
from sqlalchemy import or_, and_
from model import entities
from database import connector
import json

app = Flask(__name__)
db = connector.Manager()

cache = {}
engine = db.createEngine()

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

@app.route('/users', methods = ['GET'])
def get_users():
    key = 'getUsers'
    if key not in cache.keys():
        session = db.getSession(engine)
        dbResponse = session.query(entities.User)
        cache[key] = dbResponse;
        print("From DB")
    else:
        print("From Cache")

    users = cache[key];
    data = []
    for user in users:
        data.append(user)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { "status": 404, "message": "Not Found"}
    return Response(message, status=404, mimetype='application/json')


@app.route('/users', methods = ['DELETE'])
def remove_user():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "Deleted User"


@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    #c = request.get_json(silent=True)
    print(c)
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'

#####################################
@app.route('/messages', methods = ['GET'])
def get_messages():
    session = db.getSession(engine)
    messages = session.query(entities.Message)
    data = []
    for message in messages:
        data.append(message)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/message/<id>', methods = ['GET'])
def get_message(id):
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        js = json.dumps(message, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    response = { "status": 404, "message": "Not Found"}
    return Response(response, status=404, mimetype='application/json')


@app.route('/messages', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"


@app.route('/messages', methods = ['POST'])
def create_message():
    #c =  json.loads(request.form['values'])
    c = request.get_json(silent=True)
    session = db.getSession(engine)
    user_from = session.query(entities.User).filter(entities.User.id == c['user_from']['id']).first()
    user_to = session.query(entities.User).filter(entities.User.id == c['user_to']['id']).first()
    message = entities.Message(
        content = c['content'],
        user_from = user_from,
        user_to = user_to,
        sent_on = datetime.datetime.utcnow()
    )
    session.add(message)
    session.commit()
    return 'Created Message'

@app.route('/messages', methods = ['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated Message'


@app.route('/chats/<user_id>', methods = ['GET'])
def get_chats(user_id):
    sessiondb = db.getSession(engine)
    chats = sessiondb.query(entities.Message.user_to_id).filter(entities.Message.user_from_id == user_id).distinct()
    data = []
    for message in chats:
        user = sessiondb.query(entities.User).filter(entities.User.id == message[0]).first()
        data.append(user)

    chats = sessiondb.query(entities.Message.user_from_id).filter(entities.Message.user_to_id == user_id).distinct()
    for message in chats:
        user = sessiondb.query(entities.User).filter(entities.User.id == message[0]).first()
        if user not in data:
            data.append(user)

    return Response(json.dumps({'response' : data}, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/chats/<user_from_id>/<user_to_id>', methods = ['GET'])
def get_chat(user_from_id, user_to_id):
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(
        or_(
            and_(entities.Message.user_from_id == user_from_id, entities.Message.user_to_id == user_to_id ),
            and_(entities.Message.user_from_id == user_to_id, entities.Message.user_to_id == user_from_id)
        )
    )
    data = []
    for message in messages:
        data.append(message)

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/do_login', methods = ['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    sessiondb = db.getSession(engine)
    user = sessiondb.query(entities.User).filter(
        and_(entities.User.username == username, entities.User.password == password )
    ).first()
    if user != None:
        session['logged'] = user.id;
        return render_template("chats.html")
    else:
        return render_template("login.html")

@app.route('/mobile_login', methods = ['POST'])
def mobile_login():
    obj = request.get_json(silent=True)
    print(obj)
    username = obj['username']
    password = obj['password']
    sessiondb = db.getSession(engine)
    user = sessiondb.query(entities.User).filter(
        and_(entities.User.username == username, entities.User.password == password )
    ).first()
    if user != None:
        session['logged'] = user.id;
        return Response(json.dumps({'response': True, "id": user.id}, cls=connector.AlchemyEncoder), mimetype='application/json')
    else:
        return Response(json.dumps({'response': False}, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/', methods = ['GET'])
def login():
    return render_template("login.html")


@app.route('/current', methods = ['GET'])
def current():
    sessiondb = db.getSession(engine)
    user = sessiondb.query(entities.User).filter(entities.User.id == session['logged']).first()
    js = json.dumps(user, cls=connector.AlchemyEncoder)
    return Response(js, status=200, mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run()
