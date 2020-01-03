# -*- coding: utf-8 -*-
"""
    server_room mapper
    ~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: chenxiaoyang(chenxiaoyang@lianjia.com)
"""

from db import db


class ServerRoom(db.Model):
    """
    机房表
    """
    __tablename__ = 'server_room'

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), unique=True)
    desc = db.Column(db.String(100))

    def __init__(self):
        pass

    def __repr__(self):
        return '<Server Room info %r : %r>' % (self.id, self.room_name)


