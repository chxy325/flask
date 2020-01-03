# -*- coding: utf-8 -*-
"""
    logger factory
    ~~~~~~~~~~~~~~
    logging configuration
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler


# use flask logger instance
logger = logging.getLogger('gunicorn.access')

# define file log location
# util_path = os.path.dirname(os.path.realpath(__file__))  # /api/utils
# logs_path = os.path.join(os.path.dirname(util_path), 'logs')
logs_path = os.path.join(os.environ['HOME'], 'var/perf_platform/logs')
if not os.path.exists(logs_path):
    os.makedirs(logs_path)

log_file = os.path.join(logs_path, 'perf.log')

# file handle
file_handler = TimedRotatingFileHandler(
    filename=log_file, when="midnight", interval=1, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s][%(name)s][%(pathname)s:%(lineno)d] ' +
    '%(message)s', '%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
