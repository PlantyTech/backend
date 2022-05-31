from flask import Blueprint
from flask import Flask, request, jsonify, make_response
import json
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from models import Admin
from app import db, app
from functools import wraps

login_admin = Blueprint('login_admin', __name__)


# decorator for verifying the JWT
def token_required_admin(f):
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
            current_user = Admin.query \
                .filter_by(user_id=data['user_id']) \
                .first()
        except Exception as e:
            print(e)
            return jsonify({
                'message': 'Token is invalid !!'
            }), 403
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


# route for loging user in
@login_admin.route('/admin/login', methods=['GET'])
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

    if not auth or not auth.get('name') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    admin = Admin.query \
        .filter_by(email=auth.get('name')) \
        .first()

    if not admin:
        # returns 404 if admin does not exist
        return make_response(
            'Admin not found',
            404,
            {'WWW-Authenticate': 'Basic realm ="Admin does not exist !!"'}
        )
    if check_password_hash(admin.password, auth.get('password')):
        # generates the JWT Token
        admin.last_login = datetime.now()
        db.session.commit()
        token = jwt.encode({
            'user_id': admin.user_id,
            'exp': datetime.utcnow() + timedelta(minutes=120)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        try:
            return make_response(jsonify({'token': token.decode(),
                                          'userDetails': {"name": admin.name}}), 201)
        except:
            return make_response(jsonify({'token': token,
                                          'userDetails': {"name": admin.name}}), 201)

    # returns 403 if password is wrong
    return make_response(
        'Forbidden',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )
