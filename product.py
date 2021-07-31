from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from models import Product
from datetime import datetime
from app import db, app

product = Blueprint('product', __name__)

@product.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@product.route('/api/product/all', methods=['GET'])
@token_required
def api_all(current_user):
    products = Product.query.all()
    output = []
    for product in products:
        output.append({
            'product_id': product.product_id,
            'producer': product.producer,
            'name': product.name,
            'image': product.image,
            'description': product.description,
            'price': product.price,
            'provider': product.provider,
            'stock': product.stock
        })

    return jsonify({'product': output})


@product.route('/api/product/add', methods=['POST'])
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

    producer = data.get('producer')
    name = data.get('name')
    image = data.get('image')
    description = data.get('description')
    price = data.get('price')
    provider = data.get('provider')
    stock = data.get('stock')

    # database ORM object
    product = Product(
        producer=producer,
        name=name,
        image=image,
        description=description,
        price=price,
        provider=provider,
        stock=stock
    )
    # insert user
    db.session.add(product)
    db.session.commit()

    return make_response('Success following a POST command', 201)


@product.route('/api/image/update', methods=['POST'])
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

    product_id = data.get('product_id')
    if product_id is not None and not Product.query.filter_by(product_id=product_id).first():
        output = {}

        if data.get('producer') is not None:
            output.update({"producer": data.get('producer')})
        if data.get('name') is not None:
            output.update({"name": data.get('name')})
        if data.get('image') is not None:
            output.update({"image": data.get('image')})
        if data.get('description') is not None:
            output.update({"description": data.get('description')})
        if data.get('price') is not None:
            output.update({"price": data.get('price')})
        if data.get('provider') is not None:
            output.update({"provider": data.get('provider')})
        if data.get('stock') is not None:
            output.update({"stock": data.get('stock')})

        Product.query.filter_by(image_id=product_id).update(output)

        db.session.commit()

        return make_response('Success following a POST command', 201)

    return make_response('Request has been accepted for processing, but processing has not completed', 202)

