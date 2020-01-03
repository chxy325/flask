# -*- coding: utf-8 -*-
"""
    products mapper
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: limingli(limingli@lianjia.com)
"""

from db import db


class TaskResult(db.Model):
    __tablename__ = 'task_result'
    id = db.Column(db.BigInteger, primary_key=True)
    task_id = db.Column(db.Integer)
    sample = db.Column(db.Integer)
    threads = db.Column(db.Integer)
    throughout_rate = db.Column(db.Float)
    avg_time = db.Column(db.Float)
    min_time = db.Column(db.Float)
    max_time = db.Column(db.Float)
    error_rate = db.Column(db.String)
    cpu_busy = db.Column(db.String)
    cpu_system = db.Column(db.String)
    cpu_user = db.Column(db.String)
    cpu_idle = db.Column(db.String)
    load_1min = db.Column(db.String)
    load_5min = db.Column(db.String)
    mem_memused = db.Column(db.String)
    mem_persent = db.Column(db.String)
    disk_io_read_bytes = db.Column(db.String)
    disk_io_write_bytes = db.Column(db.String)
    disk_io_util = db.Column(db.String)
    net_if_in_bytes = db.Column(db.String)
    net_if_out_bytes = db.Column(db.String)

    def __init__(self):
        pass
