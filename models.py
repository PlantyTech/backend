from app import db
# Database ORMs

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))
    # image = db.relationship('Image', backref=db.backref('client', lazy=True))


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String(100))
    image = db.Column(db.String, nullable=False)
    disease = db.Column(db.String(80))
    treatment = db.Column(db.String(100))
    data1 = db.Column(db.DateTime)
    data2 = db.Column(db.DateTime)
