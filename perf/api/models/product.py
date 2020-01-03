# -*- coding: utf-8 -*-
"""
    products mapper
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: limingli(limingli@lianjia.com)
"""

from db import db


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String)
    key = db.Column(db.String)
    business = db.Column(db.String)
    status = db.Column(db.Integer)

    def __init__(self):
        pass
