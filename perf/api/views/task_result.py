# -*- coding: utf-8 -*-
"""
    blueprints of tasklist
    ~~~~~~~~~~~~~~~~~~~~
    author: zuofeng(zuofeng@lianjia.com)
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
import traceback
import json
import commands
from flask import jsonify, Blueprint, request, current_app
from ..utils.log import logger
from ..models.task_result import TaskResult

task_result = Blueprint('task_result', __name__, url_prefix='/api')


@task_result.route('/get-task-result', methods=['POST'])
def get_task_result():
    """
    获取指定task_id的执行结果
    # :param {task_id: []}
    :param task_id:
    :return:
    """
    data = request.get_json()
    logger.info(data)

    t_task_id = data["task_id"]
    data["task_id"] = [t_task_id, t_task_id-1]
    res_data = []
    for task_id in data['task_id']:
        t_result = TaskResult.query.filter(TaskResult.task_id == task_id).first()
        if not t_result:
            tmp = {'task_id': task_id,
                   'msg': "未找到task_id=%s的任务" % task_id,
                   'jmeter_perf': "",
                   'monitor_machine_perf': ""
                }
        else:
            tmp = { 'task_id': task_id,
                    'jmeter_perf': {
                        'sample': t_result.sample,
                        'threads': t_result.threads,
                        'throughout': t_result.throughout_rate,
                        'avg': t_result.avg_time,
                        'min': t_result.min_time,
                        'max': t_result.max_time,
                        'error_rate': t_result.error_rate
                    },
                    'monitor_machine_perf': {
                        'cpu-busy': t_result.cpu_busy,
                        'cpu-system': t_result.cpu_system,
                        'cpu-user': t_result.cpu_user,
                        'cpu-idle': t_result.cpu_idle,
                        'load-1min': t_result.load_1min,
                        'load-5min': t_result.load_5min,
                        'mem-memused': t_result.mem_memused,
                        'mem-memused-percent': t_result.mem_persent,
                        'disk-io-read-bytes': t_result.disk_io_read_bytes,
                        'disk-io-write-bytes': t_result.disk_io_write_bytes,
                        'disk-io-util': t_result.disk_io_util,
                        'net-if-in-bytes': t_result.net_if_in_bytes,
                        'net-if-out-bytes': t_result.net_if_out_bytes
                    }
                 }
    	res_data.append(tmp)

    html_file = _get_result_html(t_task_id, res_data)

    return jsonify({'code': 1, 'msg': 'success', 'result_html_path': html_file, 'data': res_data})


def _get_result_html(task_id, data):
    """
    获取结果html文件
    :param data:
    :return:
    """
    app = current_app
    with app.app_context():
        local_result_path = app.config['LOCAL_RESULT_PATH']
    if not os.path.exists(local_result_path):
        os.makedirs(local_result_path)
    html_file = local_result_path + '/' + str(task_id) + '.html'
    html_str = _get_html_str(data)
    with open(html_file, "w") as f:
        f.write(html_str)

    status, ip = commands.getstatusoutput("hostname -i")
    html_file_path = 'ftp://' + ip + html_file
    return html_file_path


def _get_html_str(data):
    """
    获取html格式字符串
    :param data:
    :return:
    """
    jmeter_str = ""
    machine_str = ""
    for res in data:
        if not res['jmeter_perf']:
            continue
        tmp_jmeter_str = """
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
        """ % (res['task_id'], res['jmeter_perf']['sample'], res['jmeter_perf']['threads'],
               res['jmeter_perf']['throughout'], res['jmeter_perf']['avg'],
               res['jmeter_perf']['max'], res['jmeter_perf']['min'], res['jmeter_perf']['error_rate'])
        jmeter_str += tmp_jmeter_str

        m_perf = res['monitor_machine_perf']
        for k, v in m_perf.iteritems():
            if not v:
                m_perf[k] = {"avg": "", "max": "", "min": ""}
            else:
                m_perf[k] = json.loads(v)

        tmp_machine_str = """
            <tr>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>

                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
        """ % (res['task_id'],
               m_perf['cpu-busy']['avg'], m_perf['cpu-busy']['max'], m_perf['cpu-busy']['min'],
               m_perf['cpu-idle']['avg'], m_perf['cpu-idle']['max'], m_perf['cpu-idle']['min'],
               m_perf['cpu-system']['avg'], m_perf['cpu-system']['max'], m_perf['cpu-system']['min'],
               m_perf['cpu-user']['avg'], m_perf['cpu-user']['max'], m_perf['cpu-user']['min'],
               m_perf['mem-memused']['avg'], m_perf['mem-memused']['max'], m_perf['mem-memused']['min'],
               m_perf['mem-memused-percent']['avg'], m_perf['mem-memused-percent']['max'], m_perf['mem-memused-percent']['min'],
               m_perf['load-1min']['avg'], m_perf['load-1min']['max'], m_perf['load-1min']['min'],
               m_perf['load-5min']['avg'], m_perf['load-5min']['max'], m_perf['load-5min']['min'],
               m_perf['disk-io-read-bytes']['avg'], m_perf['disk-io-read-bytes']['max'], m_perf['disk-io-read-bytes']['min'],
               m_perf['disk-io-write-bytes']['avg'], m_perf['disk-io-write-bytes']['max'], m_perf['disk-io-write-bytes']['min'],
               m_perf['disk-io-util']['avg'], m_perf['disk-io-util']['max'], m_perf['disk-io-util']['min'],
               m_perf['net-if-in-bytes']['avg'], m_perf['net-if-in-bytes']['max'], m_perf['net-if-in-bytes']['min'],
               m_perf['net-if-out-bytes']['avg'], m_perf['net-if-out-bytes']['max'], m_perf['net-if-out-bytes']['min']
               )
        machine_str += tmp_machine_str

    html_str = """
        <html>
            <table border="1">jmeter性能参数
            <!-- <table width="500" border="1"cellspacing="1"> -->
                <thead>
                    <tr>
                        <th rowspan="2">task_id</th>
                        <th rowspan="2">sample</th>
                        <th rowspan="2">threads</th>
                        <th rowspan="2">throughout</td>
                        <th rowspan="2">avg</td>
                        <th rowspan="2">max</td>
                        <th rowspan="2">min</td>
                        <th rowspan="2">error_rate</td>
                    </tr>
                </thead>
                <tbody>
                    %s
                </tbody>
            </table>
            <hr>
            <hr>
            <table border="1">被压机器性能参数
                <thead>
                    <tr>
                        <th rowspan="2">task_id</th>
                        <th colspan="3">cpu-busy</td>
                        <th colspan="3">cpu-idle</td>
                        <th colspan="3">cpu-system</td>
                        <th colspan="3">cpu-user</td>
                        <th colspan="3">mem-memused</td>
                        <th colspan="3">mem-memused-percent</td>
                        <th colspan="3">load-1min</td>
                        <th colspan="3">load-5min</td>
                        <th colspan="3">disk-io-read-bytes</td>
                        <th colspan="3">disk-io-write-bytes</td>
                        <th colspan="3">disk-io-util</td>
                        <th colspan="3">net-if-in-bytes</td>
                        <th colspan="3">net-if-out-bytes</td>
                    </tr>
                    <tr>
                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>

                        <th>avg</th>
                        <td>max</td>
                        <td>min</td>
                    </tr>
                </thead>
                <tbody>
                    %s
                </tbody>
            </table>
        </html>
    """ % (jmeter_str, machine_str)

    return html_str

@task_result.errorhandler(Exception)
def error_handle(error):
    logger.error(traceback.format_exc())
    return jsonify({
        'code': 10000,
        'msg': str(error),
        'data': {}})

