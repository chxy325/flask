# -*- coding: utf-8 -*-
"""
    scripts mapper
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: limingli(limingli@lianjia.com)
"""

from db import db
from sqlalchemy.sql import func
# from jmeter import Jmeter


class Script(db.Model):
    """
    脚本表
    """

    __tablename__ = 'script'

    id = db.Column(db.BigInteger, primary_key=True)
    prd_id = db.Column(db.BigInteger)
    name = db.Column(db.String)
    description = db.Column(db.String)
    parameter = db.Column(db.Text)
    server_room_id = db.Column(db.Integer)
    monitor_machine = db.Column(db.String)
    is_parametric = db.Column(db.Integer)
    create_time = db.Column(db.TIMESTAMP, server_default=func.now())
    update_time = db.Column(db.TIMESTAMP, server_default=func.now())

    def __init__(self):
        pass
        # self.prd_id = prd_id
        # self.name = name
        # self.description = description
        # self.parameter = parameter
        # self.ip = ip
        # self.create_time = create_time
        # self.update_time = update_time
        # self.url = url
         
    def __repr__(self):
        pass
        # return '<Scripts %r(%r): %r>' % (self.prd_id, self.name, self.description)
