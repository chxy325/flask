# -*- coding: utf-8 -*-
"""
    blueprints of server
    ~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import traceback
from datetime import datetime, timedelta
from collections import OrderedDict
from flask import Blueprint, request, jsonify

from ..utils.log import logger
from ..utils.falcon import falcon_request
from ..utils.exception import errors, InvalidUsage, CustomRuntimeError
from ..models.db import db
from ..models.machine import Machine
from ..models.server_room import ServerRoom


server = Blueprint('server', __name__, url_prefix='/api/server')


@server.route('/server-room/list', methods=['GET'])
def get_server_room_list():
    """
    获取机房列表
    """
    server_room = ServerRoom.query.all()

    data = [{'serverRoomId': s.id, 'serverRoomName': s.room_name} for s in server_room]

    return jsonify({'code': 1, 'msg': 'success', 'data': data})


@server.route('/list')
def get_server_list():
    """
    obtain server's info
    """

    ip = request.args.get('ip', '')
    if ip:
        machine = Machine.get_valid_machine_by_ip(ip)
    else:
        machine = Machine.query.filter(Machine.status == 1).all()

    data = [{'id': m.id,
             'ip': m.ip,
             'hostname': m.hostname,
             'network_card_name': m.network_card_name,
             'disk_name': m.disk_name,
             'other': m.other} for m in machine]

    return jsonify({'code': 1, 'msg': '', 'data': data})


@server.route('/add', methods=['POST'])
def add_server():
    """
    add a server to server list
    """

    if request.method == 'POST':
        data = request.get_json()

        if not Machine.query.filter(Machine.ip == data['ip']).first():
            machine = Machine(data['ip'],
                              data['hostname'],
                              data['network_card_name'],
                              data['disk_name'],
                              data.get('other', ''))
            db.session.add(machine)
            db.session.commit()
        else:
            raise InvalidUsage(10005, errors[10005])

    return jsonify({'code': 1, 'msg': '', 'data': {}})


@server.route('/metric')
def metric():
    """
    obtain server's metric
    监听op falcon服务器，获取对应机器性能指标
    """

    now = datetime.now()
    node = request.args.get('node', '10.33.107.24')
    metric = request.args.get('metric', 'cpu.busy')
    start = request.args.get('start',
                             (now + timedelta(minutes=-10)).strftime('%s'))
    end = request.args.get('end', now.strftime('%s'))

    if start >= end:
        raise InvalidUsage(10002, errors[10002])

    if start <= (datetime.now() + timedelta(days=-14)).strftime('%s'):
        raise InvalidUsage(10003, errors[10003].format(14))

    # falcon延迟特殊处理 放到falcon.py中
    # end = str(int(end) + 60)

    machine = Machine.query.filter(Machine.ip == node).first()
    # add additional device name for disk and net metrics
    if metric.startswith('disk'):
        metric += '/device={}'.format(machine.disk_name)
    elif metric.startswith('net'):
        metric += '/iface={}'.format(machine.network_card_name)

    logger.info(metric)
    # obtain corresponding hostname
    resp = falcon_request(machine.hostname, metric, start, end)

    pre_series = resp['series'][0]['data']
    if metric == "mem.memused":
        processed = [[p[0] / 1000, round(p[1]/(1024 ** 3), 2)] for p in pre_series if p[1] is not None]
    elif metric.startswith("disk.io.read_bytes") or metric.startswith("disk.io.write_bytes") \
            or metric.startswith("net.if.in.bytes") or metric.startswith("net.if.out.bytes"):
        processed = [[p[0] / 1000, round(p[1]/1024, 2)] for p in pre_series if p[1] is not None]
    else:
        processed = [[p[0] / 1000, round(p[1], 2)] for p in pre_series if p[1] is not None]

    data = OrderedDict(processed)

    res = {'code': 1,
           'msg': '',
           'data': {'endpoint': node,
                    'title': resp.get('title').split('/')[0],
                    'series': data}
           }

    return jsonify(res)


@server.errorhandler(InvalidUsage)
def invalidhandle(error):
    logger.error(traceback.format_exc())
    return jsonify(error.to_dict())


@server.errorhandler(CustomRuntimeError)
def runtimehandle(error):
    logger.error(traceback.format_exc())
    return jsonify(error.to_dict())


@server.errorhandler(Exception)
def errorhandle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})
