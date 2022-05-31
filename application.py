from app import app, db
from login import login, token_required
from login_admin import login_admin, token_required_admin
from models import User
from flask import request, jsonify, make_response
from image import image
from product import product
from order import order
from notification import notification
from mail import mail
import json

app.register_blueprint(login)
app.register_blueprint(login_admin)
app.register_blueprint(image)
app.register_blueprint(product)
app.register_blueprint(order)
app.register_blueprint(notification)
app.register_blueprint(mail)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>nothing here</h1>
<p>Planty.</p>'''


@app.route('/api/ta/update', methods=['POST'])
@token_required
def ta_accept(current_user):
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
    user.ta_accept = int(json.loads(str(data.get('ta_accept')).lower()))
    db.session.commit()

    return "succes"


# User Database Route
# this route sends back list of users users
@app.route('/admin/users', methods=['GET'])
@token_required_admin
def get_all_users(*_):
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
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'location': user.location
        })

    return jsonify({'users': output})


@app.route('/api/user/delete', methods=['DELETE'])
@token_required
def api_delete(current_user):

    user_id = current_user.user_id

    User.query.filter_by(user_id=user_id).delete()

    db.session.commit()

    return "success"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(debug=True, host="0.0.0.0", port=8080)
