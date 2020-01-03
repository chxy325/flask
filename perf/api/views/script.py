# -*- coding: utf-8 -*-
"""
    blueprints of monitor
    ~~~~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import os
import json
import traceback
import urllib
import copy
# from collections import OrderedDict
from flask import Blueprint, request, jsonify, current_app
from ..utils.log import logger
from ..utils.xml_manager import XmlManager
from ..utils.xml_process import XmlProcess
from ..utils.ftp_process import FtpProcess
from ..utils.upload_service import UploadService
from ..models.db import db
from ..models.script import Script
# from ..models.task import Task
from ..models.jmeter import Jmeter

script = Blueprint('script', __name__, url_prefix='/api/script')


def _get_local_path():
    app = current_app
    with app.app_context():
        return app.config['LOCAL_CASE_PATH']


@script.route('/add', methods=['POST'])
def script_insert():
    """
    @description: 新建脚本接口
    @param:
            "name":,
            "description": ,
            "serverRoomId": "",
            "monitorMachine" : "",
            "productId":,
            "base": {
                "ip":"",
                "port":"",
                "route":"",
                "requestMethod":, GET, POST
                "paramType":, 1-form 2-参数化 3-json
                "param":{},
                "threads": 1,
                "rampTime": 1,
                "loops": -1,
                "duration": null
            }
    """
    # data = request.get_json()
    data = request.form.to_dict()
    for k, v in data.iteritems():
        if k == 'base':
            data[k] = json.loads(v)
    logger.info(data)

    local_case_path = _get_local_path()
    jmx_file = _get_jmx_file(data, local_case_path)
    logger.info(jmx_file)

    source_csv_file = ""
    if data['base']['paramType'] == 2:
        source_csv_file = request.files['csvFile']

    # 编辑脚本script_type=2  新建upload_type=1
    UploadService.upload_file(local_case_path=local_case_path,
                              script_name=data['name'],
                              server_room_id=data['serverRoomId'],
                              source_jmx_file=jmx_file,
                              source_csv_file=source_csv_file,
                              script_type=2,
                              upload_type=1)
    os.remove(jmx_file)
        
    target_script = Script()
    target_script.prd_id = data['productId']
    target_script.name = data['name']
    target_script.description = data['description']
    target_script.server_room_id = data['serverRoomId']
    target_script.parameter = json.dumps(data['base'])
    target_script.monitor_machine = data['monitorMachine']
    db.session.add(target_script)
    db.session.commit()

    return jsonify({"code": 1, "msg": 'success', "data": {"scriptId": target_script.id}})


@script.route('/update', methods=['POST'])
def script_update():
    """
    @description: 编辑脚本接口
    @param:
            "name":,
            "description": ,
            "serverRoomId": "",
            "monitorMachine" : "",
            "scriptId":,
            "base": {
                "ip":"",
                "port":"",
                "route":"",
                "requestMethod":, GET, POST
                "paramType":, 1-form 2-参数化 3-json
                "param":{},
                "threads": 1,
                "rampTime": 1,
                "loops": -1,
                "duration": null
            }
    """
    # data = request.get_json()
    data = request.form.to_dict()
    for k, v in data.iteritems():
        if k == 'base':
            data[k] = json.loads(v)
    logger.info(data)

    target_script = Script.query.filter(Script.id == data['scriptId']).first()
    if not target_script:
        raise Exception("未从数据库中获取到script_id=%s的记录" % data['scriptId'])

    local_case_path = _get_local_path()
    jmx_file = _get_jmx_file(data, local_case_path)
    logger.info(jmx_file)

    source_csv_file = ""
    if data['base']['paramType'] == 2:
        source_csv_file = request.files['csvFile']

    # 编辑脚本script_type=2 更新upload_type=2
    UploadService.upload_file(local_case_path=local_case_path,
                              script_name=data['name'],
                              server_room_id=data['serverRoomId'],
                              source_jmx_file=jmx_file,
                              source_csv_file=source_csv_file,
                              script_type=2,
                              upload_type=2)
    os.remove(jmx_file)

    target_script.name = data['name']
    target_script.description = data['description']
    target_script.server_room_id = data['serverRoomId']
    target_script.parameter = json.dumps(data['base'])
    target_script.monitor_machine = data['monitorMachine']
    db.session.add(target_script)
    db.session.commit()

    return jsonify({"code": 1, "msg": 'success', "data": {"scriptId": target_script.id}})


@script.route('/del', methods=['POST'])
def script_del():
    """
    @description: 删除脚本接口 ftp远程删除
    @param: script_id           #脚本id
    """
    data = request.get_json()
    logger.info(data)

    target_script = Script.query.filter(Script.id == data['script_id']).first()
    if not target_script:
        raise Exception("未从数据库中获取到script_id=%s的记录" % data['script_id'])

    file_name = target_script.name + ".jmx"
    csv_file_name = target_script.name + ".txt"
    jmeter_slaves = Jmeter.query.filter(Jmeter.server_room_id == target_script.server_room_id)
    for slave in jmeter_slaves:
        ftp_process = FtpProcess(host=slave.machine_ip,
                                 port=21,
                                 username=slave.machine_user,
                                 password=slave.machine_passwd,
                                 default_path=slave.jmeter_case_path)

        if ftp_process.file_exist(file_name):
            ftp_process.delete_file(file_name)

        if ftp_process.file_exist(csv_file_name):
            ftp_process.delete_file(csv_file_name)

    db.session.delete(target_script)
    db.session.commit()

    return jsonify({"code": 1, "msg": 'success', "data": {}})


def _get_jmx_file(data, local_case_path):
    """
    根据参数生成新的jmx脚本
    :param data:
    :return:
    """
    # get
    if data['base']['requestMethod'] == "GET":
        # form
        if data['base']['paramType'] == 1:
            jmx_file = _get_form_jmx(data, local_case_path)
        # 参数化
        else:
            jmx_file = _get_parametric_jmx(data, local_case_path)
    # post
    else:
        # form
        if data['base']['paramType'] == 1:
            jmx_file = _post_form_jmx(data, local_case_path)
        # 参数化
        elif data['base']['paramType'] == 2:
            jmx_file = _post_parametric_jmx(data, local_case_path)
        # json
        else:
            jmx_file = _post_json_jmx(data, local_case_path)
    return jmx_file


def _get_form_jmx(data, local_case_path):
    """
    方法：新建、编辑接口,统一处理脚本,处理get参数
    :return:
    """
    tmp_path = data['base']['route'][1:] if data['base']['route'].startswith('/') else data['base']['route']
    param = urllib.urlencode(data['base']['param'])
    path = tmp_path + '?' + param
    is_scheduler = "true" if data['base']['loops'] == "-1" else "false"

    jmx_path = os.path.join(os.path.dirname(__file__), "../data/")
    source_jmx_file = jmx_path + "template_get.jmx"
    des_jmx_file = local_case_path + '/' +  data['name'] + ".jmx"
    logger.info(des_jmx_file)
    xml_update = XmlManager(source_jmx_file, des_jmx_file)

    xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
                                filter_dict={"name": "HTTPSampler.domain"},
                                text=data['base']['ip'])
    xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
                                filter_dict={"name": "HTTPSampler.path"},
                                text=path)
    xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
                                filter_dict={"name": "HTTPSampler.port"},
                                text=data['base']['port'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
                                filter_dict={"name": "ThreadGroup.num_threads"},
                                text=data['base']['threads'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
                                filter_dict={"name": "ThreadGroup.ramp_time"},
                                text=data['base']['rampTime'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/elementProp/stringProp',
                                filter_dict={"name": "LoopController.loops"},
                                text=data['base']['loops'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
                                filter_dict={"name": "ThreadGroup.duration"},
                                text=data['base']['duration'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/boolProp',
                                filter_dict={"name": "ThreadGroup.scheduler"},
                                text=is_scheduler)

    return des_jmx_file


def _post_form_jmx(data, local_case_path):
    """
    方法：处理post接口，表单形式参数
    :return:
    """
    path = data['base']['route'][1:] if data['base']['route'].startswith('/') else data['base']['route']
    is_scheduler = "true" if data['base']['loops'] == "-1" else "false"

    jmx_path = os.path.join(os.path.dirname(__file__), "../data/")
    source_jmx_file = jmx_path + "template_post_form.jmx"
    des_jmx_file = local_case_path + '/' + data['name'] + ".jmx"

    # xml文件转化成json
    s_json = _xml2json(source_jmx_file)
    # logger.info(s_json)

    # 处理json
    # ip port path
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['stringProp']
    for key in tmp_list:
        if key['@name'] == "HTTPSampler.domain":
            key['#text'] = data['base']['ip']
        elif key['@name'] == "HTTPSampler.port":
            key['#text'] = data['base']['port']
        elif key['@name'] == "HTTPSampler.path":
            key['#text'] = path
    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['stringProp'] = tmp_list

    # threads  rampTime duration
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['stringProp']
    for key in tmp_list:
        if key['@name'] == "ThreadGroup.num_threads":
            key['#text'] = data['base']['threads']
        elif key['@name'] == "ThreadGroup.ramp_time":
            key['#text'] = data['base']['rampTime']
        elif key['@name'] == "ThreadGroup.duration":
            key['#text'] = data['base']['duration']
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['stringProp'] = tmp_list

    # loops
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['elementProp']['stringProp']['#text'] \
        = data['base']['loops']

    # scheduler
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['boolProp']['#text'] = is_scheduler

    # form param
    s_json = _add_node_jmx(s_json, data['base']['param'])
    # logger.info(json.dumps(s_json, indent=4))

    # json生成xml文件
    _json2xml(s_json, des_jmx_file)

    # xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
    #                             filter_dict={"name": "HTTPSampler.domain"},
    #                             text=data['base']['ip'])
    # xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
    #                             filter_dict={"name": "HTTPSampler.path"},
    #                             text=path)
    # xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
    #                             filter_dict={"name": "HTTPSampler.port"},
    #                             text=data['base']['port'])

    # xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
    #                             filter_dict={"name": "ThreadGroup.num_threads"},
    #                             text=data['base']['threads'])
    # xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
    #                             filter_dict={"name": "ThreadGroup.ramp_time"},
    #                             text=data['base']['rampTime'])
    # xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/elementProp/stringProp',
    #                             filter_dict={"name": "LoopController.loops"},
    #                             text=data['base']['loops'])
    # xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
    #                             filter_dict={"name": "ThreadGroup.duration"},
    #                             text=data['base']['duration'])
    # xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/boolProp',
    #                             filter_dict={"name": "ThreadGroup.scheduler"},
    #                             text=is_scheduler)
    #
    # _add_node_jmx(xml_update, data['base']['param'])

    return des_jmx_file


def _xml2json(sourcefile):
    """
    xml文件转化为json串
    :param sourcefile:
    :return:
    """
    template_file = open(sourcefile, 'r')
    sourcefile = template_file.read()
    template_file.close()

    doc = XmlProcess.parse(sourcefile)
    # res = json.dumps(doc)
    # res = json.loads(res)
    return doc


def _json2xml(input_dict, destfile):
    """
    json串生成xml文件
    :param destfile:
    :return:
    """
    df = open(destfile, 'wb')
    # json2xml = json.loads(input_dict, object_pairs_hook=OrderedDict)
    XmlProcess.unparse2file(input_dict, df)
    df.close()


def _add_node_jmx(s_json, param, type=None):
    """
    jmx文件新增节点
    :param xml_update:
    :param param:
    :return:
    """
    tmp_dict = {
        "@name": "a",
        "@elementType": "HTTPArgument",
        "boolProp": [
            {
                "@name": "HTTPArgument.always_encode",
                "#text": "false"
            },
            {
                "@name": "HTTPArgument.use_equals",
                "#text": "true"
            }
        ],
        "stringProp": [
            {
                "@name": "Argument.value",
                "#text": "1"
            },
            {
                "@name": "Argument.metadata",
                "#text": "="
            },
            {
                "@name": "Argument.name",
                "#text": "a"
            }
        ]
    }
    tmp_list = []
    if len(param) == 0:
        tmp = None
    elif len(param) == 1:
        for k, v in param.iteritems():
            if type is 'csv':
                v = '${' + v + '}'
            tmp_dict['@name'] = k
            for key in tmp_dict['stringProp']:
                if key['@name'] == "Argument.value":
                    key['#text'] = v
                elif key['@name'] == "Argument.name":
                    key['#text'] = k
        tmp = {"@name": "Arguments.arguments", "elementProp": tmp_dict}
    else:
        for k, v in param.iteritems():
            if type is 'csv':
                v = '${' + v + '}'
            d = copy.deepcopy(tmp_dict)
            d['@name'] = k
            for key in d['stringProp']:
                if key['@name'] == "Argument.value":
                    key['#text'] = v
                elif key['@name'] == "Argument.name":
                    key['#text'] = k
            tmp_list.append(d)
            # logger.info(tmp_list)
        tmp = {"@name": "Arguments.arguments", "elementProp": tmp_list}

    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['elementProp']['collectionProp']\
        = tmp

    return s_json


def _post_json_jmx(data, local_case_path):
    """
    方法：处理post接口，json形式参数
    :return:
    """
    path = data['base']['route'][1:] if data['base']['route'].startswith('/') else data['base']['route']
    is_scheduler = "true" if data['base']['loops'] == "-1" else "false"

    jmx_path = os.path.join(os.path.dirname(__file__), "../data/")
    source_jmx_file = jmx_path + "template_post_json.jmx"
    des_jmx_file = local_case_path + '/' + data['name'] + ".jmx"
    xml_update = XmlManager(source_jmx_file, des_jmx_file)

    xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
                                filter_dict={"name": "HTTPSampler.domain"},
                                text=data['base']['ip'])
    xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
                                filter_dict={"name": "HTTPSampler.path"},
                                text=path)
    xml_update.modify_xml_value(path='hashTree/hashTree/hashTree/HTTPSamplerProxy/stringProp',
                                filter_dict={"name": "HTTPSampler.port"},
                                text=data['base']['port'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
                                filter_dict={"name": "ThreadGroup.num_threads"},
                                text=data['base']['threads'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
                                filter_dict={"name": "ThreadGroup.ramp_time"},
                                text=data['base']['rampTime'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/elementProp/stringProp',
                                filter_dict={"name": "LoopController.loops"},
                                text=data['base']['loops'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/stringProp',
                                filter_dict={"name": "ThreadGroup.duration"},
                                text=data['base']['duration'])
    xml_update.modify_xml_value(path='hashTree/hashTree/ThreadGroup/boolProp',
                                filter_dict={"name": "ThreadGroup.scheduler"},
                                text=is_scheduler)
    xml_update.modify_xml_value(path=('hashTree/hashTree/hashTree/HTTPSamplerProxy/'
                                'elementProp/collectionProp/elementProp/stringProp'),
                                filter_dict={"name": "Argument.value"},
                                text=data['base']['param'])

    return des_jmx_file


def _get_parametric_jmx(data, local_case_path):
    """
    方法：处理get接口，参数化形式
    :return:
    """
    path = data['base']['route'][1:] if data['base']['route'].startswith('/') else data['base']['route']
    is_scheduler = "true" if data['base']['loops'] == "-1" else "false"

    jmx_path = os.path.join(os.path.dirname(__file__), "../data/")
    source_jmx_file = jmx_path + "template_get_csv.jmx"
    des_jmx_file = local_case_path + '/' + data['name'] + ".jmx"

    # xml文件转化成json
    s_json = _xml2json(source_jmx_file)
    logger.debug(json.dumps(s_json))

    # 处理json
    # ip port path
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['stringProp']
    for key in tmp_list:
        if key['@name'] == "HTTPSampler.domain":
            key['#text'] = data['base']['ip']
        elif key['@name'] == "HTTPSampler.port":
            key['#text'] = data['base']['port']
        elif key['@name'] == "HTTPSampler.path":
            key['#text'] = path
    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['stringProp'] = tmp_list

    # threads  rampTime duration
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['stringProp']
    for key in tmp_list:
        if key['@name'] == "ThreadGroup.num_threads":
            key['#text'] = data['base']['threads']
        elif key['@name'] == "ThreadGroup.ramp_time":
            key['#text'] = data['base']['rampTime']
        elif key['@name'] == "ThreadGroup.duration":
            key['#text'] = data['base']['duration']
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['stringProp'] = tmp_list

    # loops
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['elementProp']['stringProp']['#text'] \
        = data['base']['loops']

    # scheduler
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['boolProp']['#text'] = is_scheduler

    # CSVDataSet
    csv_file_name = data['name'] + '.txt'
    param_str = ''
    length = len(data['base']['param'])
    count = 0
    for k, v in data['base']['param'].iteritems():
        count += 1
        if count == length:
            param_str = param_str + v
        else:
            param_str = param_str + v + ','

    logger.info(csv_file_name)
    logger.info(param_str)
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['CSVDataSet']['stringProp']
    # logger.info(tmp_list)
    for key in tmp_list:
        if key['@name'] == 'filename':
            key['#text'] = csv_file_name
        elif key['@name'] == 'variableNames':
            key['#text'] = param_str
    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['CSVDataSet']['stringProp'] = tmp_list

    # csv param
    s_json = _add_node_jmx(s_json, data['base']['param'], type='csv')
    # logger.info(json.dumps(s_json, indent=4))

    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['hashTree'] = None

    # json生成xml文件
    _json2xml(s_json, des_jmx_file)

    xml_update = XmlManager(des_jmx_file, des_jmx_file)
    xml_update.add_node(path='hashTree/hashTree/hashTree',
                        tag='hashTree',
                        value_dict={})
    return des_jmx_file


def _post_parametric_jmx(data, local_case_path):
    """
    方法：处理post接口，参数化形式
    :return:
    """
    path = data['base']['route'][1:] if data['base']['route'].startswith('/') else data['base']['route']
    is_scheduler = "true" if data['base']['loops'] == "-1" else "false"

    jmx_path = os.path.join(os.path.dirname(__file__), "../data/")
    source_jmx_file = jmx_path + "template_post_csv.jmx"
    des_jmx_file = local_case_path + '/' + data['name'] + ".jmx"

    # xml文件转化成json
    s_json = _xml2json(source_jmx_file)
    # logger.info(s_json)

    # 处理json
    # ip port path
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['stringProp']
    for key in tmp_list:
        if key['@name'] == "HTTPSampler.domain":
            key['#text'] = data['base']['ip']
        elif key['@name'] == "HTTPSampler.port":
            key['#text'] = data['base']['port']
        elif key['@name'] == "HTTPSampler.path":
            key['#text'] = path
    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['HTTPSamplerProxy']['stringProp'] = tmp_list

    # threads  rampTime duration
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['stringProp']
    for key in tmp_list:
        if key['@name'] == "ThreadGroup.num_threads":
            key['#text'] = data['base']['threads']
        elif key['@name'] == "ThreadGroup.ramp_time":
            key['#text'] = data['base']['rampTime']
        elif key['@name'] == "ThreadGroup.duration":
            key['#text'] = data['base']['duration']
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['stringProp'] = tmp_list

    # loops
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['elementProp']['stringProp']['#text'] \
        = data['base']['loops']

    # scheduler
    s_json['jmeterTestPlan']['hashTree']['hashTree']['ThreadGroup']['boolProp']['#text'] = is_scheduler

    # CSVDataSet
    csv_file_name = data['name'] + '.txt'
    param_str = ''
    length = len(data['base']['param'])
    count = 0
    for k, v in data['base']['param'].iteritems():
        count += 1
        if count == length:
            param_str = param_str + v
        else:
            param_str = param_str + v + ','

    logger.info(csv_file_name)
    logger.info(param_str)
    tmp_list = s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['CSVDataSet']['stringProp']
    # logger.info(tmp_list)
    for key in tmp_list:
        if key['@name'] == 'filename':
            key['#text'] = csv_file_name
        elif key['@name'] == 'variableNames':
            key['#text'] = param_str
    s_json['jmeterTestPlan']['hashTree']['hashTree']['hashTree']['CSVDataSet']['stringProp'] = tmp_list

    # csv param
    s_json = _add_node_jmx(s_json, data['base']['param'], type='csv')
    # logger.info(json.dumps(s_json, indent=4))

    # json生成xml文件
    _json2xml(s_json, des_jmx_file)

    return des_jmx_file


@script.errorhandler(Exception)
def error_handle(error):
    logger.error(traceback.format_exc())
    return jsonify({
                   'code': 10000,
                   'msg': str(error),
                   'data': {}})

