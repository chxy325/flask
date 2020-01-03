#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    application file
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
from datetime import datetime

from flask import Flask, request, jsonify, url_for
from flask_bootstrap import Bootstrap
from weasyprint import HTML

from bs4 import BeautifulSoup

from views import (jmeter, server, monitor, products,
                   tasklist, script, upload, script_excute)
from configs import config
from extensions import socket_io
from utils.exception import errors
from utils.postman import send_mail
from utils.factory import create_celery
from utils.plotter import generate_jmeter, generate_server
from models.db import db
from models.task import Task
from models.script import Script
from models.machine import Machine


def create_app(config_name='default'):
    """
    application factory
    """
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))

    # init database
    from models.db import db
    db.init_app(app)

    # init socketio
    socket_io.init_app(app)

    # init flask-bootstrap
    Bootstrap(app)

    # register blueprints
    app.register_blueprint(jmeter.jmeter)
    app.register_blueprint(server.server)
    app.register_blueprint(monitor.monitor)
    app.register_blueprint(products.products)
    app.register_blueprint(tasklist.tasklist)
    app.register_blueprint(script.script)
    app.register_blueprint(upload.upload)
    app.register_blueprint(script_excute.script_excute)

    return app


# init application instance
conf_name = 'default'
app = create_app(conf_name)
conf = config.get(conf_name)

# init celery instance
celery = create_celery(app)


@celery.task
def send_report(task_id, email):
    """
    async task to render and email jmeter test report
    """

    # generate jmeter metric figures
    generate_jmeter(task_id)

    # generate server metric figures
    _, desc, ip, start, end = Script.query.join(
        Task,
        Script.id == Task.scr_id).add_columns(
            Script.description,
            Script.ip,
            Task.start_time,
            Task.end_time).filter(Task.id == int(task_id)).all()[0]

    machine = Machine.query.filter(Machine.ip == ip).one()
    generate_server(machine.hostname, start, end, str(task_id))

    # parse and update template
    start = datetime.strftime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strftime(end, '%Y-%m-%d %H:%M:%S')
    _path = os.path.dirname(os.path.realpath(__file__)) + '/'
    _replacements = [u'project: ' + desc,
                     'server: ' + ip,
                     'duration: ' + start + ' to ' + end]
    with open(_path + 'templates/report_task.html', 'r+') as f:
        soup = BeautifulSoup(f, 'lxml')
        for r, s in zip(_replacements, soup.find_all('button')):
            s.string = r

        for img in soup.find_all('img'):
            img['src'] = img['src'] + '.' + task_id

        html = soup.prettify('utf-8')

    # generate pdf report
    HTML(string=html,
         base_url='http://0.0.0.0:' + str(conf.SERVER_PORT),
         encoding='utf-8').write_pdf(
        _path + 'data/report.pdf.' + task_id)

    # send report by email
    send_mail(email, task_id)


@app.route('/api/task', methods=['POST'])
def render_report():
    """
    start async task to render test report
    """

    if request.method == 'POST':
        data = request.get_json()
        task_id = data['taskid']
        email = data['email'].split('@')[0]

        async_task = send_report.delay(str(task_id), email + '@lianjia.com')

        task = Task.query.filter(Task.id == task_id).one()
        task.async_task_id = async_task.id
        db.session.commit()

    return jsonify({'code': 1, 'msg': ''}),\
        202,\
        {'Location': url_for('render_task_status', aync_task_id=async_task.id)}


@app.route('/api/status/<string:aync_task_id>')
def render_task_status(aync_task_id):
    """
    return async task status
    """
    res = send_report.AsyncResult(aync_task_id)
    status = res.state

    if status == 'SUCCESS':
        code = 1
    elif status == 'PENDING':
        code = 0
    else:
        code = 10004

    response = {'code': code,
                'msg': errors[10004].format(aync_task_id)
                if res.failed() else ''}
    return jsonify(response)


@app.after_request
def add_response_header(response):
    """
    process response
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=conf.SERVER_PORT)
    # socket_io.run(app, host='0.0.0.0', port=conf.SERVER_PORT)
