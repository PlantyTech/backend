from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from models import Order, Ordered_Products, Product, User, Orderdetails
from datetime import datetime
from app import db, app

order = Blueprint('order', __name__)


@order.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@order.route('/api/order/all', methods=['GET'])
@token_required
def api_all(current_user):

    user_id = current_user.user_id

    db.session.commit()

    if not (id or user_id):
        return page_not_found(404)

    orders = User.query.get(user_id).order

    output = []
    for order in orders:
        output.append({
            'order_id': order.order_id,
            'user_id': order.user_id,
            'total_price': order.total_price,
            'status': order.status,
            'data1': order.data1,
            'orderdetails_id_l': order.orderdetails_id_l,
            'orderdetails_id_f': order.orderdetails_id_f,
            'payment_type': order.payment_type
        })

    return jsonify({'order': output})


@order.route('/api/order/add', methods=['POST'])
@token_required
def api_add(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user_id = current_user.user_id
    total_price = data.get('total_price')
    status = "In progres"
    data1 = datetime.now()
    orderdetails_id_l = data.get('orderdetails_id_l')
    orderdetails_id_f = data.get('orderdetails_id_f')
    payment_type = data.get('payment_type')

    # database ORM object
    order = Order(
        user_id=user_id,
        total_price=total_price,
        status=status,
        data1=data1,
        orderdetails_id_l=orderdetails_id_l,
        orderdetails_id_f=orderdetails_id_f,
        payment_type=payment_type
    )

    # insert user
    db.session.add(order)
    db.session.commit()

    cart=data.get("cart")# database ORM object
    for product in cart:
        ordered_product = Ordered_Products(
            order_id=order.order_id,
            product_id=product,
            quantity=product.get(product),
        )

        # insert user
        db.session.add(ordered_product)
        db.session.commit()

    return make_response('Success following a POST command', 201)


@order.route('/api/order/update', methods=['POST'])
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

    order_id = data.get('order_id')
    if order_id is not None and not Order.query.get(order_id):
        output = {}
        if data.get('status') is not None and len(data.get('status')) > 0:
            output.update({"status": data.get('status')})

        Order.query.get(order_id).update(output)

        db.session.commit()

        return make_response('Success following a POST command', 201)

    return make_response('Request has been accepted for processing, but processing has not completed', 202)


@order.route('/api/ordered_products/all', methods=['GET'])
@token_required
def api_ordered_update(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    order_id = data.get('order_id')

    db.session.commit()

    if not (id or order_id):
        return page_not_found(404)

    ordered_products = Order.query.get(order_id).ordered_products

    output = []
    for ordered_product in ordered_products:
        product = Product.query.get(ordered_product.product_id)
        output.append({
            'name': product.name,
            'image': product.image,
            'price': product.price,
            'provider': product.provider,
            'quantity': ordered_product.quantity
        })

    return jsonify({'ordered_products': output})


@order.route('/api/order/shipping-details/add', methods=['POST'])
@token_required
def api_order_details_add(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user_id = current_user.user_id
    order_type = data.get('order_type')
    email = data.get('email')
    FirstName = data.get('FirstName')
    SecondName = data.get('SecondName')
    phone = data.get('phone')
    county = data.get('county')
    city = data.get('city')
    street = data.get('street')
    number = data.get('number')
    block = data.get('block')
    stairs = data.get('stairs')
    apartment = data.get('apartment')

    # database ORM object
    orderdetails = Orderdetails(
        user_id=user_id,
        order_type=order_type,
        email=email,
        FirstName=FirstName,
        SecondName=SecondName,
        phone=phone,
        county=county,
        city=city,
        street=street,
        number=number,
        block=block,
        stairs=stairs,
        apartment=apartment
    )

    # insert user
    db.session.add(orderdetails)
    db.session.commit()

    return make_response('Success following a POST command', 201)


@order.route('/api/order/shipping-details/all', methods=['GET'])
@token_required
def api_order_details_all(current_user):

    user_id = current_user.user_id

    db.session.commit()

    if not (id or user_id):
        return page_not_found(404)

    orderdetails_list = User.query.get(user_id).orderdetails

    output = []
    for orderdetails in orderdetails_list:
        output.append({
            'orderdetails_id': orderdetails.orderdetails_id,
            'user_id': orderdetails.user_id,
            'order_type': orderdetails.order_type,
            'email': orderdetails.email,
            'FirstName': orderdetails.FirstName,
            'SecondName': orderdetails.SecondName,
            'phone': orderdetails.phone,
            'county': orderdetails.county,
            'city': orderdetails.city,
            'street': orderdetails.street,
            'number': orderdetails.number,
            'block': orderdetails.block,
            'stairs': orderdetails.stairs,
            'apartment': orderdetails.apartment
        })

    return jsonify({'orderdetails': output})

