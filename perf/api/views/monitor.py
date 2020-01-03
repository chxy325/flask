# -*- coding: utf-8 -*-
"""
    获取jmeter slave机器的jmeter执行日志，解析指标
    ~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""
import traceback
import datetime
import time
import threading

from flask import Blueprint, jsonify, current_app
# from flask_socketio import emit
# from extensions import socket_io
from ..utils.log import logger
from ..utils.ftp_process import HandleRemoteFile
from ..utils import parser
from ..utils.jenkins_util import JenkinsUtil
from ..utils.save_task_result import SaveTaskResult
from ..models.task import Task
from ..models.db import db
from ..models.jmeter import Jmeter


monitor = Blueprint('monitor', __name__, url_prefix='/api/monitor')


@monitor.route('/get_state/<int:task_id>', methods=['GET'])
def get_state(task_id):
    """
    @description: 监听器-获取开始时间 结束时间 运行状态
    @param: task_id
    """
    tmp_data = {"startTime": None,
                "endTime": None,
                "duration": None,
                "state": 0
                }

    task = Task.query.filter(Task.id == task_id).first()

    if not HandleRemoteFile.is_log_exist(task_id) and task.status == 2:
        task.status = 0
        db.session.add(task)
        db.session.commit()
        raise Exception("task_id = %s 的任务未获取到日志" % task_id)

    jenkins_server = JenkinsUtil.connect_jenkins()
    if task.start_time is None or task.end_time is None:
        jmeter_info = Jmeter.query.filter(Jmeter.machine_ip == task.press_machine).first()
        job_name = jmeter_info.jenkins_job_name

        flag = True
	for i in range(10):
            try:
                status = jenkins_server.get_build_info(job_name, task.build_id)['result']
		break
            except Exception, e:
	        logger.info("get jenkins status try %d" % (i+1))

	    if i == 9:
		logger.info("get jenkins status error: %s" % str(e))
                flag = False
                now = datetime.datetime.now()
                execute_time = task.execute_time
                if (now - execute_time).seconds > 300:
                    db.session.query(Task).filter(task.build_id == Task.build_id) \
                        .update({Task.status: 0})
                    db.session.commit()


	logger.info(flag)
        if flag:
            if status == "SUCCESS":
                start = jenkins_server.get_build_info(job_name, task.build_id)['timestamp']
                duration = jenkins_server.get_build_info(job_name, task.build_id)['duration']
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start / 1000))
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((start + duration) / 1000))
                db.session.query(Task).filter(task.build_id == Task.build_id)\
                    .update({Task.status: 2,
                             Task.start_time: start_time,
                             Task.end_time: end_time})
                db.session.commit()

                # 保存执行结果
		app = current_app._get_current_object()
                save_t_res = SaveTaskResult()
                th = threading.Thread(target=save_t_res.save_task_result, args=(app, task_id, task.press_machine, start/1000, (start + duration)/1000))
                th.start()

                # save_t_res.save_task_result(task_id, task.press_machine, start/1000, (start+duration)/1000)

            elif status == "FAILURE":
		logger.info("jenkins job failure")
                db.session.query(Task).filter(task.build_id == Task.build_id)\
                    .update({Task.status: 0})
                db.session.commit()
            else:
                start = jenkins_server.get_build_info(job_name, task.build_id)['timestamp']
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start / 1000))
                db.session.query(Task).filter(task.build_id == Task.build_id)\
                    .update({Task.start_time: start_time})
                db.session.commit()

    tmp_data['startTime'] = task.start_time.strftime("%Y-%m-%d %H:%M:%S") if task.start_time is not None else None
    tmp_data['endTime'] = task.end_time.strftime("%Y-%m-%d %H:%M:%S") if task.end_time is not None else None
    if task.end_time is not None:
        tmp_data['duration'] = str(task.end_time - task.start_time)

    tmp_data['state'] = task.status
    logger.info(tmp_data)

    res = {"code": 1, "msg": "success", "data": tmp_data}
    return jsonify(res)


@monitor.route('/get_perf_param/<int:task_id>', methods=['GET'])
def get_param(task_id):
    """
    @description: 监听器-根据jmeter日志，返回性能指标
    @param: task_id
    """
    remote_file = HandleRemoteFile.get_remote_log(task_id)
    log_list = remote_file.split('\n')
    result = parser.parse_jmeter_result(log_list)
    return jsonify({"code": 1, "msg": "success", "data": result})
        # for line in log_list[::-1]:
        #     if 'summary =' in line:
        #         param_list = line.split()
        #         logger.info(param_list)
        #         res['data'] = {
        #             "total_requests": param_list[7],
        #             "run_time": param_list[9],
        #             "qps": param_list[11],
        #             "avg": param_list[13],
        #             "min_time": param_list[15] + 'ms',
        #             "max_time": param_list[17] + 'ms',
        #             "err_num": param_list[19],
        #             "err_rate": param_list[20].replace("(", "").replace(")", "")
        #         }


@monitor.route('/get_jmeter_log/<int:task_id>', methods=['GET'])
def get_log(task_id):
    """
    @description: 监听器-返回jmeter日志
    @param: task_id
    """
    remote_log = HandleRemoteFile.get_remote_log(task_id)
    res = {"code": 1, "msg": 'success', "data": remote_log}
    return jsonify(res)


@monitor.errorhandler(Exception)
def errorhandle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})

