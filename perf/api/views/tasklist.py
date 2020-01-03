# -*- coding: utf-8 -*-
"""
    blueprints of tasklist
    ~~~~~~~~~~~~~~~~~~~~
    author: zuofeng(zuofeng@lianjia.com)
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import traceback
import time
import datetime
import threading
from flask import jsonify, Blueprint, current_app
from ..utils.log import logger
from ..utils.jenkins_util import JenkinsUtil
from ..utils.save_task_result import SaveTaskResult
from ..models.db import db
from ..models.task import Task
from ..models.product import Product
from ..models.jmeter import Jmeter


tasklist = Blueprint('tasklist', __name__, url_prefix='/api/task')


@tasklist.route('/list/<int:product_id>', methods=['GET'])
def get_task_list(product_id):
    """
    按产品线获取任务列表
    :param product_id:
    :return:
    """
    # 更新所有任务状态
    _update_task_status()

    product = Product.query.filter(Product.id == product_id).all()

    if not product:
        return jsonify({"code": 1,
                        "msg": "success",
                        "data": {"total": 0, "list": []}
                        })

    task_info = Task.get_task_info(product_id)
    data = []
    for r in task_info:
        tmp_data = {"productId": r.product_id,
                    "productName": r.product_name,
                    "taskId": r.task_id,
                    "status": r.status,
                    "startTime": r.start_time.strftime("%Y-%m-%d %H:%M:%S") if r.start_time is not None else None,
                    "endTime": r.end_time.strftime("%Y-%m-%d %H:%M:%S") if r.end_time is not None else None,
                    "pressMachine": r.press_machine,
                    "monitorMachine": r.monitor_machine,
                    "scriptId": r.scr_id,
                    "scriptName": r.script_name,
                    "scriptDesc": r.description,
                    "jenkinsJobName": r.jenkins_job_name,
                    "jenkinsBuildId": r.build_id,
                    "jmeterReportPath": r.jmeter_report_path
                    }
        data.append(tmp_data)

    return jsonify({"code": 1,
                    "msg": "success",
                    "data": {"total": len(data),
                             "list": data
                             }
                    })
    

def _update_task_status():
    """
    获取进行中的构建, 查看是否完成，若完成，则把状态置为2，且返回构建完成时间
    :return:
    """
    jenkins_server = JenkinsUtil.connect_jenkins()
    task = Task.query.filter(Task.status == 1).all()

    for t in task:
        jmeter_info = Jmeter.query.filter(Jmeter.machine_ip == t.press_machine).first()
        logger.info(jmeter_info)
        job_name = jmeter_info.jenkins_job_name

        try:
            status = jenkins_server.get_build_info(job_name, t.build_id)['result']
        except Exception, e:
            logger.info("get jenkins status error: %s" % str(e))

            now = datetime.datetime.now()
            execute_time = t.execute_time
            if (now - execute_time).seconds > 300:
                db.session.query(Task).filter(t.build_id == Task.build_id) \
                    .update({Task.status: 0})
                db.session.commit()
            continue

        if status == "SUCCESS":
            start = jenkins_server.get_build_info(job_name, t.build_id)['timestamp']
            duration = jenkins_server.get_build_info(job_name, t.build_id)['duration']
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start / 1000))
            end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((start + duration) / 1000))
            # t_task = Task.query.filter(Task.id == t.id).first()
            # t_task.status = 2
            # t_task.end_time = end
            db.session.query(Task).filter(t.build_id == Task.build_id)\
                .update({Task.status: 2,
                         Task.start_time: start_time,
                         Task.end_time: end_time})
            db.session.commit()

            # 保存执行结果
            app = current_app._get_current_object()
            save_t_res = SaveTaskResult()
            th = threading.Thread(target=save_t_res.save_task_result, args=(app, t.id, t.press_machine, start/1000, (start + duration)/1000))
            th.start()

            # save_t_res.save_task_result(t.id, t.press_machine, start/1000, (start + duration)/1000)

        elif status == "FAILURE":
	    logger.info("from tasklist: jenkins job failure")
            db.session.query(Task).filter(t.build_id == Task.build_id)\
                .update({Task.status: 0})
            db.session.commit()
        elif status == "ABORTED":
	    logger.info("from tasklist: jenkins job aborted")
            db.session.query(Task).filter(t.build_id == Task.build_id)\
                .update({Task.status: 0})
            db.session.commit()
        else:
            start = jenkins_server.get_build_info(job_name, t.build_id)['timestamp']
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start / 1000))
            db.session.query(Task).filter(t.build_id == Task.build_id)\
                .update({Task.start_time: start_time})
            db.session.commit()


@tasklist.errorhandler(Exception)
def errorhandle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})

