# -*- coding: utf-8 -*-

"""
    blueprints of scripts
    ~~~~~~~~~~~~~~~~~~~~~
    :author: limingli(limingli@lianjia.com)
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""
import traceback
import time
from flask import Blueprint, jsonify
from ..utils.exception import errors, InvalidUsage
from ..utils.log import logger
from ..utils.jenkins_util import JenkinsUtil
from ..models.db import db
from ..models.script import Script
from ..models.task import Task
from ..models.product import Product
from ..models.jmeter import Jmeter
from ..models.server_room import ServerRoom

script_excute = Blueprint('script_excute', __name__, url_prefix='/api/script')


@script_excute.route('/execute/<int:script_id>', methods=['GET'])
def execute_script(script_id):
    """
    带脚本参数执行jekins
    """
    jenkins_server = JenkinsUtil.connect_jenkins()

    script = Script.query.filter(Script.id == script_id).first()
    # jmeter_slaves = Jmeter.query.filter(and_(Jmeter.server_room_id == script.server_room_id, Jmeter.status == 1).all()
    jmeter_slaves = Jmeter.query.filter(Jmeter.server_room_id == script.server_room_id).filter(Jmeter.status == 1).all()

    # 多slave选择
    for slave in jmeter_slaves:
        job_name = slave.jenkins_job_name

        job_info = jenkins_server.get_job_info(job_name)
        # 判断是否为第一次构建
        if job_info['firstBuild'] is None:
            build_id = 1
            task_id = _script_excute(job_name, script_id, build_id, script.name, jenkins_server, slave.machine_ip)
            data = {"task_id":task_id, "job_id": build_id}
            return jsonify({"code": 1, "msg": "success", "data":data})

        last_build_id = jenkins_server.get_job_info(job_name)['lastBuild']['number']
        last_build_result = jenkins_server.get_build_info(job_name, last_build_id)['building']
        if last_build_result:
            break

        build_id = int(last_build_id) + 1
        task_id = _script_excute(job_name, script_id, build_id, script.name, jenkins_server, slave.machine_ip)
        data = {"task_id":task_id, "job_id": build_id}
        return jsonify({"code": 1, "msg": "success", "data": data})

    raise InvalidUsage(10007, errors[10007])


@script_excute.route('/list/<int:product_id>', methods=['GET'])
def get_script_list(product_id):
    """
    获取脚本列表
    """
    product = Product.query.filter(Product.id == product_id).first()
    script = Script.query.filter(Script.prd_id == product_id).all()
    script_list = []
    for s in script:
        server_room = ServerRoom.query.filter(ServerRoom.id == s.server_room_id).first()
        script = {"productId": s.prd_id,
                  "productName": product.name,
                  "scriptId": s.id,
                  "scriptName": s.name,
                  "scriptDesc": s.description,
                  "serverRoomName": server_room.room_name,
                  "monitorMachine": s.monitor_machine,
                  "createTime": s.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                  "updateTime": s.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                  "base": s.parameter}
        script_list.append(script)

    res = {"code": 1,
           "msg": "sucess",
           "data": {"total": len(script_list),
                    "list": script_list
                    }
           }
    return jsonify(res)


def _script_excute(job_name, script_id, build_id, script_name, jenkins_server, press_machine):
    """
    执行脚本 写入task表 并返回task_id
    """
    # task表写入记录
    task = Task(scr_id=script_id,
                status=1,
		jenkens_job_name=job_name,
                build_id=build_id,
                press_machine=press_machine)
    db.session.add(task)
    db.session.commit()
    
    task_info = Task.query.filter(Task.build_id == build_id).filter(Task.jenkens_job_name == job_name).first()
    # query = db.session.query(Task)
    # query.filter(Task.build_id == build_id).update({Task.jmeter_report: jmeter_report})

    # 以脚本名字为参数，触发jekins参数构建  是不是参数只有脚本名字
    data_param = {"tag1": script_name, "tag2": task_info.id}
    jenkins_server.build_job(job_name, parameters=data_param)

    jmeter_report = str(task_info.id) + ".log"
    task_info.jmeter_report = jmeter_report
    db.session.add(task_info)
    db.session.commit()

    return task_info.id

@script_excute.errorhandler(InvalidUsage)
def invalidhandle(error):
    logger.error(traceback.format_exc())
    return jsonify(error.to_dict())


@script_excute.errorhandler(Exception)
def errorhandle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})

