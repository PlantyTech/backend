from app import db
import uuid
# Database ORMs

ItemNotification = db.Table('ItemDetail',
                            db.Column('id', db.Integer, primary_key=True),
                            db.Column('user_id', db.String, db.ForeignKey('user.user_id')),
                            db.Column('notification_id', db.String, db.ForeignKey('notification.notification_id')))


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))
    phone = db.Column(db.String(50))
    location = db.Column(db.String(100))
    push_token = db.Column(db.String(200))
    last_login = db.Column(db.DateTime)
    ta_accept = db.Column(db.Boolean, default=False)
    os_type = db.Column(db.String(200))
    language = db.Column(db.String(200))
    image = db.relationship("Image", back_populates="user")
    notification = db.relationship("Notification", secondary=ItemNotification, back_populates="user")
    order = db.relationship("Order", back_populates="user")
    orderdetails = db.relationship("Orderdetails", back_populates="user")


class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    image = db.Column(db.String, nullable=False)
    orientation = db.Column(db.String, nullable=False)
    disease = db.Column(db.String(80))
    treatment = db.Column(db.String(100))
    created_data = db.Column(db.DateTime)
    updated_data = db.Column(db.DateTime)
    category = db.Column(db.String(80), nullable=False)
    user = db.relationship("User", back_populates="image")


class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String)
    data = db.Column(db.DateTime)
    read_flag = db.Column(db.Boolean, nullable=False)
    category = db.Column(db.String(80))
    user = db.relationship("User", secondary=ItemNotification, back_populates="notification")


class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    producer = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Float)
    provider = db.Column(db.String(80))
    stock = db.Column(db.Integer)
    stock_flag = db.Column(db.Boolean, nullable=False)
    product_details = db.relationship("Product_Details", back_populates="product")
    ordered_products = db.relationship("Ordered_Products", back_populates="product")


class Product_Details(db.Model):
    __tablename__ = 'product_details'
    product_details_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    field = db.Column(db.String(80), nullable=False)
    pests = db.Column(db.String(80), nullable=False)
    dose_Ha = db.Column(db.Float)
    dose_1_m2 = db.Column(db.Float)
    break_time = db.Column(db.String(80))
    product = db.relationship("Product", back_populates="product_details")


class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    created_data = db.Column(db.DateTime)
    orderdetails_shipping_id = db.Column(db.Integer, db.ForeignKey('orderdetails.orderdetails_id'), nullable=False)
    orderdetails_billing_id = db.Column(db.Integer, db.ForeignKey('orderdetails.orderdetails_id'), nullable=False)
    payment_type = db.Column(db.String(80))
    user = db.relationship("User", back_populates="order")
    ordered_products = db.relationship("Ordered_Products", back_populates="order")


class Ordered_Products(db.Model):
    __tablename__ = 'ordered_products'
    ordered_products_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    order_id = db.Column(db.String, db.ForeignKey('order.order_id'), nullable=False)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship("Order", back_populates="ordered_products")
    product = db.relationship("Product", back_populates="ordered_products")


class Orderdetails(db.Model):
    __tablename__ = 'orderdetails'
    orderdetails_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(70))
    first_name = db.Column(db.String(50))
    second_name = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    county = db.Column(db.String(50))
    city = db.Column(db.String(50))
    street = db.Column(db.String(50))
    number = db.Column(db.String(30))
    block = db.Column(db.String(30))
    stairs = db.Column(db.String(30))
    apartment = db.Column(db.String(30))
    user = db.relationship("User", back_populates="orderdetails")


class Phyto(db.Model):
    __tablename__ = 'phyto'
    phyto_id = db.Column(db.String, default=lambda: uuid.uuid4().hex, primary_key=True)
    location = db.Column(db.String(100))
    name = db.Column(db.String(100))
    county = db.Column(db.String(100))
    email = db.Column(db.String(70))
    phone = db.Column(db.String(50))
    hours = db.Column(db.String(100))
