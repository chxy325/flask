#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    figure generation
    ~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt

from parser import parse_jmeter
from falcon import falcon_request

matplotlib.use('Agg')

_util_path = os.path.dirname(os.path.realpath(__file__))
_static_path = os.path.join(os.path.dirname(_util_path), 'static/img/')

_jmeters = {'min': 'minimum response time (ms)',
            'max': 'maximum response time (ms)',
            'avg': 'average response time (ms)',
            'sample': 'sample number',
            'throughput': 'throughput (req/s)',
            'error': 'error percentage (%)'}

_servers = {'cpu.idle': 'cpu idle',
            'cpu.user': 'cpu user',
            'cpu.system': 'cpu system',
            'mem.memused.percent': 'mem.memused.percent (%)',
            'mem.swapused.percent': 'mem.swapused.percent (%)',
            'disk.io.util/device=sda': 'disk.io.util',
            'disk.io.avgrq_sz/device=sda': 'disk.io.avgrq_sz',
            'disk.io.avgqu-sz/device=sda': 'disk.io.avgqu-sz',
            'disk.io.await/device=sda': 'disk.io.await',
            'disk.io.read_bytes/device=sda': 'disk.io.read_bytes',
            'disk.io.write_bytes/device=sda': 'disk.io.write_bytes',
            'net.if.in.bytes/iface=eth0': 'net.if.in.bytes',
            'net.if.out.bytes/iface=eth0': 'net.if.out.bytes',
            'net.if.total.bytes/iface=eth0': 'net.if.total.bytes'}


def generate_jmeter(task_id):
    """
    generate jmeter test figures
    """

    raw = parse_jmeter()

    time_series = [int(item.get('time')) for item in raw]
    start = min(time_series)
    end = max(time_series)
    for metric, title in _jmeters.iteritems():
        data_series = [float(item.get(metric)) for item in raw]

        plt.plot(time_series, data_series, 'bo-')
        plt.xlabel('time')
        plt.xticks([start, end],
                   [datetime.fromtimestamp(int(start)).strftime('%H:%M:%S'),
                    datetime.fromtimestamp(int(end)).strftime('%H:%M:%S')])
        plt.title(title)
        plt.grid(True)

        plt.savefig(_static_path + metric + '.png.' + task_id,
                    format='png',
                    bbox_inches='tight')
        plt.clf()


def generate_server(node, start, end, task_id):
    """
    generate server metric figures
    @node: server hostname
    """

    start = start.strftime('%s')
    end = end.strftime('%s')

    for metric, title in _servers.iteritems():
        raw = falcon_request(node, metric, start, end)
        pre_series = raw['series'][0]['data']
        time_series = [l[0] / 1000 for l in pre_series]
        data_series = [float(l[1] or 0) for l in pre_series]

        plt.plot(time_series, data_series, 'go-')
        plt.xlabel('time')
        plt.xticks([start, end],
                   [datetime.fromtimestamp(int(start)).strftime('%H:%M:%S'),
                    datetime.fromtimestamp(int(end)).strftime('%H:%M:%S')])
        plt.title(title)
        plt.grid(True)

        plt.savefig(_static_path + metric.split('/')[0] + '.png.' + task_id,
                    format='png',
                    bbox_inches='tight')
        plt.clf()
