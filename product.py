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
        if product.stock_flag:
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
        stock=stock,
        stock_flag=True
    )
    # insert user
    db.session.add(product)
    db.session.commit()

    return make_response('Success following a POST command', 201)


@product.route('/api/product/update', methods=['POST'])
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
    if product_id is not None and not Product.query.get(product_id):
        output = {}

        if data.get('producer') is not None and len(data.get('producer')) > 0:
            output.update({"producer": data.get('producer')})
        if data.get('name') is not None and len(data.get('name')) > 0:
            output.update({"name": data.get('name')})
        if data.get('image') is not None and len(data.get('image')) > 0:
            output.update({"image": data.get('image')})
        if data.get('description') is not None and len(data.get('description')) > 0:
            output.update({"description": data.get('description')})
        if data.get('price') is not None and len(data.get('price')) > 0:
            output.update({"price": data.get('price')})
        if data.get('provider') is not None and len(data.get('provider')) > 0:
            output.update({"provider": data.get('provider')})
        if data.get('stock') is not None and len(data.get('stock')) > 0:
            output.update({"stock": data.get('stock')})
        if data.get('stock_flag') is not None and len(data.get('stock_flag')) > 0:
            output.update({"stock_flag": (data.get('stock_flag'))})

        Product.query.get(product_id).update(output)

        db.session.commit()

        return make_response('Success following a POST command', 201)

    return make_response('Request has been accepted for processing, but processing has not completed', 202)

