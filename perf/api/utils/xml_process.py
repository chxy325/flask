# -*- coding: utf-8 -*-
"""
    xml manager
    ~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import json
import xmltodict


class XmlProcess(object):

    def __init__(self):
        pass

    @classmethod
    def parse(cls, source):
        doc = xmltodict.parse(source, encoding='utf-8')
        return doc

    @classmethod
    def unparse2file(cls, input_dict, output_file):
        xmltodict.unparse(input_dict, output=output_file, pretty=True)

    @classmethod
    def unparse(cls, input_dict):
        xmltodict.unparse(input_dict, pretty=True)

