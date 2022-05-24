from app import db, app
import uuid
from sqlalchemy_utils import StringEncryptedType
# Database ORMs
key = app.config['SECRET_KEY']

ItemNotification = db.Table('ItemDetail',
                            db.Column('id', db.Integer, primary_key=True),
                            db.Column('user_id', db.String, db.ForeignKey('user.user_id')),
                            db.Column('notification_id', db.String, db.ForeignKey('notification.notification_id')))


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    name = db.Column(StringEncryptedType(db.String(100), key))
    email = db.Column(StringEncryptedType(db.String(70), key), unique=True)
    password = db.Column(StringEncryptedType(db.String(80), key))
    phone = db.Column(StringEncryptedType(db.String(50), key))
    location = db.Column(StringEncryptedType(db.String(100), key))
    push_token = db.Column(StringEncryptedType(db.String, key))
    last_login = db.Column(StringEncryptedType(db.DateTime, key))
    ta_accept = db.Column(StringEncryptedType(db.Boolean, key), default=False)
    os_type = db.Column(StringEncryptedType(db.String(200), key))
    language = db.Column(StringEncryptedType(db.String(200), key))
    image = db.relationship("Image", back_populates="user")
    notification = db.relationship("Notification", secondary=ItemNotification, back_populates="user")
    order = db.relationship("Order", back_populates="user")
    orderdetails = db.relationship("Orderdetails", back_populates="user")


class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    image1 = db.Column(StringEncryptedType(db.String(), key))  # image table
    image2 = db.Column(StringEncryptedType(db.String(), key))  # image table
    orientation1 = db.Column(StringEncryptedType(db.String(), key), nullable=False)
    orientation2 = db.Column(StringEncryptedType(db.String(), key), nullable=False)  # image table
    disease = db.Column(StringEncryptedType(db.String(80), key))
    treatment = db.Column(StringEncryptedType(db.String(100), key))
    created_data = db.Column(StringEncryptedType(db.DateTime, key))
    updated_data = db.Column(StringEncryptedType(db.DateTime, key))
    category = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    lat = db.Column(StringEncryptedType(db.Float(), key))
    long = db.Column(StringEncryptedType(db.Float(), key))
    leaf_detected = db.Column(StringEncryptedType(db.Boolean, key))
    leaf_set_flag = db.Column(StringEncryptedType(db.Boolean, key))
    validated = db.Column(StringEncryptedType(db.Boolean, key))
    question = db.relationship("Question", back_populates="image")
    user = db.relationship("User", back_populates="image")


class Question(db.Model):
    __tablename__ = 'question'
    question_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    image_id = db.Column(db.String, db.ForeignKey('image.image_id'), nullable=False)
    question = db.Column(StringEncryptedType(db.String(), key))  # image table
    answer = db.Column(StringEncryptedType(db.String(), key))  # image table
    image = db.relationship("Image", back_populates="question")


class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    title = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    text = db.Column(StringEncryptedType(db.String, key))
    data = db.Column(StringEncryptedType(db.DateTime, key))
    read_flag = db.Column(StringEncryptedType(db.Boolean, key), nullable=False)
    category = db.Column(StringEncryptedType(db.String(80), key))
    user = db.relationship("User", secondary=ItemNotification, back_populates="notification")


class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    producer = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    name = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    image = db.Column(StringEncryptedType(db.String, key))
    description = db.Column(StringEncryptedType(db.String, key))
    price = db.Column(StringEncryptedType(db.Float, key))
    provider = db.Column(StringEncryptedType(db.String(80), key))
    stock = db.Column(StringEncryptedType(db.Integer, key))
    stock_flag = db.Column(StringEncryptedType(db.Boolean, key), nullable=False)
    product_details = db.relationship("Product_Details", back_populates="product")
    ordered_products = db.relationship("Ordered_Products", back_populates="product")


class Product_Details(db.Model):
    __tablename__ = 'product_details'
    product_details_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    field = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    pests = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    dose_Ha = db.Column(StringEncryptedType(db.Float, key))
    dose_1_m2 = db.Column(StringEncryptedType(db.Float, key))
    break_time = db.Column(StringEncryptedType(db.String(80), key))
    product = db.relationship("Product", back_populates="product_details")


class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    total_price = db.Column(StringEncryptedType(db.Float, key), nullable=False)
    status = db.Column(StringEncryptedType(db.String(80), key), nullable=False)
    created_data = db.Column(StringEncryptedType(db.DateTime, key))
    orderdetails_shipping_id = db.Column(db.Integer, db.ForeignKey('orderdetails.orderdetails_id'), nullable=False)
    orderdetails_billing_id = db.Column(db.Integer, db.ForeignKey('orderdetails.orderdetails_id'), nullable=False)
    payment_type = db.Column(StringEncryptedType(db.String(80), key))
    user = db.relationship("User", back_populates="order")
    ordered_products = db.relationship("Ordered_Products", back_populates="order")


class Ordered_Products(db.Model):
    __tablename__ = 'ordered_products'
    ordered_products_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    order_id = db.Column(db.String, db.ForeignKey('order.order_id'), nullable=False)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(StringEncryptedType(db.Integer, key), nullable=False)
    order = db.relationship("Order", back_populates="ordered_products")
    product = db.relationship("Product", back_populates="ordered_products")


class Orderdetails(db.Model):
    __tablename__ = 'orderdetails'
    orderdetails_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    order_type = db.Column(StringEncryptedType(db.String(20), key), nullable=False)
    email = db.Column(StringEncryptedType(db.String(70), key))
    first_name = db.Column(StringEncryptedType(db.String(50), key))
    second_name = db.Column(StringEncryptedType(db.String(50), key))
    phone = db.Column(StringEncryptedType(db.String(50), key))
    county = db.Column(StringEncryptedType(db.String(50), key))
    city = db.Column(StringEncryptedType(db.String(50), key))
    street = db.Column(StringEncryptedType(db.String(50), key))
    number = db.Column(StringEncryptedType(db.String(30), key))
    block = db.Column(StringEncryptedType(db.String(30), key))
    stairs = db.Column(StringEncryptedType(db.String(30), key))
    apartment = db.Column(StringEncryptedType(db.String(30), key))
    user = db.relationship("User", back_populates="orderdetails")


class Phyto(db.Model):
    __tablename__ = 'phyto'
    phyto_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    location = db.Column(StringEncryptedType(db.String(100), key))
    name = db.Column(StringEncryptedType(db.String(100), key))
    county = db.Column(StringEncryptedType(db.String(100), key))
    email = db.Column(StringEncryptedType(db.String(70), key))
    phone = db.Column(StringEncryptedType(db.String(50), key))
    hours = db.Column(StringEncryptedType(db.String(100), key))
