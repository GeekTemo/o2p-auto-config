# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

# 已经登录
LOGINED = 'logined'
# 透传
TRANSMISSION = 'tranis'
# 协转
CONVERT = 'convert'

WEBSERVICE = 'webservice'
HTTP = 'http'
REST = 'rest'

SUCCESS = 'success'
FAIL = 'fail'

# 状态,每个状态对应一个页面
state = {LOGINED: 'base.html', TRANSMISSION: 'transm.html', CONVERT: 'convert.html'}

Request = 'REQ'
Response = 'RSP'


# 内容格式
class Con_Type(object):
    XML = "1"
    JSON = "2"
    URL_GET = "3"


# ID后缀数字的最大值
MAX_ID_SUFFIX_NUMBER = 999


# 通讯协议
class COMM_PRO_CD(object):
    http_get = 1
    rest = 11
    http_post = 2
    http_get_post = 3
    sftp = 4
    ftp = 5
    webservice = 6
    socket = 7

# 通讯协议映射
comm_pro_cd_map = {WEBSERVICE: COMM_PRO_CD.webservice, HTTP: COMM_PRO_CD.http_get_post, REST: COMM_PRO_CD.rest}


class comm_pro_type(object):
    # 入协议
    in_protocol = 1
    # 出协议
    out_protocol = 2


# attr_spec列表
class attr_spec(object):
    # 描述webservice 方法名
    webserviceoperation = 202
    # webservice 请求名
    webserviceInput = 203
    # webservice 响应名
    webserviceOutput = 204
    # 调用地址
    address = 1
    # rest资源
    rest_resource = 205
    # rest方法
    rest_action = 206
    # 代表服务技术实现ID属性的ID值
    service_tech_id = 34
    # 代表转换规则属性ID 的属性
    transformer_rule_id = 991000147
    # 协转时调用外部 WebService调用方法 属性
    webserviceMethod = 35


# 数据类型
class DataType(object):
    String = 1
    Integer = 2
    Long = 3
    Double = 4
    Date = 5
    JavaBean = 6
    Array = 12
    XML = 101
    JSON = 102

# 数据类型名
DataTypeName = {DataType.String: "String", DataType.XML: "XML", DataType.JSON: "JSON"}


class EndpointType(object):
    # 开发端点
    Begin = 7
    # 调用端点
    Call = 6
    # 转换端点
    Transfomer = 5
    # 结束端点
    End = 11


class EndPoint_Spec_Attr(object):
    # 调用服务技术实现属性ID
    call_service_tech_id = 22
    # 转换端点的适配属性ID
    transformer_rule_id = 990000030


# 信息文档类型
class Message_Doc_Type(object):
    XML = "xml"
    JSON = "json"
    String = "string"


# 配置REST方案的时候,技术实现的component_id只能为1005
O2p_Commpoent_ID = 1005


# XSTL转换模板
xstl_template = '''
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        %s
    </xsl:template>
</xsl:stylesheet>
'''

xstl_valueof_template = '''<xsl:value-of select="%s"/>'''

json_2_json_script = open('json_2_json.bs', 'r').read()
json_2_xml_script = open('json_2_xml.bs', 'r').read()
xml_2_json_script = open('xml_2_json.bs', 'r').read()


class Adapter_Type(object):
    beanshell = 3
    xstl = 5


# 已经配置过
HAVED_CONFIGED = 1

import db_utils


def get_session(db_env):
    key = db_env['host'] + ':' + db_env['user'] + ':' + db_env['passwd'] + ':' + db_env['db'] + ':' + db_env['port']
    if key in sessions:
        return sessions[key]
    else:
        session = db_utils.create_session(db_env)
        sessions[key] = session
        return session
