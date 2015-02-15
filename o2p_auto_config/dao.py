# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

from db_utils import *
import utils
import bo
import sqls
from bs4 import BeautifulSoup

# 根据version获取contract
def get_contract_by_version(version, db_env):
    session = create_session(db_env)
    contract = session.query(bo.Contract).from_statement(sqls.get_contract_by_version).params(baseversion).first()
    return contract


# 根据用户填写的信息判断是否已经配置过
def if_haved_config(flow):
    session = create_session(flow.db_env)
    contract_operation_names = None
    if flow.protocol == constant.WEBSERVICE:
        if not flow.doc_version_str:
            contract_operation_names = session.query('RESOURCE_ALISS', 'DOC_VERSION', 'VERSION', 'VALUE',
                                                     'ATTR_SPEC_CODE').from_statement(
                sqls.get_contract_operation_name).params(version=flow.org.name + flow.operation).params(
                resource_alis=flow.resource_alis)
        else:
            contract_operation_names = session.query('RESOURCE_ALISS', 'DOC_VERSION', 'VERSION', 'VALUE',
                                                     'ATTR_SPEC_CODE').from_statement(
                sqls.get_contract_operation_name + ' AND T1.DOC_VERSION = :doc_version').params(
                version=flow.org.name + flow.operation).params(
                resource_alis=flow.resource_alis).params(doc_version=flow.doc_version_str)
        if not contract_operation_names:
            return False
        elif len(contract_operation_names) == 1:
            if contract_operation_names[0][4] == 'webserviceOperation' and contract_operation_names[0][
                3] == flow.operation:
                return True
            elif contract_operation_names[0][4] == 'webserviceInput' and contract_operation_names[0][3] == flow.input:
                return True
            else:
                return False
        elif len(contract_operation_names) == 2:
            return True
    elif flow.protocol == constant.REST:
        pass


# 根据用户输入的必要参数,判断是否已经配置过
def if_have_configued(flow):
    contract_id = None
    session = get_session(flow.db_env)
    # base_version = flow.base_contract_version_str
    resource_alis = flow.resource_alis_str
    doc_version = flow.doc_version_str  # 默认为1.0
    operation = flow.operation
    if doc_version:
        contract_id = session.query('contract_id').from_statement(
            sqls.if_have_configued).params(
            resource_alis=resource_alis,
            doc_version=doc_version,
            operation=operation).first()
    else:
        contract_id = session.query('contract_id').from_statement(
            sqls.if_have_configued).params(
            resource_alis=resource_alis,
            doc_version='1.0',
            operation=operation).first()
    return contract_id


# 根据resouce_alis 与, doc_version以及request_method获取api_operation列表
def get_api_operation_list(resource_alis, request_method, db_env, doc_version=None):
    api_operation_list = None
    session = create_session(db_env)
    # 如果没有dov_version
    if not doc_version:
        api_operation_list = session.query('resource_alis', 'doc_version', 'version').from_statement(
            sqls.get_api_operation).params(resource_alis=resource_alis).first()
    else:
        api_operation_list = session.query('resource_alis', 'doc_version', 'version').from_statement(
            sqls.get_api_operation + ' AND T1.DOC_VERSION = :doc_version').params(resource_alis=resource_alis,
                                                                                  doc_version=doc_version)
    if not api_operation_list:
        return None
    elif len(api_operation_list) == 1:  # 如果一个资源别名对应一个服务
        contract_operation_names = None
        if not doc_version:
            contract_operation_names = session.query('RESOURCE_ALISS', 'DOC_VERSION', 'VERSION', 'VALUE',
                                                     'ATTR_SPEC_CODE').from_statement(
                sqls.get_contract_operation_name).params(resource_alis='OttWimp').all()
        elif doc_version:
            contract_operation_names = session.query('RESOURCE_ALISS', 'DOC_VERSION', 'VERSION', 'VALUE',
                                                     'ATTR_SPEC_CODE').from_statement(
                sqls.get_contract_operation_name + ' AND T1.doc_version=:doc_version').params(
                resource_alis='OttWimp').params(doc_version=doc_version).all()
        if not contract_operation_names:
            return api_operation_list
        else:
            pass
    return api_operation_list


# 根据资源别名获取协议文档
def get_contract_doc_by_resource_alis(db_env, resource_alis, doc_version=None):
    seeesion = get_session(db_env)
    if doc_version:
        contract_doc = seeesion.query(bo.Contract_doc).filter(
            bo.Contract_doc.resource_aliss == resource_alis).filter(bo.Contract_doc.doc_version == doc_version).first()
    else:
        contract_doc = seeesion.query(bo.Contract_doc).filter(bo.Contract_doc.resource_aliss == resource_alis).first()
    return contract_doc


# 检测文档协议是否存在，如果存在则返回，否则返回None
def exists_doc_contract(contract_doc_id, contract_version_id, db_env):
    session = get_session(db_env)
    doc_contract = session.query(bo.Doc_contract).filter(bo.Doc_contract.contract_doc_id == contract_doc_id).filter(
        bo.Doc_contract.contract_version_id == contract_version_id).first()
    return doc_contract


# 配置节点描述
# is_base表示是否描述基类协议(就是Header部分)
def config_node_desc(contract_format, xml_doc, is_base, flow):
    node_descs = []
    root = BeautifulSoup(xml_doc, 'xml')
    if is_base:
        header = root.Header
        leaf_nodes = utils.get_leaf_nodes(header)
        for tag in leaf_nodes:
            xpath = utils.get_tag_xpath(tag)
            node_desc = bo.Node_desc()
            node_desc.node_desc_id = flow.generate_table_id(bo.Node_desc.__tablename__, 'node_desc_id')
            node_desc.tcp_ctr_f_id = contract_format.tcp_ctr_f_id
            node_desc.node_name = tag.name
            node_desc.node_code = tag.name
            node_desc.node_path = xpath
            node_desc.java_field = tag.name
            node_descs.append(node_desc)
    else:
        body = root.Body
        leaf_nodes = utils.get_leaf_nodes(body)
        for tag in leaf_nodes:
            xpath = utils.get_tag_xpath(tag)
            node_desc = bo.Node_desc()
            node_desc.node_desc_id = flow.generate_table_id(bo.Node_desc.__tablename__, 'node_desc_id')
            node_desc.tcp_ctr_f_id = contract_format.tcp_ctr_f_id
            node_desc.node_name = tag.name
            node_desc.node_code = tag.name
            node_desc.node_path = xpath
            node_desc.java_field = tag.name
            node_descs.append(node_desc)
    return node_descs


# 配置端点,这个是最复杂的
def config_endpoints(flow):
    flow.endpoints = []
    # 透传Begin->Call-End
    if flow.configplan == constant.TRANSMISSION:
        begin_endpoint = bo.Endpoint()
        begin_endpoint.endpoint_id = flow.generate_table_id(bo.Endpoint.__tablename__, 'endpoint_id')
        begin_endpoint.endpoint_spec_id = constant.EndpointType.Begin
        begin_endpoint.in_data_type_id = utils.get_message_type(flow.req_doc)
        begin_endpoint.out_data_type_id = utils.get_message_type(flow.req_doc)
        begin_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.Begin'
        begin_endpoint.endpoint_code = begin_endpoint.endpoint_name
        flow.endpoints.append(begin_endpoint)

        call_endpoint = config_call_endpoints(flow)
        flow.endpoints.append(call_endpoint)

        end_endpoint = bo.Endpoint()
        end_endpoint.endpoint_id = flow.generate_table_id(bo.Endpoint.__tablename__, 'endpoint_id')
        end_endpoint.endpoint_spec_id = constant.EndpointType.End
        end_endpoint.in_data_type_id = call_endpoint.out_data_type_id
        end_endpoint.out_data_type_id = call_endpoint.out_data_type_id
        end_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.End'
        end_endpoint.endpoint_code = end_endpoint.endpoint_name
        flow.endpoints.append(end_endpoint)
    # 协转Begin->Transform->Call->Transform->End
    elif flow.configplan == constant.CONVERT:
        # 开始端点
        begin_endpoint = bo.Endpoint()
        begin_endpoint.endpoint_id = flow.generate_table_id(bo.Endpoint.__tablename__, 'endpoint_id')
        begin_endpoint.endpoint_spec_id = constant.EndpointType.Begin
        begin_endpoint.in_data_type_id = utils.get_message_type(flow.input_doc)
        begin_endpoint.out_data_type_id = utils.get_message_type(flow.input_doc)
        begin_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.Begin'
        begin_endpoint.endpoint_code = begin_endpoint.endpoint_name
        flow.endpoints.append(begin_endpoint)
        # 转换端点,转换req文档
        trans_endpoint1 = config_trans_endpoint(flow, flow.input_doc, flow.target_input_doc, constant.Request)
        flow.endpoints.append(trans_endpoint1)
        # 调用端点
        call_endpoint = config_call_endpoints(flow)
        flow.endpoints.append(call_endpoint)
        # 转换端点,转换rsp文档
        trans_endpoint2 = config_trans_endpoint(flow, flow.target_output_doc, flow.output_doc, constant.Response)
        flow.endpoints.append(trans_endpoint2)
        # 转换结束端点
        end_endpoint = bo.Endpoint()
        end_endpoint.endpoint_id = flow.generate_table_id(bo.Endpoint.__tablename__, 'endpoint_id')
        end_endpoint.endpoint_spec_id = constant.EndpointType.End
        end_endpoint.in_data_type_id = call_endpoint.out_data_type_id
        end_endpoint.out_data_type_id = call_endpoint.out_data_type_id
        end_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.End'
        end_endpoint.endpoint_code = end_endpoint.endpoint_name
        flow.endpoints.append(end_endpoint)
    return flow


# 配置调用端点,不同方案的调用端点属性值也不一样
def config_call_endpoints(flow):
    call_endpoint = bo.Endpoint()
    call_endpoint.endpoint_id = flow.generate_table_id(bo.Endpoint.__tablename__, 'endpoint_id')
    call_endpoint.endpoint_spec_id = constant.EndpointType.Call
    call_endpoint.in_data_type_id = flow.endpoints[
        -1].out_data_type_id  # 上一个端点的输入类型 flow.endpoints[-1].out_data_type_id
    call_endpoint.out_data_type_id = flow.endpoints[
        -1].out_data_type_id  # 上一个端点的输入类型 flow.endpoints[-1].out_data_type_id
    call_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.Call'
    call_endpoint.endpoint_code = call_endpoint.endpoint_name
    # 配置调用端点的技术实现
    tech_impl = bo.Tech_impl()
    tech_impl.tech_impl_id = flow.generate_table_id(bo.Tech_impl.__tablename__, 'tech_impl_id')
    tech_impl.tech_imp_con_po_id = constant.comm_pro_type.out_protocol
    tech_impl.tech_impl_name = flow.org.name + '.' + flow.operation
    tech_impl.comm_pro_cd = constant.comm_pro_cd_map[flow.protocol]
    tech_impl.component_id = flow.component.component_id
    call_endpoint.tech_impl = tech_impl
    # 配置技术实现属性
    call_endpoint.tech_impl.attrs = []
    # 如果是WebService 则只需要配置Address地址
    if flow.target_protocol == constant.WEBSERVICE or flow.target_protocol == constant.HTTP:
        tech_impl_attr = bo.Tech_imp_att()
        tech_impl_attr.tech_imp_att_id = flow.generate_table_id(bo.Tech_imp_att.__tablename__, 'tech_imp_att_id')
        tech_impl_attr.tech_impl_id = tech_impl.tech_impl_id
        tech_impl_attr.attr_spec_id = constant.attr_spec.address
        tech_impl_attr.attr_spec_value = flow.target_url
        call_endpoint.tech_impl.attrs.append(tech_impl_attr)
        # 如果是协赚调用WebService
        if flow.configplan == constant.CONVERT:
            method_tech_impl_attr = bo.Tech_imp_att()
            method_tech_impl_attr.tech_imp_att_id = flow.generate_table_id(bo.Tech_imp_att.__tablename__,
                                                                           'tech_imp_att_id')
            method_tech_impl_attr.tech_impl_id = tech_impl.tech_impl_id
            method_tech_impl_attr.attr_spec_id = constant.attr_spec.webserviceMethod
            method_tech_impl_attr.attr_spec_value = flow.target_method
            call_endpoint.tech_impl.attrs.append(method_tech_impl_attr)
    # 如果是Rest,则需要配置Address, RestResource, RestAction
    elif flow.target_protocol == constant.REST:
        # 解析地址
        add_regex = r'(http://[^/]+)'
        import re

        addr = re.findall(add_regex, flow.target_url)[0]
        rest_resource = flow.target_url.replace(addr, '')

        addr_tech_impl_attr = bo.Tech_imp_att()
        addr_tech_impl_attr.tech_imp_att_id = flow.generate_table_id(bo.Tech_imp_att.__tablename__, 'tech_imp_att_id')
        addr_tech_impl_attr.tech_impl_id = call_endpoint.tech_impl.tech_impl_id
        addr_tech_impl_attr.attr_spec_id = constant.attr_spec.address
        addr_tech_impl_attr.attr_spec_value = addr
        call_endpoint.tech_impl.attrs.append(addr_tech_impl_attr)

        rest_resource_tech_impl_attr = bo.Tech_imp_att()
        rest_resource_tech_impl_attr.tech_imp_att_id = flow.generate_table_id(bo.Tech_imp_att.__tablename__,
                                                                              'tech_imp_att_id')
        rest_resource_tech_impl_attr.tech_impl_id = call_endpoint.tech_impl.tech_impl_id
        rest_resource_tech_impl_attr.attr_spec_id = constant.attr_spec.rest_resource
        rest_resource_tech_impl_attr.attr_spec_value = rest_resource
        call_endpoint.tech_impl.attrs.append(rest_resource_tech_impl_attr)

        rest_action_tech_impl_attr = bo.Tech_imp_att()
        rest_action_tech_impl_attr.tech_imp_att_id = flow.generate_table_id(bo.Tech_imp_att.__tablename__,
                                                                            'tech_imp_att_id')
        rest_action_tech_impl_attr.tech_impl_id = call_endpoint.tech_impl.tech_impl_id
        rest_action_tech_impl_attr.attr_spec_id = constant.attr_spec.rest_action
        rest_action_tech_impl_attr.attr_spec_value = flow.action_method
        call_endpoint.tech_impl.attrs.append(rest_action_tech_impl_attr)
    # 配置服务技术实现
    ser_tech_impl = bo.Ser_tech_impl()
    ser_tech_impl.ser_tech_impl_id = flow.generate_table_id(bo.Ser_tech_impl.__tablename__, 'ser_tech_impl_id')
    ser_tech_impl.service_id = flow.service.service_id
    ser_tech_impl.tech_impl_id = tech_impl.tech_impl_id
    call_endpoint.ser_tech_impl = ser_tech_impl
    # 配置调用端点的属性
    endpoint_attr_value = bo.Endpoint_attr_value()
    endpoint_attr_value.endpoint_attr_value_id = flow.generate_table_id(bo.Endpoint_attr_value.__tablename__,
                                                                        'endpoint_attr_value_id')
    endpoint_attr_value.endpoint_id = call_endpoint.endpoint_id
    endpoint_attr_value.endpoint_spec_attr_id = constant.EndPoint_Spec_Attr.call_service_tech_id
    endpoint_attr_value.attr_value = ser_tech_impl.ser_tech_impl_id

    call_endpoint.attr_value = endpoint_attr_value
    return call_endpoint


# 配置路由
def config_route(flow):
    endpoints = flow.endpoints
    flow.routes = []
    size = len(endpoints)
    for i in range(size - 1):
        service_route_config = bo.Service_route_config()
        service_route_config.route_id = flow.generate_table_id(bo.Service_route_config.__tablename__, 'route_id')
        service_route_config.from_endpoint_id = flow.endpoints[i].endpoint_id
        service_route_config.to_endpoint_id = flow.endpoints[i + 1].endpoint_id
        service_route_config.message_flow_id = flow.message_flow.message_flow_id
        flow.routes.append(service_route_config)
    return flow


# 配置转换端点
# from_doc_type 从什么类型
# to_doc_type 到什么类型
# req_rsp 表明是转换请求格式还是转换响应格式
def config_trans_endpoint(flow, in_doc, out_doc, req_rsp):
    trans_endpoint = bo.Endpoint()
    trans_endpoint.endpoint_id = flow.generate_table_id(bo.Endpoint.__tablename__, 'endpoint_id')
    trans_endpoint.endpoint_spec_id = constant.EndpointType.Transfomer
    trans_endpoint.in_data_type_id = utils.get_message_type(in_doc)
    trans_endpoint.out_data_type_id = utils.get_message_type(out_doc)
    if req_rsp == constant.Request:
        trans_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.Request.Transform'
        trans_endpoint.endpoint_code = trans_endpoint.endpoint_name
    elif req_rsp == constant.Response:
        trans_endpoint.endpoint_name = flow.org.name + '.' + flow.operation + '.Response.Transform'
        trans_endpoint.endpoint_code = trans_endpoint.endpoint_name
    # 适配
    contract_adapter = bo.Contract_adapter()
    contract_adapter.CONTRACT_ADAPTER_ID = flow.generate_table_id(bo.Contract_adapter.__tablename__,
                                                                  'CONTRACT_ADAPTER_ID')
    if req_rsp == constant.Request:
        contract_adapter.APAPTER_NAME = flow.org.name + '.' + flow.operation + ' input adapter'
    else:
        contract_adapter.APAPTER_NAME = flow.org.name + '.' + flow.operation + ' output adapter'
    if req_rsp == constant.Request:
        contract_adapter.SCRIPT_SRC = utils.generate_script(in_doc, out_doc, flow.input_map_rule_text, req_rsp)
    elif req_rsp == constant.Response:
        contract_adapter.SCRIPT_SRC = utils.generate_script(in_doc, out_doc, flow.output_map_rule_text, req_rsp)
    trans_endpoint.contract_adapter = contract_adapter
    # 端点属性
    endpoint_attr_value = bo.Endpoint_attr_value()
    endpoint_attr_value.endpoint_attr_value_id = flow.generate_table_id(bo.Endpoint_attr_value.__tablename__,
                                                                        'endpoint_attr_value_id')
    endpoint_attr_value.endpoint_id = trans_endpoint.endpoint_id
    endpoint_attr_value.endpoint_spec_attr_id = constant.EndPoint_Spec_Attr.transformer_rule_id
    endpoint_attr_value.attr_value = contract_adapter.CONTRACT_ADAPTER_ID
    trans_endpoint.attr_value = endpoint_attr_value
    return trans_endpoint
    







