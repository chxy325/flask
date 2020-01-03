# -*- coding: utf-8 -*-
"""
    jenkins
    ~~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""
import jenkins

_jenkins_server_url = 'http://ci.lianjia.com/'
_user_id = 'chenxiaoyang'
_api_token = 'Chen1234'


class JenkinsUtil(object):
    def __init__(self):
        pass

    @classmethod
    def connect_jenkins(cls):
        server = jenkins.Jenkins(_jenkins_server_url,
                                 username=_user_id,
                                 password=_api_token)
        return server
