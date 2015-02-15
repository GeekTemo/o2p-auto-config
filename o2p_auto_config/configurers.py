# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

import constant
from db_utils import *

from bo import *
import dao
import exceptions
from core import *
from dao import *


class BaseConfiguer(object):
    def __init__(self, flow):
        self.flow = flow

    def config(self):
        pass


# WebService配置类
class WebServiceConfiguer(BaseConfiguer):
    def __init__(self, flow):
        super(WebServiceConfiguer, self).__init__(flow)

    def config(self):
        # 首先配置组织(如果存在则不用配置)
        self.flow.org = Org.get_or_generate_org(self.flow)
        # 配置组件
        self.flow.component = Component.get_or_generate_component(self.flow)
        # 配置App
        self.flow.app = App.get_or_generate_app(self.flow)
        # 路径信息
        pathinfo = self.flow.path.split('/')
        # 基类协议
        base_contract_version_str = None
        # 文档协议
        doc_version_str = None
        # 资源别名
        resource_alis_str = None
        if len(pathinfo) == 3:  # /base_contract_version/resource_alis
            base_contract_version_str = pathinfo[1]
            resource_alis_str = pathinfo[2]
        elif len(pathinfo) == 4:  # /base_contract_version/doc_version/resource_alis
            base_contract_version_str = pathinfo[1]
            doc_version_str = pathinfo[2]
            resource_alis_str = pathinfo[3]
        self.flow.base_contract_version_str = base_contract_version_str
        self.flow.doc_version_str = doc_version_str
        self.flow.resource_alis_str = resource_alis_str
        # 根据base_contract_str,doc_version_Str, doc_version_str, operation判断是否已经配置过
        # 如果已经配置过则不用在配置了
        if if_have_configued(self.flow):
            return self.flow, constant.HAVED_CONFIGED
        # 先根据baseversion查询base_contract是否存在
        base_contract = Contract.get_contract_by_version(base_contract_version_str, self.flow.db_env)
        # 如果不存在则根据报文头创建基类协议
        if not base_contract:
            self.flow.base_contract = Contract.generate_contract(self.flow, True)
        else:
            self.flow.base_contract = base_contract
        # 配置业务协议
        self.flow.contract = Contract.generate_contract(self.flow, False)
        # 配置基类业务协议版本
        self.flow.base_contract_version = Contract_version.generate_contract_version(self.flow, True)
        # 配置业务协议版本
        self.flow.contract_version = Contract_version.generate_contract_version(self.flow, False)
        # 配置基类业务协议请求格式
        self.flow.base_req_contract_format = Contract_format.generate_contract_format(self.flow, constant.Request, True)
        # 配置业务协议请求格式
        self.flow.req_contract_format = Contract_format.generate_contract_format(self.flow, constant.Request, False)
        # 配置基类业务协议响应格式
        self.flow.base_rsp_contract_format = Contract_format.generate_contract_format(self.flow, constant.Response,
                                                                                      True)
        # 配置业务协议响应格式
        self.flow.rsp_contract_format = Contract_format.generate_contract_format(self.flow, constant.Response, False)

        # 配置基类协议节点描述
        self.flow.base_contract.node_descs = dao.config_node_desc(self.flow.base_req_contract_format,
                                                                  self.flow.req_doc or self.flow.input_doc,
                                                                  True, self.flow)
        # 配置协议节点描述
        self.flow.contract.node_descs = dao.config_node_desc(self.flow.req_contract_format,
                                                             self.flow.req_doc or self.flow.input_doc, False,
                                                             self.flow)
        # 配置业务协议文档
        self.flow.contract_doc = Contract_doc.get_or_generate_doc(self.flow, resource_alis_str)
        # 配置文档协议
        self.flow.doc_contract = Doc_contract.get_or_generate_doc_contract(self.flow)
        # 配置业务协议属性 一般只有WebService方案的时候才配置
        self.flow = Contract_2_attr_spec.config_contract_attr(self.flow)
        # 配置服务
        self.flow.service = Service.generate_service(self.flow)
        # 配置端点
        self.flow = config_endpoints(self.flow)
        # 配置消息流
        self.flow.message_flow = Message_flow.generate_message_flow(self.flow)
        # 配置路由
        self.flow = config_route(self.flow)
        # 配置调用实例
        self.flow.ser_invoke_ins = Ser_invoke_ins.generate_ser_invoke_ins(self.flow)
        return exec_ws_config_flow(self.flow)
        # return self.flow, constant.SUCCESS


# REST方案的配置
class RestConfiguer(BaseConfiguer):
    def __init__(self, flow):
        super(RestConfiguer, self).__init__(flow)

    def config(self):
        # 配置组织
        # 首先配置组织(如果存在则不用配置)
        self.flow.org = Org.get_or_generate_org(self.flow)
        # 配置组件
        self.flow.component = Component.get_or_generate_component(self.flow)
        # 配置APP
        self.flow.app = App.get_or_generate_app(self.flow)
        # 配置contract
        self.flow.contract = Contract.generate_contract(self.flow, False)
        # 配置contract_version
        self.flow.contract_version = Contract_version.generate_contract_version(self.flow, False)
        # 配置服务
        self.flow.service = Service.generate_service(self.flow)
        # 配置REST的技术实现
        self.flow.rest_tech_impl = Tech_impl.generate_tech_impl(self.flow, constant.comm_pro_type.in_protocol)
        # 配置REST的技术实现属性列表
        self.flow.rest_tech_impl_attrs = Tech_imp_att.generate_rest_tech_impl_atts(self.flow)
        # 配置REST服务技术实现
        self.flow.rest_ser_tech_impl = Ser_tech_impl.generate_rest_ser_tech_impl(self.flow)
        # 配置端点
        self.flow = config_endpoints(self.flow)
        # 配置消息流
        self.flow.message_flow = Message_flow.generate_message_flow(self.flow)
        # 配置路由
        self.flow = config_route(self.flow)
        # 配置调用实例
        self.flow.ser_invoke_ins = Ser_invoke_ins.generate_ser_invoke_ins(self.flow)
        return exec_rest_config_flow(self.flow)


class HttpConfiguer(BaseConfiguer):
    def __init__(self, flow):
        self.flow = flow

    def config(self):
        pass


configuers = {constant.WEBSERVICE: WebServiceConfiguer, constant.REST: RestConfiguer,
              constant.HTTP: WebServiceConfiguer}