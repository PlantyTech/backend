from app import app, db
from login import login, token_required
from models import User, Image
from flask import request, jsonify
from image import image
from product import product
from order import order
from notification import notification

app.register_blueprint(login)
app.register_blueprint(image)
app.register_blueprint(product)
app.register_blueprint(order)
app.register_blueprint(notification)


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
@app.route('/api/users', methods=['GET'])
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
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'location': user.location
        })

    return jsonify({'users': output})

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debuger shell
    # if you hit an error while running the server
    app.run(debug=True, host="0.0.0.0", port=8080)
