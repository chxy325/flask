# -*- coding: utf-8 -*-
import os
from ..models.jmeter import Jmeter
from ..utils.ftp_process import FtpProcess
from ..utils.log import logger
from ..configs import Config
from flask import current_app


class UploadService(object):
    def __init__(self):
        pass

    @classmethod
    def upload_file(cls, local_case_path=None, script_name=None, server_room_id=None,
                    source_jmx_file=None, source_csv_file=None, script_type=1, upload_type=1):
        """
        文件上传功能
        :param script_name:
        :param server_room_id:
        :param source_jmx_file:jmx文件
        :param source_csv_file: csv文件
        :param script_type: 1上传脚本 2编辑脚本
        :param upload_type: 1新建 2 更新
        :return:
        """
        # app = current_app
        # with app.app_context():
        # local_case_path = app.config['LOCAL_CASE_PATH']
        if not os.path.exists(local_case_path):
            os.makedirs(local_case_path)

        # 上传脚本
        jmx_file = "%s.jmx" % script_name
        if script_type == 1:
            if source_jmx_file is not "":
                local_jmx_file = os.path.join(local_case_path, jmx_file)
                source_jmx_file.save(local_jmx_file)
        else:
            local_jmx_file = source_jmx_file

        jmeter_slaves = Jmeter.query.filter(Jmeter.server_room_id == server_room_id).all()
        for jmeter_slave in jmeter_slaves:
            fp = FtpProcess(host=jmeter_slave.machine_ip,
                            port=21,
                            username=jmeter_slave.machine_user,
                            password=jmeter_slave.machine_passwd,
                            default_path=jmeter_slave.jmeter_case_path)
            if upload_type == 1:
                if fp.file_exist(jmx_file):
                    raise Exception("jmeter slave driver {}服务器已存在名字为{}的脚本"
                                    .format(jmeter_slave.machine_ip, jmx_file))
            else:
                # 删除原脚本
                if fp.file_exist(jmx_file):
                    fp.delete_file(jmx_file)

        for slave in jmeter_slaves:
            fp = FtpProcess(host=slave.machine_ip,
                            port=21,
                            username=slave.machine_user,
                            password=slave.machine_passwd,
                            default_path=slave.jmeter_case_path)
            # 上传新脚本
            if source_jmx_file is not "":
                fp.upload_file(local_jmx_file)

        if source_csv_file is not "":
            csv_file = "%s.txt" % script_name
            local_csv_file = os.path.join(local_case_path, csv_file)
            source_csv_file.save(local_csv_file)

            for slave in jmeter_slaves:
                fp = FtpProcess(host=slave.machine_ip,
                                port=21,
                                username=slave.machine_user,
                                password=slave.machine_passwd,
                                default_path=slave.jmeter_case_path)
                # 上传参数化文件
                fp.upload_file(local_csv_file)
