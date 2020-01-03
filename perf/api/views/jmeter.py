# -*- coding: utf-8 -*-
"""
    blueprints of jmeter results
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import traceback
from collections import OrderedDict
from flask import Blueprint, request, jsonify
from ..utils.log import logger
from ..utils.exception import errors, InvalidUsage
from ..utils.parser import parse_jmeter_list
from ..utils.ftp_process import HandleRemoteFile

jmeter = Blueprint('jmeter', __name__, url_prefix='/api/jmeter')


@jmeter.route('/result')
def get_jmeter_result():
    """
    obtain certain jmeter result from jmeter log file
    """
    metric = request.args.get('metric', '')
    task_id = request.args.get('task_id', '')
    if not metric:
        raise InvalidUsage(10001, errors[10001].format(metric))

    remote_file = HandleRemoteFile.get_remote_log(task_id)
    log_list = remote_file.split('\n')
    raw = parse_jmeter_list(log_list)
    series = OrderedDict({r.get('time'): float(r.get(metric)) for r in raw})

    data = {'code': 1,
            'msg': '',
            'data': {'title': metric, 'series': series}}
    return jsonify(data)


@jmeter.errorhandler(InvalidUsage)
def invalidhandle(error):
    logger.error(traceback.format_exc())
    return jsonify(error.to_dict())


@jmeter.errorhandler(Exception)
def errorhandle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})
