from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from models import Image, Notification, User
from datetime import datetime
from app import db, sendPush
image = Blueprint('image', __name__)
import boto3
import os


@image.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@image.route('/api/image/all', methods=['GET'])
@token_required
def api_all(current_user):
    images = Image.query.all()
    output = []
    for image in images:
        link = [boto3.client('s3').generate_presigned_url('get_object',
                                                          Params={'Bucket': 'plantyai-api', 'Key': image_i},
                                                          ExpiresIn=120)
                for image_i in image.image]

        output.append({
            'image_id': image.image_id,
            'user_id': image.user_id,
            'image': link,
            'orientation': image.orientation,
            'disease': image.disease,
            'treatment': image.treatment,
            'created_data': image.created_data,
            'updated_data': image.updated_data,
            'lat': image.lat,
            'long': image.long,
            'category': image.category,
            'questions': image.questions
        })

    return jsonify({'images': output})


@image.route('/api/image/add', methods=['POST'])
@token_required
def api_add(current_user):
    try:
        if request.form is not None:
            data = request.form
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
        file = request.files.getlist('image[]')  # to check if this is ok
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user_id = current_user.user_id
    image = data.get('category')
    category = data.get('category')
    orientation = data.get('orientation')  # to check if is array or is string
    created_data = datetime.now()
    # database ORM object
    image = Image(
        image=image,
        orientation=orientation,
        user_id=user_id,
        disease=None,
        treatment=None,
        created_data=created_data,
        updated_data=None,
        category=category
    )
    # insert user
    db.session.add(image)
    db.session.commit()

    dir = os.path.join("temp", image.category)
    if not os.path.exists(dir):
        os.mkdir(dir)

    image.image = [image.category+"/"+str(image.image_id)+'.'+file_i.filename.split('.')[1] for file_i in file]
    for i, image_i in enumerate(image.image):
        filepath=image_i
        file[i].save("temp/"+filepath)
        boto3.resource('s3').Bucket('plantyai-api').upload_file("temp/"+filepath, filepath,
                                                                ExtraArgs={"ContentType": 'image/jpeg'})
        os.remove("temp/"+filepath)

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

    image_id = data.get('image_id')
    disease = data.get('disease')
    treatment = data.get('treatment')

    updated_data = datetime.now()

    image = Image.query.get(image_id)
    image.disease = disease
    image.treatment = treatment
    image.updated_data = updated_data

    image_user = User.query.get(image.user_id)
    notification = Notification(
        title="Noutati despre o imagine adaugata",
        text="Avem noutati despre poza din categoria " + image.category +
             " din data " + image.created_data.strftime("%d/%m/%Y, %H:%M") + ". Intra sa verifici in aplicatie",
        data=updated_data,
        read_flag=False,
        category=image.category,
        user=[image_user]
    )
    # insert notification
    db.session.add(notification)
    db.session.commit()
    registration_token = [user_it.push_token for user_it in [image_user] if user_it.push_token]
    sendPush(title=notification.title, msg=notification.text, registration_token=registration_token)

    return "success"


@image.route('/api/image/get', methods=['GET'])
@token_required
def api_get(current_user):

    user_id = current_user.user_id

    db.session.commit()

    if not (id or user_id):
        return page_not_found(404)

    images = current_user.image

    output = []
    for image in images:
        link = [boto3.client('s3').generate_presigned_url('get_object',
                                                          Params={'Bucket': 'plantyai-api', 'Key': image_i},
                                                          ExpiresIn=120)
                for image_i in image.image]

        output.append({
            'image_id': image.image_id,
            'user_id': image.user_id,
            'image': link,
            'orientation': image.orientation,
            'disease': image.disease,
            'treatment': image.treatment,
            'created_data': image.created_data,
            'updated_data': image.updated_data,
            'lat': image.lat,
            'long': image.long,
            'category': image.category,
            'questions': image.questions
        })

    return jsonify({'images': output})
