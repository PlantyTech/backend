from flask import Blueprint
from flask import Flask, request, jsonify, make_response
import json
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from models import User
from app import db, app
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests

login = Blueprint('login', __name__)


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query \
                .filter_by(user_id=data['user_id']) \
                .first()
        except Exception as e:
            print(e)
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


# route for loging user in
@login.route('/api/login', methods=['GET'])
def _login():
    # creates dictionary of form data
    try:
        if request.json is not None:
            auth = request.json
        elif request.args is not None:
            auth = request.args
        else:
            auth = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query \
        .filter_by(email=auth.get('email')) \
        .first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'user_id': user.user_id,
            'exp': datetime.utcnow() + timedelta(minutes=120)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        try:
            return make_response(jsonify({'token': token.decode(),
                                          'userDetails': {"name": user.name, "email": user.email, "telefon": user.telefon}}), 201)
        except:
            return make_response(jsonify({'token': token,
                                          'userDetails': {"name": user.name, "email": user.email, "telefon": user.telefon}}), 201)

    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )

# route for loging user in
@login.route('/api/login-with-google', methods=['GET'])
def _login_with_google():
    # creates dictionary of form data
    try:
        if request.json is not None:
            auth = request.json
        elif request.args is not None:
            auth = request.args
        else:
            auth = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    if not auth or not auth.get('email'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    try:
        idToken=auth.get('idToken')
        idinfo = id_token.verify_oauth2_token(idToken, requests.Request())

        if idinfo['email'] != auth.get('email') or idinfo['sub'] != auth.get('id'):
            return make_response(
                'Could not verify',
                401,
                {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
            )
    except:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    user = User.query \
        .filter_by(email=auth.get('email')) \
        .first()

    if not user:
        # database ORM object
        user = User(
            name=auth.get('name'),
            email=auth.get('email'),
            password=generate_password_hash("google-password"),
            telefon=None,
            locatie=None
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        user = User.query \
            .filter_by(email=auth.get('email')) \
            .first()

    token = jwt.encode({
        'user_id': user.user_id,
        'exp': datetime.utcnow() + timedelta(minutes=120)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    try:
        return make_response(jsonify({'token': token.decode(),
                                      'userDetails': {"name": user.name, "email": user.email, "telefon": user.telefon}}), 201)
    except:
        return make_response(jsonify({'token': token,
                                      'userDetails': {"name": user.name, "email": user.email, "telefon": user.telefon}}), 201)



# signup route
@login.route('/api/signup', methods=['POST'])
def signup():
    # creates a dictionary of the form data
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')
    telefon, locatie = data.get('telefon'), data.get('locatie')

    # checking for existing user
    user = User.query \
        .filter_by(email=email) \
        .first()
    if not user:
        # database ORM object
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            telefon=telefon,
            locatie=locatie
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)
