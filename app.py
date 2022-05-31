# flask imports
from flask import Flask, request, jsonify, make_response
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import firebase_admin
from firebase_admin import credentials, messaging
from flask_cors import CORS
import detection
from flask_mail import Mail
import boto3
import base64
from botocore.exceptions import ClientError
SECRET_KEY = ""
MAIL_PASSWORD = ""


def get_secret():
    secret_name = "PlantyAI"
    region_name = "eu-central-1"
    global SECRET_KEY
    global MAIL_PASSWORD

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SECRET_KEY' in get_secret_value_response:
            SECRET_KEY = get_secret_value_response['SECRET_KEY']
        if 'MAIL_PASSWORD' in get_secret_value_response:
            MAIL_PASSWORD = get_secret_value_response['MAIL_PASSWORD']


get_secret()
print(SECRET_KEY, MAIL_PASSWORD)
# creates Flask object
app = Flask(__name__)
# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = SECRET_KEY
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200/*"}})

cred = credentials.Certificate('./plantyai-firebase-adminsdk-v8bx3-b11e46feef.json')
firebase_admin.initialize_app(cred)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "plantytech@gmail.com",
    "MAIL_PASSWORD": MAIL_PASSWORD
}
app.config.update(mail_settings)
mail_service = Mail(app)

detection_function = detection.get_detection_function()


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
