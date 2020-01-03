# -*- coding: utf-8 -*-
"""
    数据库联表查询
    ~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
    :author: chenxiaoyang(chenxiaoyang@lianjia.com)
"""

from db import db
from jmeter import Jmeter
from script import Script
from machine import Machine
from task import Task
from product import Product 

def query_task_info_by_task_id(task_id):
    '''
    根据task_id查询task 、 script、machine信息
    '''
    res = db.session.query( Jmeter.jmeter_report_path,
                            Task, Task.jmeter_report,
                            Machine.ip,
                            Machine.machine_user,
                            Machine.machine_passwd)\
                        .join(Machine, Jmeter.machine_ip == Machine.ip)\
                        .join(Scripts, Machine.ip == Scripts.ip)\
                        .join(Task, Scripts.id == Task.scr_id)\
                        .filter(Task.id == task_id).first()
    return res

def query_script_info_by_script_id(script_id):
    ''' 
    根据script_id查询script、machine、jmeter信息
    '''
    res = db.session.query(Machine.ip,
			   Machine.machine_user,
			   Machine.machine_passwd, 
			   Jmeter.jmeter_case_path)\
                        .join(Scripts, Machine.ip == Scripts.ip)\
                        .join(Jmeter, Jmeter.machine_ip == Scripts.ip)\
                        .filter(Scripts.id == script_id).first()
    return res
