# -*- coding: utf-8 -*-
"""
    task mapper
    ~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: chenxiaoyang(chenxiaoyang@lianjia.com)
"""

from db import db
from sqlalchemy.sql import func
from .jmeter import Jmeter
from .product import Product
from .script import Script


class Task(db.Model):
    """
    Task table
    """
    __tablename__ = 'task'

    id = db.Column(db.BigInteger, primary_key=True)
    scr_id = db.Column(db.BigInteger)
    press_machine = db.Column(db.String)
    status = db.Column(db.Integer)
    execute_time = db.Column(db.TIMESTAMP, server_default=func.now())
    start_time = db.Column(db.TIMESTAMP)
    end_time = db.Column(db.TIMESTAMP)
    jenkens_job_name = db.Column(db.String)
    build_id = db.Column(db.Integer)
    async_task_id = db.Column(db.String)
    jmeter_report = db.Column(db.String)

    @classmethod
    def get_slave_info(cls, task_id):
        task_info = db.session.query(Jmeter.machine_ip,
                                     Jmeter.machine_user,
                                     Jmeter.machine_passwd,
                                     Jmeter.jmeter_report_path,
                                     Task.jmeter_report)\
            .join(Task, Task.press_machine == Jmeter.machine_ip)\
            .filter(Task.id == task_id).first()
        return task_info

    @classmethod
    def get_task_info(cls, product_id):
        """
        根据product_id获取任务信息
        :param product_id:
        :return:
        """
        result = db.session.query(Product.name.label("product_name"),
                                  Product.id.label("product_id"),
                                  Task.id.label("task_id"),
                                  Task.scr_id,
                                  Task.status,
                                  Task.start_time,
                                  Task.end_time,
                                  Task.build_id,
                                  Task.press_machine,
                                  Script.name.label("script_name"),
                                  Script.description,
                                  Script.monitor_machine,
                                  Jmeter.jenkins_job_name,
                                  Jmeter.jmeter_report_path)\
            .join(Script, Script.prd_id == product_id)\
            .join(Task, Task.scr_id == Script.id)\
            .join(Jmeter, Jmeter.machine_ip == Task.press_machine)\
            .filter(Product.id == product_id).all()

        return result
