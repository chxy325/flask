# -*- coding: utf-8 -*-
"""
    xml manager
    ~~~~~~~~~~~
    :copyright: (c) 2017 lianjia.com, Inc. All rights Reserved
"""

import xml.etree.ElementTree as ET
from log import logger
# from xml.etree.ElementTree import Element

class XmlManager(object):

    def __init__(self, source_path, dest_path):
        self.source_path = source_path
        self.dest_path = dest_path
        self.tree = ET.parse(self.source_path)
        # self.tree = ET.parse('D:\user.jmx')

    def modify_xml_value(self, path=None, filter_dict=None, value_dict=None, text=None):
        """
        根据路径 查找节点，修改此节点的属性或文本
        :param path:
        :param filter_dict:
        :param value_dict:
        :param text:
        :return:
        """
        nodes = self.get_nodes(path, filter_dict=filter_dict)
        if len(nodes) is 0:
            return
        for node in nodes:
            if value_dict is not None:
                self.modify_attrib_value(node, value_dict)
            if text is not None:
                node.text = str(text)
        self.tree.write(self.dest_path)

    def add_node(self, path, filter_dict=None, tag=None, value_dict=None, text=None):
        """
        根据路径 查找节点，在此节点下新增节点
        :param path:
        :param filter_dict:
        :param tag:
        :param value_dict:
        :param text:
        :return:
        """
        nodes = self.get_nodes(path, filter_dict=filter_dict)
	logger.info(len(nodes))
        if len(nodes) is 0:
            return
        for node in nodes:
            element = self.create_node(tag, value_dict, text)
            self.add_child_node(node, element)
        self.tree.write(self.dest_path)


    def modify_attrib_value(self, node, value_dict):
        for k, v in value_dict.items():
            node.set(k, v)

    # 根据路径查找node
    def find_nodes(self, path):
        return self.tree.findall(path)

    # 判断节点属性值是否匹配
    def is_match(self, node, kv_map):
        for k, v in kv_map.items():
            if node.get(k) != v:
                return False
        return True

    # 根据attrib的{key：value}筛选node
    def filter_nodes(self, nodes, filter_dict=None):
        nodelist = []
        if filter_dict is None:
            return nodes
        for node in nodes:
            if self.is_match(node, filter_dict):
                nodelist.append(node)
        return nodelist

    def get_nodes(self, path, filter_dict=None):
        tmp_nodes = self.find_nodes(path)
        nodes = self.filter_nodes(tmp_nodes, filter_dict=filter_dict)
        return nodes

    def create_node(self, tag, property_map, content):
        """
        新建节点
        :param tag: 节点标签
        :param property_map: 属性及属性值map
        :param content: 节点闭合标签里的文本内容
        :return: 新节点
        """
        element = ET.Element(tag, property_map)
        element.text = content
        return element

    def add_child_node(self, node, element):
        """
        给一个节点添加子节点
        :param nodelist: 节点
        :param element: 子节点
        :return:
        """
        node.append(element)
