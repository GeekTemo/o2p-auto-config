# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

import string

from bo import *
import constant
import db_utils


# 配置流,表示整个配置流程
class ConfigFlow(object):
    def __init__(self):
        # 路径
        self.path = None
        # 数据库环境
        self.db_env = {}
        # 协议方案
        self.protocol = None
        # 请求文档
        self.req_doc = None
        # 组织
        self.org = Org()
        # 记录配置过程中每张表产生过的ID
        self.id_counts = {}

    # 为每张表产生唯一的ID
    def generate_table_id(self, tablename, primary_key):
        id = None
        if tablename not in self.id_counts:
            self.id_counts[tablename] = []
            id = db_utils.generate_id(tablename, primary_key, self.org.org_code + '001', self.db_env)
            self.id_counts[tablename].append(id)
        else:
            last_id = self.id_counts[tablename][-1]
            id = db_utils.generate_id(tablename, primary_key, last_id + 1, self.db_env)
            self.id_counts[tablename].append(id)
        return id


from sqlalchemy import text
# 执行WebService配置流,要不全部成功，要不全部失败
def exec_ws_config_flow(flow):
    result = None
    session = get_session(flow.db_env)
    session.autocommit = False
    session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    try:
        # 添加组织
        if not session.query(Org).filter(Org.org_code == flow.org.org_code).first():
            session.add(flow.org)
        # 添加组件
        if not session.query(Component).filter(Component.org_id == flow.org.org_id).first():
            session.add(flow.component)
        # 添加app
        if not session.query(App).filter(App.app_id == flow.app.app_id).first():
            session.add(flow.app)
        # 如果基类协议不存在添加基类协议
        if not session.query(Contract).filter(Contract.contract_id == flow.base_contract.contract_id).first():
            add_contract(session, flow.base_contract)
        # 添加协议
        add_contract(session, flow.contract)
        # 添加基类协议版本
        session.add(flow.base_contract_version)
        # 添加业务协议版本
        session.add(flow.contract_version)
        # 添加基类协议请求格式
        session.add(flow.base_req_contract_format)
        # 添加基类协议响应格式
        session.add(flow.base_rsp_contract_format)
        # 添加业务请求格式
        session.add(flow.req_contract_format)
        # 添加业务响应格式
        session.add(flow.rsp_contract_format)

        # 添加业务协议文档
        session.add(flow.contract_doc)
        # 添加文档协议
        session.add(flow.doc_contract)
        # 添加业务协议属性
        session.add_all(flow.contract_attr_list)
        # 添加服务
        session.add(flow.service)
        # 配置端点
        for endpoint in flow.endpoints:
            add_endpoint(session, endpoint)
        # 添加消息流
        session.add(flow.message_flow)
        # 添加路由
        session.add_all(flow.routes)
        # 添加调用实例
        session.add(flow.ser_invoke_ins)
        # 全部添加成功提交
        session.commit()
        session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        flow.info = 'Success Configued'
        result = constant.SUCCESS
    except Exception, e:
        # 回滚
        session.rollback()
        session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        flow.info = str(e)
        result = constant.FAIL
        print e
    return flow, result


# 添加业务协议
def add_contract(session, contract):
    session.add(contract)
    session.add_all(contract.node_descs)


# 添加端点, 不同的端点要添加的附属值也不一样
def add_endpoint(session, endpoint):
    if endpoint.endpoint_spec_id == constant.EndpointType.Begin or endpoint.endpoint_spec_id == constant.EndpointType.End:
        session.add(endpoint)
    elif endpoint.endpoint_spec_id == constant.EndpointType.Call:
        session.add(endpoint)
        # 添加端点的技术实现
        session.add(endpoint.tech_impl)
        # 端点端点技术实现的属性
        session.add_all(endpoint.tech_impl.attrs)
        # 添加端点的服务技术实现
        session.add(endpoint.ser_tech_impl)
        # 添加端点的属性值
        session.add(endpoint.attr_value)
    elif endpoint.endpoint_spec_id == constant.EndpointType.Transfomer:
        session.add(endpoint)
        # 添加端点协议适配
        session.add(endpoint.contract_adapter)
        # 添加端点属性值
        session.add(endpoint.attr_value)


# 执行HTTP配置流
def exec_http_config_flow(flow):
    return flow, constant.SUCCESS


# 执行REST配置流
def exec_rest_config_flow(flow):
    result = None
    session = get_session(flow.db_env)
    session.autocommit = False
    session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
    try:
        # 添加组织
        if not session.query(Org).filter(Org.org_code == flow.org.org_code).first():
            session.add(flow.org)
        # 添加组件
        if not session.query(Component).filter(Component.org_id == flow.org.org_id).first():
            session.add(flow.component)
        # 添加app
        if not session.query(App).filter(App.app_id == flow.app.app_id).first():
            session.add(flow.app)
        # 添加业务协议
        session.add(flow.contract)
        # 配置业务协议版本
        session.add(flow.contract_version)
        # 添加服务
        session.add(flow.service)
        # 添加REST的技术实现
        session.add(flow.rest_tech_impl)
        # 添加REST的技术实现属性列表
        session.add_all(flow.rest_tech_impl_attrs)
        # 添加REST服务技术实现
        session.add(flow.rest_ser_tech_impl)
        # 配置端点
        for endpoint in flow.endpoints:
            add_endpoint(session, endpoint)
        # 添加消息流
        session.add(flow.message_flow)
        # 添加路由
        session.add_all(flow.routes)
        # 添加调用实例
        session.add(flow.ser_invoke_ins)
        # 全部添加成功提交
        session.commit()
        session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        flow.info = 'Success configued'
        result = constant.SUCCESS
    except Exception, e:
        # 回滚
        session.rollback()
        session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        flow.info = str(e)
        result = constant.FAIL
        print e
    return flow, result