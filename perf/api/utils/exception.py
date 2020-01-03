# -*- coding: utf-8 -*-
"""
    exceptions
    ~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""


errors = {
    10001: 'parameter {} is required',
    10002: 'start time cannot be later than end time',
    10003: 'start time cannot be earlier than {} days from now',
    10004: 'async task (id={}) failed',
    10005: 'duplicate insertion',
    10006: 'OP falcon monitor returns empty data',
    10007: '没有空闲的jmeter slave机器，请稍后再试'
}


class InvalidUsage(Exception):

    def __init__(self, code, msg):
        Exception.__init__(self)

        self.code = code
        self.msg = msg

    def to_dict(self):
        rv = {'code': self.code, 'msg': self.msg}
        return rv


class CustomRuntimeError(Exception):

    def __init__(self, code, msg):
        Exception.__init__(self)

        self.code = code
        self.msg = msg

    def to_dict(self):
        rv = {'code': self.code, 'msg': self.msg}
        return rv
