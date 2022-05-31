from flask import Blueprint, make_response
from flask import request, jsonify
import json
from login import token_required
from login_admin import token_required_admin
from models import Product
from datetime import datetime
from app import db, app

product = Blueprint('product', __name__)

@product.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@product.route('/api/product/all', methods=['GET'])
@token_required
def api_all(*_):
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


@product.route('/admin/product/all', methods=['GET'])
@token_required_admin
def api_all_admin(*_):
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


@product.route('/api/product/search', methods=['GET'])
@token_required
def api_search(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    products = Product.query.all()
    output = []
    search = data.get("search")
    for product in products:
        if product.stock_flag:
            if (search in product.producer or
                    search in product.name or
                    search in product.description or
                    search is None):
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


@product.route('/admin/product/search', methods=['GET'])
@token_required_admin
def api_search_admin(*_):
    try:
        if request.json is not None:
            data = request.json
        elif request.args is not None:
            data = request.args
        else:
            data = json.loads(request.data)
    except:
        return make_response('Request had bad syntax or was impossible to fulfill', 400)

    products = Product.query.all()
    output = []
    search = data.get("search")
    for product in products:
        if product.stock_flag:
            if (search in product.producer or
                    search in product.name or
                    search in product.description or
                    search is None):
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


@product.route('/admin/product/add', methods=['POST'])
@token_required_admin
def api_add(*_):
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


@product.route('/admin/product/update', methods=['POST'])
@token_required_admin
def api_update(*_):
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
    product=Product.query.get(product_id)
    if product is not None:

        if data.get('producer') is not None and len(data.get('producer')) > 0:
            product.producer = data.get('producer')
        if data.get('name') is not None and len(data.get('name')) > 0:
            product.name = data.get('name')
        if data.get('image') is not None and len(data.get('image')) > 0:
            product.image = data.get('image')
        if data.get('description') is not None and len(data.get('description')) > 0:
            product.description = data.get('description')
        if data.get('price') is not None and len(data.get('price')) > 0:
            product.price = data.get('price')
        if data.get('provider') is not None and len(data.get('provider')) > 0:
            product.provider = data.get('provider')
        if data.get('stock') is not None and len(data.get('stock')) > 0:
            product.stock = data.get('stock')
        if data.get('stock_flag') is not None and len(data.get('stock_flag')) > 0:
            product.stock_flag = int(json.loads(str(data.get('stock_flag')).lower()))

        db.session.commit()

        return make_response('Success following a POST command', 201)

    return make_response('Request has been accepted for processing, but processing has not completed', 202)

