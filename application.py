from app import app, db
from login import login, token_required
from models import User, Image
from flask import request, jsonify
from datetime import datetime


app.register_blueprint(login)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>nothing here</h1>
<p>Planty.</p>'''


# User Database Route
# this route sends back list of users users
@login.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email
        })

    return jsonify({'users': output})


@app.route('/api/all', methods=['GET'])
@token_required
def api_all(current_user):
    images = Image.query.all()
    output = []
    for image in images:
        output.append({
            'id': image.id,
            'image': image.image,
            'client': image.client,
            'disease': image.disease,
            'treatment': image.treatment,
            'data1': image.data1,
            'data2': image.data2
        })

    return jsonify({'images': output})


@app.route('/api/add', methods=['POST'])
@token_required
def api_add(current_user):
    data = request.json

    client, image = data.get('client'), data.get('image')

    data1 = datetime.now()

    # database ORM object
    image = Image(
        image=image,
        client=client,
        disease=None,
        treatment=None,
        data1=data1,
        data2=None
    )
    '''
    user = User.query \
        .filter_by(name=client) \
        .first()

    user.image.append(image)
    '''
    # insert user
    db.session.add(image)
    db.session.commit()

    return "success"


@app.route('/api/update', methods=['GET'])
@token_required
def api_update(current_user):
    data = request.json

    img_id, disease, treatment = data.get('id'), data.get('disease'), data.get('treatment')

    data2 = datetime.now()

    Image.query.filter_by(id=img_id).update({"disease": disease, "treatment": treatment, "data2": data2})

    db.session.commit()

    return "success"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/get', methods=['GET'])
@token_required
def api_get(current_user):
    data = request.json

    client = data.get('client')

    db.session.commit()

    if not (id or client):
        return page_not_found(404)

    images = Image.query.filter_by(client=client)

    output = []
    for image in images:
        output.append({
            'id': image.id,
            'image': image.image,
            'client': image.client,
            'disease': image.disease,
            'treatment': image.treatment,
            'data1': image.data1,
            'data2': image.data2
        })

    return jsonify({'images': output})


if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(debug=True, host="0.0.0.0", port=8080)
