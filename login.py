from flask import Blueprint
from flask import request, jsonify, make_response, url_for
import json
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from models import User
from app import db, app, mail_service, DOMAIN
from flask_mail import Message
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

login = Blueprint('login', __name__)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


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
            if not current_user:
                return jsonify({
                    'message': 'Token is invalid !!'
                }), 403
        except Exception as e:
            print(e)
            return jsonify({
                'message': 'Token is invalid !!'
            }), 403
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
        # returns 404 if user does not exist
        return make_response(
            'User not found',
            404,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if not user.validated:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Email confirmation required !!"'})

    if not user.google:
        if check_password_hash(user.password, auth.get('password')):
            # generates the JWT Token
            user.push_token = auth.get('push_token')
            user.last_login = datetime.now()
            user.os_type = auth.get('os_type')
            user.language = auth.get('language')
            db.session.commit()
            token = jwt.encode({
                'user_id': user.user_id,
                'exp': datetime.utcnow() + timedelta(minutes=120)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            try:
                return make_response(jsonify({'token': token.decode(),
                                              'userDetails': {"name": user.name, "email": user.email, "phone": user.phone,
                                                              "ta_accept": user.ta_accept}}), 201)
            except:
                return make_response(jsonify({'token': token,
                                              'userDetails': {"name": user.name, "email": user.email, "phone": user.phone,
                                                              "ta_accept": user.ta_accept}}), 201)

    # returns 403 if password is wrong
    return make_response(
        'Forbidden',
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
        idToken = auth.get('idToken')
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
            phone=None,
            location=None,
            google=int(json.loads(str(True).lower()))
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        user = User.query \
            .filter_by(email=auth.get('email')) \
            .first()

    user.push_token = auth.get('push_token')
    user.last_login = datetime.now()
    user.os_type = auth.get('os_type')
    user.language = auth.get('language')

    db.session.commit()
    token = jwt.encode({
        'user_id': user.user_id,
        'exp': datetime.utcnow() + timedelta(minutes=120)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    try:
        return make_response(jsonify({'token': token.decode(),
                                      'userDetails': {"name": user.name, "email": user.email, "phone": user.phone,
                                                      "ta_accept": user.ta_accept}}), 201)
    except:
        return make_response(jsonify({'token': token,
                                      'userDetails': {"name": user.name, "email": user.email, "phone": user.phone,
                                                      "ta_accept": user.ta_accept}}), 201)


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
    phone, location = data.get('phone'), data.get('location')

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
            phone=phone,
            location=location,
            google=int(json.loads(str(False).lower())),
            created_data=datetime.now()
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email', sender='PlantyAI', recipients=[email])

        link = url_for('login.confirm_email', token=token, _external=True)
        link = link.replace("127.0.0.1:8000", DOMAIN)

        msg.body = 'Buna ziua,\n\nPentru a confirma contul creat pe aplicatia PlantyAI faceti click pe urmatorul ' \
                   'link: {} \n\nIn cazul in care nu ati creat dumneavoastra acest cont va rugam sa ignorati' \
                   ' acest email.\n\nVa multumim,\nEchipa PlantyAI'.format(link)

        mail_service.send(msg)

        return make_response('Successfully registered.', 201)
    else:
        if not user.validated:
            token = s.dumps(email, salt='email-confirm')

            msg = Message('Confirm Email', sender='PlantyAI', recipients=[email])

            link = url_for('login.confirm_email', token=token, _external=True)
            link = link.replace("127.0.0.1:8000", DOMAIN)
            msg.body = 'Buna ziua,\n\nPentru a confirma contul creat pe aplicatia PlantyAI faceti click pe urmatorul ' \
                       'link: {} \n\nIn cazul in care nu ati creat dumneavoastra acest cont va rugam sa ignorati' \
                       ' acest email.\n\nVa multumim,\nEchipa PlantyAI'.format(link)

            mail_service.send(msg)

        return make_response('User already exists. Please Log in.', 409)


@login.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600*72)
        user = User.query \
            .filter_by(email=email) \
            .first()
        if user:
            if user.validated:
                return '<h1>Adresa de email a fost deja validata cu succes!</h1>\n\nVa multumim,\nEchipa PlantyAI'

            user.validated = int(json.loads(str(True).lower()))
            db.session.commit()
        else:
            return '<h1>Ne Pare rau dar nu gasim acest cont!</h1> ' \
                   '\n\nEste posibil sa fi trecut prea mult timp de la crearea lui!'
    except SignatureExpired:
        return '<h1>Tokenul a expirat!</h1>'
    return '<h1>Adresa de email a fost validata cu succes!</h1>\n\nVa multumim,\nEchipa PlantyAI'
