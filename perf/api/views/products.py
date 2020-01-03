# -*- coding: utf-8 -*-
"""
    blueprints of products
    ~~~~~~~~~~~~~~~~~~~~~~
    author: limingli(limingli@lianjia.com)
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import traceback
from flask import Blueprint, jsonify
from ..models.product import Product
from ..utils.log import logger

products = Blueprint('products', __name__, url_prefix='/api/products')


@products.route('/', methods=['GET'])
def get_products():
    """
    @description: 获取所有产品线
    @param: None
    """
    product_dict = Product.query.all()
    products_all = []
    for p in product_dict:
        product = {"product_id": p.id, "product_name": p.name}
        products_all.append(product)
    # logger.info(products_all)
    data = {'products': products_all}
    res = {"code": 1, "msg": "success", "data": data}
    return jsonify(res)


@products.errorhandler(Exception)
def errorhandle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})

