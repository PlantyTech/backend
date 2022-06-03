from flask_mail import Message
from app import mail_service, db
from flask import Blueprint, make_response
from flask import request
import json
import random
import string
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from login import token_required
mail = Blueprint('mail', __name__)
password_length = 10
characters = string.ascii_letters


@mail.route('/api/password/forget', methods=['POST'])
def _reset_password():
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user = User.query \
        .filter_by(email=data.get('email')) \
        .first()

    if not user:
        # returns 404 if user does not exist
        return make_response(
            'User not found',
            404,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )
    if not user.google:
        password = "".join(random.sample(characters, password_length-3)) + "".join(random.sample(string.punctuation, 1))\
                   + "".join(random.sample(string.digits, 2))
        user.password = generate_password_hash(password)
        msg = Message(subject="Resetare Parola",
                      sender="PlantyAI",
                      recipients=[user.email],
                      body="Salut,\n\nNoua ta parola este:\n"+password+"\n\nPuteti schimba parola din aplicatie\n\n"
                                                                       "Cu respect,\nEchipa PlantyAI")
        mail_service.send(msg)
        db.session.commit()
        return str(True)

    return str(False)


@mail.route('/api/password/change', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user = User.query.get(current_user.user_id)

    if not user.google:
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if check_password_hash(user.password, old_password):
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return str(True)

        return make_response(
            'Wrong Password',
            200)
    return str(False)
