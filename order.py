from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from login_admin import token_required_admin
from models import Order, Ordered_Products, Product, User, Orderdetails
from datetime import datetime
from app import db, mail_service, CONTACT
from flask_mail import Message

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
        output_shipping = Orderdetails.query.get(order.orderdetails_shipping_id)
        output_billing = Orderdetails.query.get(order.orderdetails_billing_id)
        output.append({
            'order_id': order.order_id,
            'user_id': order.user_id,
            'total_price': order.total_price,
            'status': order.status,
            'created_data': order.created_data,
            'orderdetails': {
                "shipping": {
                    'orderdetails_id': output_shipping.orderdetails_id,
                    'user_id': output_shipping.user_id,
                    'order_type': output_shipping.order_type,
                    'email': output_shipping.email,
                    'first_name': output_shipping.first_name,
                    'second_name': output_shipping.second_name,
                    'phone': output_shipping.phone,
                    'county': output_shipping.county,
                    'city': output_shipping.city,
                    'street': output_shipping.street,
                    'number': output_shipping.number,
                    'block': output_shipping.block,
                    'stairs': output_shipping.stairs,
                    'apartment': output_shipping.apartment},
                "billing": {
                    'orderdetails_id': output_billing.orderdetails_id,
                    'user_id': output_billing.user_id,
                    'order_type': output_billing.order_type,
                    'email': output_billing.email,
                    'first_name': output_billing.first_name,
                    'second_name': output_billing.second_name,
                    'phone': output_billing.phone,
                    'county': output_billing.county,
                    'city': output_billing.city,
                    'street': output_billing.street,
                    'number': output_billing.number,
                    'block': output_billing.block,
                    'stairs': output_billing.stairs,
                    'apartment': output_billing.apartment}},
            'payment_type': order.payment_type
        })

    return jsonify({'order': output})


@order.route('/admin/order/all', methods=['GET'])
@token_required_admin
def api_all_admin(*_):

    orders = Order.query.all()

    output = []
    for order in orders:
        output_shipping = Orderdetails.query.get(order.orderdetails_shipping_id)
        output_billing = Orderdetails.query.get(order.orderdetails_billing_id)

        output.append({
            'order_id': order.order_id,
            'user_id': order.user_id,
            'total_price': order.total_price,
            'status': order.status,
            'created_data': order.created_data,
            'orderdetails': {
                "shipping": {
                    'orderdetails_id': output_shipping.orderdetails_id,
                    'user_id': output_shipping.user_id,
                    'order_type': output_shipping.order_type,
                    'email': output_shipping.email,
                    'first_name': output_shipping.first_name,
                    'second_name': output_shipping.second_name,
                    'phone': output_shipping.phone,
                    'county': output_shipping.county,
                    'city': output_shipping.city,
                    'street': output_shipping.street,
                    'number': output_shipping.number,
                    'block': output_shipping.block,
                    'stairs': output_shipping.stairs,
                    'apartment': output_shipping.apartment},
                "billing": {
                    'orderdetails_id': output_billing.orderdetails_id,
                    'user_id': output_billing.user_id,
                    'order_type': output_billing.order_type,
                    'email': output_billing.email,
                    'first_name': output_billing.first_name,
                    'second_name': output_billing.second_name,
                    'phone': output_billing.phone,
                    'county': output_billing.county,
                    'city': output_billing.city,
                    'street': output_billing.street,
                    'number': output_billing.number,
                    'block': output_billing.block,
                    'stairs': output_billing.stairs,
                    'apartment': output_billing.apartment}},
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
            if CONTACT == "True":
                msg = Message(subject="Comanda noua!!!",
                              sender="PlantyAI",
                              recipients=["contact@plantytech.com"],
                              body="Comanda noua!!!")
                mail_service.send(msg)
            user = User.query.get(user_id)
            msg = Message(subject="Confirmare comanda",
                          sender="PlantyAI",
                          recipients=[user.email],
                          body="Buna ziua,\n\n"
                               "Comanda dumneavostra a fost inregistrata cu succes. "
                               "Ne ocupam de ea cat mai curand posibil.\n\n"
                               "Cu respect,\nEchipa PlantyAI")
            mail_service.send(msg)
    except:
        Order.query.filter_by(order_id=order.order_id).delete()
        db.session.commit()
    return make_response('Success following a POST command', 201)


@order.route('/admin/order/update', methods=['POST'])
@token_required_admin
def api_update_admin(*_):
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
def api_ordered_all(*_):
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


@order.route('/admin/ordered_products/all', methods=['GET'])
@token_required_admin
def api_ordered_all_admin(*_):
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

    order = Order.query.get(order_id)

    if not order:
        return "No order"
    ordered_products = order.ordered_products

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
        if not orderdetails.deleted_flag:
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


@order.route('/admin/order/shipping-details/all', methods=['GET'])
@token_required_admin
def api_order_details_all_admin(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    user_id = data.get('user_id')

    db.session.commit()

    if not (id or user_id):
        return page_not_found(404)

    user = User.query.get(user_id)

    if not user:
        return "No user"
    orderdetails_list = user.orderdetails

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
def api_shiping_update(*_):
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

    Orderdetails.query.get(orderdetails_id).deleted_flag = int(json.loads(str(True).lower()))
    db.session.commit()

    return "success"
