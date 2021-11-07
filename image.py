from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from models import Image, Notification, User, Question
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
    questions = []
    for image in images:
        link1 = boto3.client('s3').generate_presigned_url('get_object',
                                                          Params={'Bucket': 'plantyai-api', 'Key': image.image1},
                                                          ExpiresIn=120)
        link2 = boto3.client('s3').generate_presigned_url('get_object',
                                                          Params={'Bucket': 'plantyai-api', 'Key': image.image2},
                                                          ExpiresIn=120)
        for question in image.questions:
            questions.append({
                'question': question.question,
                'answer': question.answer
            })
        output.append({
            'image_id': image.image_id,
            'user_id': image.user_id,
            'image1': link1,
            'image2': link2,
            'orientation1': image.orientation1,
            'orientation2': image.orientation2,
            'disease': image.disease,
            'treatment': image.treatment,
            'created_data': image.created_data,
            'updated_data': image.updated_data,
            'lat': image.lat,
            'long': image.long,
            'category': image.category,
            'questions': questions
        })

    return jsonify({'images': output})


@image.route('/api/image/add', methods=['POST'])
@token_required
def api_add(current_user):
    try:
        if request.form is not None:
            data = request.form
            print(data)
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
        file1 = request.files["image1"]
        file2 = request.files["image2"]
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user_id = current_user.user_id
    category = data.get('category')
    orientation1 = data.get('orientation1')
    orientation2 = data.get('orientation2')
    created_data = datetime.now()
    lat = data.get('lat')
    long = data.get('long')
    # database ORM object
    image = Image(
        image1=None,
        image2=None,
        orientation1=orientation1,
        orientation2=orientation2,
        user_id=user_id,
        disease=None,
        treatment=None,
        created_data=created_data,
        updated_data=None,
        lat=lat,
        long=long,
        questions=None,
        category=category
    )
    # insert user
    db.session.add(image)
    db.session.commit()

    for i in range(int(data.get('questions_number'))):
        question = Question(
            image_id=image.image_id,
            question=data.get('question'+str(i)),
            answer=data.get('answer'+str(i))
        )
        db.session.add(question)

    dir = os.path.join("temp", image.category)
    if not os.path.exists(dir):
        os.mkdir(dir)

    image.image1 = image.category+"/"+str(image.image_id)+'.'+file1.filename.split('.')[1]
    image.image2 = image.category+"/"+str(image.image_id)+'.'+file1.filename.split('.')[1]
    file1.save("temp/"+image.image1)
    file1.save("temp/"+image.image2)
    boto3.resource('s3').Bucket('plantyai-api').upload_file("temp/"+image.image1, image.image1,
                                                            ExtraArgs={"ContentType": 'image/jpeg'})
    boto3.resource('s3').Bucket('plantyai-api').upload_file("temp/"+image.image2, image.image2,
                                                            ExtraArgs={"ContentType": 'image/jpeg'})
    os.remove("temp/"+image.image1)
    os.remove("temp/"+image.image2)

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
    questions = []
    for image in images:
        link1 = boto3.client('s3').generate_presigned_url('get_object',
                                                          Params={'Bucket': 'plantyai-api', 'Key': image.image1},
                                                          ExpiresIn=120)
        link2 = boto3.client('s3').generate_presigned_url('get_object',
                                                          Params={'Bucket': 'plantyai-api', 'Key': image.image2},
                                                          ExpiresIn=120)
        for question in image.questions:
            questions.append({
                'question': question.question,
                'answer': question.answer
            })
        output.append({
            'image_id': image.image_id,
            'user_id': image.user_id,
            'image1': link1,
            'image2': link2,
            'orientation1': image.orientation1,
            'orientation2': image.orientation2,
            'disease': image.disease,
            'treatment': image.treatment,
            'created_data': image.created_data,
            'updated_data': image.updated_data,
            'lat': image.lat,
            'long': image.long,
            'category': image.category,
            'questions': questions
        })

    return jsonify({'images': output})
