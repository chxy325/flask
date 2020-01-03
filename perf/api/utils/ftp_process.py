# -*- coding: utf-8 -*-
"""
    xml manager
    ~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""
import StringIO
import os
# import gzip
from ftplib import FTP
# from urllib2 import urlopen
from urllib import urlretrieve
# from werkzeug.utils import secure_filename
# from utils.log import logger
#from ..models.db import db
#from ..models.task import Task
#from ..utils.log import logger

# _host = '10.33.107.24'  # ftp地址
# _port = 21  # 端口号
# _timeout = 50000  # 超时时间
# _username = 'work'  # ftp用户名
# _password = 'qa2016@lianjia'  # ftp 密码
# _remote_path = '/home/work/perf/jmeter/Case/'  # ftp服务器的路径 (例：ftp://10.10.76.217/up)


class FtpProcess(object):
    def __init__(self, host=None, port=21, username=None, password=None, default_path=None):
        timeout = 50000
        self.conn = FTP()
        self.conn.connect(host, port, timeout)  # 连接ftp服务器
        self.conn.login(username, password)  # 登录ftp服务器
        self.conn.cwd(default_path)  # 设置ftp服务器端的处理目录
        self.host = host
        self.path = default_path

    def read_file(self, file_name=None):
        # path = os.path.join(os.environ['HOME'], 'jmeterLocalLog')
        # if not os.path.exists(path):
        #    os.makedirs(path)
        # name = os.path.join(path, file_name)

        sio = StringIO.StringIO()

        def handle_binary(more_data):
            sio.write(more_data)
        # self.conn.retrlines('RETR %s'%file_name, callback=handle_binary)
        self.conn.retrbinary('RETR %s' % file_name, callback=handle_binary)
        # self.conn.retrbinary('RETR %s'%file_name, open(name, 'wb').write)

        sio.seek(0)     # Go back to the start
        return sio.read()

    def read_file_by_url(self, file_name):
        path = os.path.join(os.environ['HOME'], 'tmpJmeter')
        if not os.path.exists(path):
            os.makedirs(path)

        name = os.path.join(path, file_name)
        path = 'ftp://' + self.host + self.path + file_name
        # u = urlopen(path)
        urlretrieve(path, name)
        # return u.read()

    def upload_file(self, file_path=None):
        local_file = open(file_path, 'rb')  # 打开本地文件
        self.conn.storbinary('STOR %s' % os.path.basename(
            file_path), local_file)  # 上传文件到ftp服务器
        local_file.close()  # 关闭本地文件
        self.conn.quit()  # 退出

    def delete_file(self, file_name=None):
        self.conn.delete(file_name)

    def file_exist(self, file_name=None):
        file_list = self.conn.nlst()
        # logger.info("Remote file list is: %s"%file_list)
        if file_name in file_list:
            return True
        else:
            return False


class HandleRemoteFile(object):
    def __init__(self):
        pass

    @classmethod
    def is_log_exist(cls, task_id):
        """
        判断远程日志是否存在
        """
        # machine_info = Jmeter.query.join(Task, Task.press_machine == Jmeter.machine_ip).filter(Task.id == task_id)
        task_info = Task.get_slave_info(task_id)
        if not task_info:
            raise Exception("任务信息获取异常")

        fp = FtpProcess(host=task_info.machine_ip,
                        port=21,
                        username=task_info.machine_user,
                        password=task_info.machine_passwd,
                        default_path=task_info.jmeter_report_path)

        if not fp.file_exist(task_info.jmeter_report):
            return False
        else:
            return True

    @classmethod
    def get_remote_log(cls, task_id, app=None):
        """
        根据task_id 获取远程slave节点的log文件, 返回的是string
        """
        if app:
            with app.app_context():
                task_info = Task.get_slave_info(task_id)
        else:
            task_info = Task.get_slave_info(task_id)
        fp = FtpProcess(host=task_info.machine_ip,
                        port=21,
                        username=task_info.machine_user,
                        password=task_info.machine_passwd,
                        default_path=task_info.jmeter_report_path)

        if not fp.file_exist(task_info.jmeter_report):
            raise Exception("task_id = %s 的任务未获取到日志" % task_id)

        remote_file = fp.read_file(task_info.jmeter_report)
        return remote_file


if __name__ == "__main__":
    fp = FtpProcess(host="10.10.35.183",
                    port=21,
                    username="ftpadmin",
                    password="Bknew2018",
                    default_path="/home/work/perf/jmeter/case")
