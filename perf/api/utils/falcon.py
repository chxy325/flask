# -*- coding: utf-8 -*-
"""
    falcon request
    ~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import requests

from ..utils.exception import errors, CustomRuntimeError
from ..utils.log import logger

# _op_host = 'http://monitor-dashboard.lianjia.com:18081'
_op_host = 'http://monitor-dashboard.lianjia.com'
_chart_url = _op_host + '/chart'
_series_url = _op_host + '/chart/h'
_headers = {'Content-Type': 'application/x-www-form-urlencoded'}


def falcon_request(node, metric, start, end):
    """
    query falcon monitor api with specific server and metric
    """
    # obtain chart id
    chart_params = 'endpoints[]={}&counters[]={}&graph_type=h'.format(
        node,
        metric
    )
    resp = requests.post(_chart_url, headers=_headers, data=chart_params)
    chart_id = resp.json().get('id')

    start = str(int(start) - 120)
    end = str(int(end) + 120)
    # obtain metric data with chart id
    series_params = {
        'id': chart_id,
        'start': start,
        'end': end,
        'cf': 'AVERAGE',
        'sum': 'off',
        'graph_type': 'h'
    }
    resp = requests.get(_series_url, params=series_params).json()
    if not resp['series']:
        raise CustomRuntimeError(10006, errors[10006])

    return resp
