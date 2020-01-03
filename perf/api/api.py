#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    application file
    ~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""
from flask import Flask
from flask_bootstrap import Bootstrap

from views import (jmeter, server, monitor, products,
                   tasklist, upload, script_excute, task_result)
from views import script
from configs import config
from extensions import socket_io
# from utils.exception import errors
# from utils.postman import send_mail
# from utils.factory import create_celery
# from utils.plotter import generate_jmeter, generate_server
from models.db import db
# from models.task import Task
# from models.script import Script
# from models.machine import Machine


def create_app(config_name='default'):
    """
    application factory
    """
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))

    # init database
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
    app.register_blueprint(task_result.task_result)

    return app
