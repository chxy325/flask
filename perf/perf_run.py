#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    perf run
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""
import os
from api import api

if os.environ['PERF_ENV'] == 'prod':
    app = api.create_app(config_name="prod")
elif os.environ['PERF_ENV'] == 'test':
    app = api.create_app(config_name="test")
else:
    app = api.create_app(config_name="dev")


@app.after_request
def add_response_header(response):
    """
    process response
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['SERVER_PORT'], threaded=True)
