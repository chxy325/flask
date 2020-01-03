# -*- coding: utf-8 -*-

import traceback
# import os
# import datetime
# from werkzeug.utils import secure_filename
from flask import jsonify, request, Blueprint, current_app
from ..models.db import db
from ..models.script import Script
# from models.machine import Machine
# from ..models.jmeter import Jmeter
from ..utils.log import logger
# from ..utils.ftp_process import FtpProcess
from ..utils.upload_service import UploadService

# _headers = {
#             'Content-Disposition': 'form-data',
#             'type': 'file',
#             "Content-Type": 'application/octet-stream'
#            }

_allowed_extensions = set(['jmx'])

upload = Blueprint('upload', __name__, url_prefix='/api/upload')


# 网页测试上传文件功能
@upload.route('/file',methods=['GET'],strict_slashes=False)
def file_upload():
    return """<form method="POST" enctype="multipart/form-data">
      <input type="file" name="file"></br>
      脚本名字: <input type="text" name="filename" /><br />
      脚本描述: <input type="text" name="fileDes" /></hr>
      ip: <input type="text" name="machineIp" />
      <input type="submit" value="保存">
</form>"""


@upload.route('/file', methods=['POST'], strict_slashes=False)
def api_upload():
    """
    上传脚本到指定服务器
    """
    source_jmx_file = request.files.get('jmxFile','')  # 从表单的file字段获取文件，file为该表单的name值
    is_parametric = request.form.get('isParametric')
    script_name = request.form.get('fileName')
    description = request.form.get('fileDesc')
    product_id = request.form.get('productId')
    server_room_id = request.form.get('serverRoomId')
    monitor_machine = request.form.get('monitorMachine')
    logger.info(request.form)

    if not source_jmx_file or not _allowed_file(source_jmx_file.filename):
        raise Exception("不存在的脚本或脚本格式不对，请上传.jmx格式脚本")

    source_csv_file = None
    if is_parametric:
        source_csv_file = request.files.get('csvFile', '')

    app = current_app
    with app.app_context():
        local_case_path = app.config['LOCAL_CASE_PATH']
    UploadService.upload_file(local_case_path=local_case_path,
                              script_name=script_name,
                              server_room_id=server_room_id,
                              source_jmx_file=source_jmx_file,
                              source_csv_file=source_csv_file)

    script = Script()
    script.name = script_name
    script.description = description
    script.prd_id = product_id
    script.server_room_id = server_room_id
    script.monitor_machine = monitor_machine
    script.is_parametric = is_parametric
    # script.create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.add(script)
    db.session.commit()
    # # 返回脚本id
    # script_id = script.id

    return jsonify({"code": 1, "msg": "success", "data": {"scriptId": script.id}})


# 用于判断文件后缀
def _allowed_file(file_name):
    return '.' in file_name and file_name.rsplit('.', 1)[1] in _allowed_extensions


@upload.errorhandler(Exception)
def error_handle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})
