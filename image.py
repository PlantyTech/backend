from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from models import Image
from datetime import datetime
from app import db, app

image = Blueprint('image', __name__)

@image.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@image.route('/api/image/all', methods=['GET'])
@token_required
def api_all(current_user):
    images = Image.query.all()
    output = []
    for image in images:
        output.append({
            'image_id': image.image_id,
            'user_id': image.user_id,
            'image': image.image,
            'disease': image.disease,
            'treatment': image.treatment,
            'data1': image.data1,
            'data2': image.data2,
            'category': image.category
        })

    return jsonify({'images': output})


@image.route('/api/image/add', methods=['POST'])
@token_required
def api_add(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user_id, image, category = current_user.user_id, data.get('image'), data.get('category')

    data1 = datetime.now()

    # database ORM object
    image = Image(
        image=image,
        user_id=user_id,
        disease=None,
        treatment=None,
        data1=data1,
        data2=None,
        category=category
    )
    # insert user
    db.session.add(image)
    db.session.commit()

    return "success"


@image.route('/api/image/update', methods=['POST'])
@token_required
def api_update(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    image_id, disease, treatment = data.get('image_id'), data.get('disease'), data.get('treatment')

    data2 = datetime.now()

    Image.query.filter_by(image_id=image_id).update({"disease": disease, "treatment": treatment, "data2": data2})

    db.session.commit()

    return "success"


@image.route('/api/image/get', methods=['GET'])
@token_required
def api_get(current_user):

    user_id = current_user.user_id

    db.session.commit()

    if not (id or user_id):
        return page_not_found(404)

    images = Image.query.filter_by(user_id=user_id)

    output = []
    for image in images:
        output.append({
            'image_id': image.image_id,
            'user_id': image.user_id,
            'image': image.image,
            'disease': image.disease,
            'treatment': image.treatment,
            'data1': image.data1,
            'data2': image.data2,
            'category': image.category
        })

    return jsonify({'images': output})
