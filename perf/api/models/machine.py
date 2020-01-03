# -*- coding: utf-8 -*-
"""
    machine mapper
    ~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: dushu(dushu@lianjia.com)
"""

from db import db
from sqlalchemy import and_


class Machine(db.Model):
    """
    监控服务器列表
    """
    __tablename__ = 'machine'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String)
    hostname = db.Column(db.String)
    network_card_name = db.Column(db.String)
    disk_name = db.Column(db.String)
    other = db.Column(db.String)
    status = db.Column(db.Integer)

    def __init__(self, ip, hostname, network_card_name, disk_name, other):
        self.ip = ip
        self.hostname = hostname
        self.network_card_name = network_card_name
        self.disk_name = disk_name
        self.other = other
	self.status = 1

    def __repr__(self):
        return '<Machine %r(%r): %r>' % (self.ip, self.hostname, self.other)

    @classmethod
    def get_valid_machine_by_ip(cls, ip):
        return Machine.query.filter(and_(Machine.ip == ip, Machine.status == 1)).all()
