# -*- coding: utf-8 -*-
"""
    send email
    ~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
import json
import requests


_url = 'http://sms.lianjia.com/lianjia/sms/send'
_version = '1.0'
_method = 'mail.sent'
_group = 'qaproject'
_auth = 'HtmjpQNNOkb2qYfEMUx1vu4ovA5kV6OC'
_sendtype = 'single'
_body = 'Attached is your JMeter Test Report.'

_util_path = os.path.dirname(os.path.realpath(__file__))
_report = os.path.join(os.path.dirname(_util_path), 'data/report.pdf')


def send_mail(recipient, task_id, subject='JMeter Test Report'):
    """
    send async email with report as attachment
    """

    report = _report + '.' + task_id
    with open(report, 'r') as f:
        attach = f.read().encode('base64')

    data = {'version': _version,
            'method': _method,
            'group': _group,
            'auth': _auth,
            'params': {'to': [recipient],
                       'subject': subject,
                       'sendtype': _sendtype,
                       'body': _body,
                       'attachbody': {'report.pdf': attach}
                       }
            }

    jdata = json.dumps(data)
    resp = requests.post(_url, data=jdata)

    return resp.status_code
