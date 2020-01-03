# -*- coding: utf-8 -*-
"""
    jmeter log file parser
    ~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
import re
from datetime import datetime

_pattern = re.compile(r"""
                     (?P<time>\d+?/\d+?/\d+\s\d+?:\d+?:\d+) # time
                     .+?=(?P<sample>[\s\d]+)                # sample number
                     .+?=(?P<throughput>[\s\d\.]+)          # throughput
                     .+?Avg:(?P<avg>[\s\d]+)                # average response
                     Min:(?P<min>[\s\d]+)                   # min response
                     Max:(?P<max>[\s\d]+)                   # max response
                     Err:.+?\((?P<error>[\s\d\.\%]+)            # error percent
                     """, re.VERBOSE)

_pattern_thread = re.compile(r"""
                            .+?StandardJMeterEngine
                            .+?Starting(?P<threads>[\s\d]+)      # 并发线程数
                            .+?threads
                            """, re.VERBOSE)

# _util_path = os.path.dirname(os.path.realpath(__file__))
# _log_path = os.path.join(os.path.dirname(_util_path), 'data/jmeter.log')


def parse_jmeter(log_path):
    """
    parse jmeter.log
    """

    with open(log_path) as f:
        ret = []
        for line in f:
            m = _pattern.match(line)
            if m:
                d = m.groupdict()
                d['time'] = datetime.strptime(d['time'],
                                              '%Y/%m/%d %H:%M:%S'
                                              ).strftime('%s')

                for k, v in d.iteritems():
                    d[k] = v.strip()
                ret.append(d)

    return ret


def parse_jmeter_list(log_list):
    """
    parse jmeter.log
    """

    ret = []
    for line in log_list:
        m = _pattern.match(line)
        if m:
            d = m.groupdict()
            d['time'] = datetime.strptime(d['time'],
                                          '%Y/%m/%d %H:%M:%S'
                                          ).strftime('%s')

            for k, v in d.iteritems():
                d[k] = v.strip()
            ret.append(d)

    return ret


def parse_jmeter_result(log_list):
    """
    parse jmeter.log
    """

    ret = {}
    for line in log_list:
        m = _pattern.match(line)
        t = _pattern_thread.match(line)
        if m:
            d = m.groupdict()
            for k, v in d.iteritems():
                ret[k] = v.strip()
        if t:
            d = t.groupdict()
            for k, v in d.iteritems():
                ret[k] = v.strip()
    return ret
