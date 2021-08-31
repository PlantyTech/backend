# flask imports
from flask import Flask, request, jsonify, make_response
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, messaging
from flask_cors import CORS

# creates Flask object
app = Flask(__name__)
# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = 'Plantai_01'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200/*"}})

cred = credentials.Certificate('./plantyai-firebase-adminsdk-v8bx3-89961ffaed.json')
firebase_admin.initialize_app(cred)


def sendPush(title, msg, registration_token):
    # See documentation on defining a message payload.
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=msg
            ),
            tokens=registration_token,
        )

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send_multicast(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)
    except:
        print('error: ')
        print(registration_token)
