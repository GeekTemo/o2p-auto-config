# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'
import constant

# 获取xml头部节点的路径
def get_xml_head_node_path(xml):
    pass


from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

# 获取指定节点的所有的叶子节点
def get_leaf_nodes(root):
    leaf_nodes = []
    for child in root.descendants:
        if is_leaf_node(child):
            leaf_nodes.append(child)
    return leaf_nodes


def is_leaf_node(node):
    if isinstance(node, Tag):
        for child in node.children:
            if isinstance(child, Tag):
                return False
        return True
    return False


def join_all_tag_path(prefix, tag_name):
    if not prefix:
        return tag_name
    else:
        return prefix + ':' + tag_name


# 获取节点路径
def get_tag_path(tag):
    if isinstance(tag, BeautifulSoup):
        return ''
    if not tag.parent:
        return join_all_tag_path(tag.prefix, tag.name)
    return join_all_tag_path(tag.prefix, tag.name) + '/' + get_tag_path(tag.parent)


# 规整节点路径
def order_tag_path(tag_path):
    path_info = tag_path.split('/')[::-1]
    path = ''
    for p in path_info:
        if p:
            path += '/' + p
    return path


# 获取节点的XPath路径
def get_tag_xpath(tag):
    tag_path = get_tag_path(tag)
    return order_tag_path(tag_path)


# 获取不带前缀的节点的路径
def get_tag_path_without_prefix(tag):
    if isinstance(tag, BeautifulSoup):
        return ''
    if not tag.parent:
        return tag.name
    return get_tag_path_without_prefix(tag.parent) + '/' + tag.name


# 获取body内数据结构,如果Body内为空则返回None
def get_xml_body_strutc_name(xml):
    root = BeautifulSoup(xml, 'xml')
    body = root.Body
    for child in body.children:
        if isinstance(child, Tag):
            return child.name
    return None


# 根据消息获内容取消息的类型
def get_message_type(message):
    if message.startswith('<'):
        return constant.DataType.XML
    elif message.startswith('{'):
        return constant.DataType.JSON
    else:
        return constant.DataType.String


# 对象路径转换为XML路径
def obj_path_2_xml_path(obj_path):
    return '/' + obj_path.replace('.', '/')


# 根据节点路径找到Tag对象
def find_tag_by_no_prefix_path(root, path):
    leaf_tags = get_leaf_nodes(root)
    for leaf_tag in leaf_tags:
        if get_tag_path_without_prefix(leaf_tag) == path:
            return leaf_tag
    return None


# 根据对象路径找到Tag对象
def find_tag_by_obj_path(root, obj_path):
    path = obj_path_2_xml_path(obj_path)
    return find_tag_by_no_prefix_path(root, path)


import string

# 根据源文档与目标文档以及映射规则产生转换脚本
def generate_script(src_doc, target_doc, map_rule_text, req_rsp):
    script = ''
    src_doc_type = get_message_type(src_doc)
    target_doc_type = get_message_type(target_doc)
    map_rules = map_rule_text.split(';')
    rules = [tuple(rule.split('=')) for rule in map_rules]
    # XML->XML
    if src_doc_type == target_doc_type and src_doc_type == constant.DataType.XML:
        src_doc_root = BeautifulSoup(src_doc, 'xml')
        target_doc_root = BeautifulSoup(target_doc, 'xml')
        for rule in rules:
            src_tag = find_tag_by_obj_path(src_doc_root, rule[0])  # 源文档节点
            target_tag = find_tag_by_obj_path(target_doc_root, rule[1])  # 目标文档节点
            src_xpath = get_tag_xpath(src_tag)  # 源文档节点XPath路径
            target_tag.string = constant.xstl_valueof_template % src_xpath
        script = constant.xstl_template % target_doc_root.prettify().replace('&lt;', '<').replace('&gt;', '>')
    # XML->JSON
    elif src_doc_type == constant.DataType.XML and target_doc_type == constant.DataType.JSON:
        script_template = string.Template(constant.xml_2_json_script)
        if req_rsp == constant.Request:  # 如果是转换请求参数
            kws = {'xml_str': 'messageBO.getReqmessage()', 'json_str': target_doc, 'rule_text': map_rule_text}
            script = script_template.substitute(kws)
            script += 'messageBO.setReqmessage(result_json_str);'
        elif req_rsp == constant.Response:  # 如果是转换响应参数
            kws = {'xml_str': 'messageBO.getRspmessage()', 'json_str': target_doc, 'rule_text': map_rule_text}
            script = script_template.substitute(kws)
            script += 'messageBO.setRspmessage(result_json_str);'
    # JSON->XML
    elif src_doc_type == constant.DataType.JSON and target_doc_type == constant.DataType.XML:
        script_template = string.Template(constant.json_2_xml_script)
        if req_rsp == constant.Request:
            kws = {'json_str': 'messageBO.getReqmessage()', 'xml_str': target_doc, 'rule_text': map_rule_text}
            script = script_template.substitute(kws)
            script += 'messageBO.setReqmessage(result_xml_str);'
        elif req_rsp == constant.Response:
            kws = {'json_str': 'messageBO.getRspmessage()', 'xml_str': target_doc, 'rule_text': map_rule_text}
            script = script_template.substitute(kws)
            script += 'messageBO.setRspmessage(result_xml_str)'
    # JSON->JSON
    elif src_doc_type == constant.DataType.JSON and target_doc_type == constant.DataType.JSON:
        script_template = string.Template(constant.json_2_json_script)
        if req_rsp == constant.Request:
            kws = {'src_json': 'messageBO.getReqmessage()', 'target_json': target_doc, 'rule_text': map_rule_text}
            script = script_template.substitute(kws)
            script += 'messageBO.setReqmessage(result_json_str);'
        elif req_rsp == constant.Response:
            kws = {'src_json': 'messageBO.getRspmessage()', 'target_json': target_doc, 'rule_text': map_rule_text}
            script = script_template.substitute(kws)
            script += 'messageBO.setRspmessage(result_xml_str)'
    return script


if __name__ == '__main__':
    src_doc = open('/Users/gongxingfa/placeAnOrder.xml', 'r').read()
    target_doc = open('/Users/gongxingfa/order.xml', 'r').read()
    map_rules = ['Envelope.Body.PlaceAnOrderRequest.orderId=Order.id',
                 'Envelope.Body.PlaceAnOrderRequest.customerName=Order.name',
                 'Envelope.Body.PlaceAnOrderRequest.customerAddress=Order.address']
    script = generate_script(src_doc, target_doc, map_rules)
    print script





