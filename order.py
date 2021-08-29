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
            'created_data': order.created_data,
            'orderdetails_shipping_id': order.orderdetails_shipping_id,
            'orderdetails_billing_id': order.orderdetails_billing_id,
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
    created_data = datetime.now()
    orderdetails_shipping_id = data.get('orderdetails_shipping_id')
    orderdetails_billing_id = data.get('orderdetails_billing_id')
    payment_type = data.get('payment_type')

    # database ORM object
    order = Order(
        user_id=user_id,
        total_price=total_price,
        status=status,
        created_data=created_data,
        orderdetails_shipping_id=orderdetails_shipping_id,
        orderdetails_billing_id=orderdetails_billing_id,
        payment_type=payment_type
    )

    db.session.add(order)
    db.session.commit()
    try:
        cart = json.loads(data.get("cart"))# database ORM object
        for product in cart:
            ordered_product = Ordered_Products(
                order_id=order.order_id,
                product_id=product,
                quantity=cart.get(product),
            )

            db.session.add(ordered_product)
            db.session.commit()
    except:
        Order.query.filter_by(order_id=order.order_id).delete()
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
def api_ordered_all(current_user):
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
    first_name = data.get('first_name')
    second_name = data.get('second_name')
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
        first_name=first_name,
        second_name=second_name,
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

    output_shipping = []
    output_billing = []
    for orderdetails in orderdetails_list:
        obj={
            'orderdetails_id': orderdetails.orderdetails_id,
            'user_id': orderdetails.user_id,
            'order_type': orderdetails.order_type,
            'email': orderdetails.email,
            'first_name': orderdetails.first_name,
            'second_name': orderdetails.second_name,
            'phone': orderdetails.phone,
            'county': orderdetails.county,
            'city': orderdetails.city,
            'street': orderdetails.street,
            'number': orderdetails.number,
            'block': orderdetails.block,
            'stairs': orderdetails.stairs,
            'apartment': orderdetails.apartment
        }
        if orderdetails.order_type == "0":
            output_shipping.append(obj)
        else:
            output_billing.append(obj)

    return jsonify({'orderdetails': [{"shipping": output_shipping}, {"billing": output_billing}]})


@order.route('/api/order/shipping-details/update', methods=['POST'])
@token_required
def api_shiping_update(current_user):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    orderdetails_id = data.get('orderdetails.orderdetails_id')
    email = data.get('orderdetails.email')
    first_name = data.get('orderdetails.first_name')
    second_name = data.get('orderdetails.second_name')
    phone = data.get('orderdetails.phone')
    county = data.get('orderdetails.county')
    city = data.get('orderdetails.city')
    street = data.get('orderdetails.street')
    number = data.get('orderdetails.number')
    block = data.get('orderdetails.block')
    stairs = data.get('orderdetails.stairs')
    apartment = data.get('orderdetails.apartment')

    orderdetails=Orderdetails.query.get(orderdetails_id)

    if email is not None:
        orderdetails.email = email
    if first_name is not None:
        orderdetails.first_name = first_name
    if second_name is not None:
        orderdetails.second_name = second_name
    if phone is not None:
        orderdetails.phone = phone
    if county is not None:
        orderdetails.county = county
    if city is not None:
        orderdetails.city = city
    if street is not None:
        orderdetails.street = street
    if street is not None:
        orderdetails.street = street
    if number is not None:
        orderdetails.number = number
    if block is not None:
        orderdetails.block = block
    if stairs is not None:
        orderdetails.stairs = stairs
    if apartment is not None:
        orderdetails.apartment = apartment

    db.session.commit()

    return "success"


@order.route('/api/order/shipping-details/delete', methods=['DELETE'])
@token_required
def api_delete(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    orderdetails_id = data.get('orderdetails_id')

    Orderdetails.query.filter_by(orderdetails_id=orderdetails_id).delete()

    db.session.commit()

    return "success"
