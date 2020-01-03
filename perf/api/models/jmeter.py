# -*- coding: utf-8 -*-
"""
    machine mapper
    ~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: chenxiaoyang(chenxiaoyang@lianjia.com)
"""

from db import db


class Jmeter(db.Model):
    """
    jenkins_job table
    """
    __tablename__ = 'jmeter'

    id = db.Column(db.Integer, primary_key=True)
    machine_ip = db.Column(db.String)
    server_room_id = db.Column(db.Integer)
    machine_user = db.Column(db.String)
    machine_passwd = db.Column(db.String)
    jenkins_job_name = db.Column(db.String)
    jmeter_report_path = db.Column(db.String)
    jmeter_case_path = db.Column(db.String)
    status = db.Column(db.Integer)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Jenkins job info %r : %r>' % (self.machine_ip, self.jenkins_job_name)
