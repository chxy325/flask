# -*- coding: utf-8 -*-
"""
    xml manager
    ~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import json
import time
from collections import OrderedDict
from ..models.db import db
from ..models.task_result import TaskResult
from ..models.machine import Machine
from .ftp_process import HandleRemoteFile
from .falcon import falcon_request
from .log import logger
import parser


class SaveTaskResult(object):

    def __init__(self):
        pass

    def save_task_result(self, app, task_id, monitor_machine, start_time, end_time):
        remote_file = HandleRemoteFile.get_remote_log(task_id, app=app)
        log_list = remote_file.split('\n')
        result_jmeter = parser.parse_jmeter_result(log_list)
        logger.debug(result_jmeter)

	with app.app_context():
            taskResult = TaskResult()
        taskResult.task_id = task_id
        taskResult.sample = result_jmeter['sample']
        taskResult.threads = result_jmeter['threads']
        taskResult.throughout_rate = result_jmeter['throughput']
        taskResult.avg_time = result_jmeter['avg']
        taskResult.min_time = result_jmeter['min']
        taskResult.max_time = result_jmeter['max']
        taskResult.error_rate = result_jmeter['error']

        # 获取machine perf
        metric_list = ["cpu.busy", "cpu.system", "cpu.user", "cpu.idle", "load.1min", "load.5min", "mem.memused",
                       "mem.memused.percent", "disk.io.read.bytes", "disk.io.write.bytes", "disk.io.util", "net.if.in.bytes",
                       "net.if.out.bytes"]

        for metric in metric_list:
            machine_result = {}
            data = self._get_machine_perf(monitor_machine, metric, int(start_time)-10, int(end_time)+10, app=app)
            logger.debug(data)
	    if data == None:
		continue
            tmp_list = []
            for k, v in data.items():
                tmp_list.append(v)
	    logger.debug(tmp_list)
	    if tmp_list == []:
		continue
            tmp_list.sort()
            machine_result['min'] = tmp_list[0]
            machine_result['max'] = tmp_list[-1]
            machine_result['avg'] = round(sum(tmp_list)/len(tmp_list), 2)
	    machine_result = json.dumps(machine_result)
            if metric == "cpu.busy":
                taskResult.cpu_busy = machine_result
            elif metric == "cpu.system":
                taskResult.cpu_system = machine_result
            elif metric == "cpu.user":
                taskResult.cpu_user = machine_result
            elif metric == "cpu.idle":
                taskResult.cpu_idle = machine_result
            elif metric == "load.1min":
                taskResult.load_1min = machine_result
            elif metric == "load.5min":
                taskResult.load_5min = machine_result
            elif metric == "mem.memused":
                taskResult.mem_memused = machine_result
            elif metric == "mem.memused.percent":
                taskResult.mem_persent = machine_result
            elif metric == "disk.io.read.bytes":
                taskResult.disk_io_read_bytes = machine_result
            elif metric == "disk.io.write.bytes":
                taskResult.disk_io_write_bytes = machine_result
            elif metric == "disk.io.util":
                taskResult.disk_io_util = machine_result
            elif metric == "net.if.in.bytes":
                taskResult.net_if_in_bytes = machine_result
            elif metric == "net.if.out.bytes":
                taskResult.net_if_out_bytes = machine_result

        with app.app_context():
            db.session.add(taskResult)
            db.session.commit()

    def _get_machine_perf(self, node, metric, start, end, app=None):
        end = str(int(end) + 60)

	if not app:
            machine = Machine.query.filter(Machine.ip == node).first()
	else:
	    with app.app_context():
		machine = Machine.query.filter(Machine.ip == node).first()
        # add additional device name for disk and net metrics
        if metric.startswith('disk'):
            metric += '/device={}'.format(machine.disk_name)
        elif metric.startswith('net'):
            metric += '/iface={}'.format(machine.network_card_name)

        # obtain corresponding hostname
	try:
            resp = falcon_request(machine.hostname, metric, start, end)
            pre_series = resp['series'][0]['data']
	except Exception, e:
	    logger.error(str(e))
            pre_series = None
	
	if pre_series is not None:
            if metric == "mem.memused":
                processed = [[p[0] / 1000, round(p[1] / (1024 ** 3), 2)] for p in pre_series if p[1] is not None]
            elif metric.startswith("disk.io.read_bytes") or metric.startswith("disk.io.write_bytes") \
                    or metric.startswith("net.if.in.bytes") or metric.startswith("net.if.out.bytes"):
                processed = [[p[0] / 1000, round(p[1] / 1024, 2)] for p in pre_series if p[1] is not None]
            else:
                processed = [[p[0] / 1000, round(p[1], 2)] for p in pre_series if p[1] is not None]
            data = OrderedDict(processed)
	else:
	    data = None

        return data
