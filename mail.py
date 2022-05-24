from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "plantytech@gmail.com",
    "MAIL_PASSWORD": "Timi1234!!"
}

app.config.update(mail_settings)
mail = Mail(app)

if __name__ == '__main__':
    with app.app_context():
        msg = Message(subject="Hello",
                      sender="Planty Tech",
                      recipients=["tofenimarius@yahoo.com"], # replace with your email for testing
                      body="Nu mai schimba 100 de parole")
        mail.send(msg)