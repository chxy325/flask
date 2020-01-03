# -*- coding: utf-8 -*-
"""
    config file
    ~~~~~~~~~~~
    Includes development and production configurations
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or ''

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BROKER_URL = 'redis://10.33.107.13:6379/10'
    CELERY_RESULT_BACKEND = 'redis://10.33.107.13:6379/11'

    @staticmethod
    def init_app(app):
        pass


class ProdConfig(Config):
    SERVER_PORT = 5002
    LOCAL_CASE_PATH = '/home/work/jmeterCase'
    LOCAL_RESULT_PATH = '/home/work/jmeterResult'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + \
        'hdic_admin:654321@10.33.107.20:3306/perf?charset=utf8'
    DEBUG = True


class TestConfig(Config):
    SERVER_PORT = 5002
    LOCAL_CASE_PATH = '/home/work/jmeterCase'
    LOCAL_RESULT_PATH = '/home/work/jmeterResult'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + \
        'root:homelink@10.33.107.24:6606/perf?charset=utf8'
    DEBUG = True

class DevConfig(Config):
    SERVER_PORT = 5005
    LOCAL_CASE_PATH = '/home/chenxiaoyang/jmeterCase'
    LOCAL_RESULT_PATH = '/home/chenxiaoyang/jmeterResult'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + \
        'root:homelink@10.33.107.24:6606/perf?charset=utf8'
    DEBUG = True


config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
    'default': DevConfig}
