from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from login_admin import token_required_admin
from models import Notification, User
from datetime import datetime
from app import db, sendPush

notification = Blueprint('notification', __name__)


@notification.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@notification.route('/admin/notification/all', methods=['GET'])
@token_required_admin
def api_all_admin(*_):
    notifications = Notification.query.all()
    output = []
    for notification in notifications:
        output.append({
            'notification_id': notification.notification_id,
            'title': notification.title,
            'text': notification.text,
            'data': notification.data,
            'read_flag': notification.read_flag,
            'category': notification.category,
            'users': [user.user_id for user in notification.user]
        })

    return jsonify({'notifications': output})


@notification.route('/admin/notification/add', methods=['POST'])
@token_required_admin
def api_add_admin(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user = data.get('users')[1:-1].split(", ")
    user = [User.query.get(user_id) for user_id in user]
    title = data.get('title')
    text = data.get('text')
    category = data.get('category')

    data = datetime.now()

    # database ORM object
    notification = Notification(
        title=title,
        text=text,
        data=data,
        read_flag=False,
        category=category,
        user=user
    )
    # insert user
    db.session.add(notification)
    db.session.commit()

    registration_token = [user_it.push_token for user_it in user if user_it.push_token]
    sendPush(title=notification.title, msg=notification.text, registration_token=registration_token)

    return "success"


@notification.route('/admin/notification/addall', methods=['POST'])
@token_required_admin
def api_addall_admin(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user = User.query.all()

    title = data.get('title')
    text = data.get('text')
    category = data.get('category')

    data = datetime.now()

    # database ORM object
    notification = Notification(
        title=title,
        text=text,
        data=data,
        read_flag=False,
        category=category,
        user=user
    )
    # insert user
    db.session.add(notification)
    db.session.commit()

    registration_token = [user_it.push_token for user_it in user if user_it.push_token]
    sendPush(title=notification.title, msg=notification.text, registration_token=registration_token)

    return "success"


@notification.route('/api/notification/update', methods=['POST'])
@token_required
def api_update(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    notification_id = data.get('notification_id')
    read_flag = data.get('read_flag')

    notification = Notification.query.get(notification_id)
    if not notification:
        return "No notification"
    if read_flag is not None:
        notification.read_flag = int(json.loads(str(read_flag).lower()))

    db.session.commit()

    return "success"


@notification.route('/admin/notification/update', methods=['POST'])
@token_required_admin
def api_update_admin(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    notification_id = data.get('notification_id')
    title = data.get('title')
    text = data.get('text')
    read_flag = data.get('read_flag')
    category = data.get('category')

    notification = Notification.query.get(notification_id)
    if not notification:
        return "No notification"
    if text is not None:
        notification.text = text
    if title is not None:
        notification.title = title
    if read_flag is not None:
        notification.read_flag = int(json.loads(str(read_flag).lower()))
    if category is not None:
        notification.category = category

    db.session.commit()

    return "success"


@notification.route('/api/notification/delete', methods=['DELETE'])
@token_required
def api_delete(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    notification_id = data.get('notification_id')

    Notification.query.filter_by(notification_id=notification_id).delete()

    db.session.commit()

    return "success"


@notification.route('/api/notification/get', methods=['GET'])
@token_required
def api_get(current_user):

    user_id = current_user.user_id

    db.session.commit()

    if not (id or user_id):
        return page_not_found(404)

    notifications = current_user.notification

    output = []
    for notification in notifications:
        output.append({
            'notification_id': notification.notification_id,
            'title': notification.title,
            'text': notification.text,
            'data': notification.data,
            'read_flag': notification.read_flag,
            'category': notification.category
        })

    return jsonify({'notifications': output})
