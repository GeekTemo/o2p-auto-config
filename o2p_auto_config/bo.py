# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, BLOB, Text, Boolean

from db_utils import *
import sqls
import constant
from utils import *
import dao

Base = declarative_base()


# 组织
class Org(Base):
    __tablename__ = 'org'

    org_id = Column(Integer, primary_key=True)
    name = Column(String)
    org_code = Column(String)
    org_type_code = Column(String, default='1')
    org_username = Column(String)
    org_pwd = Column(String)
    cert_type_code = Column(String)
    s_file_id = Column(Integer)
    fil_s_file_id = Column(Integer)
    area_id = Column(Integer)
    cert_number = Column(String)
    telephone = Column(String)
    email = Column(String)
    audit_flow_id = Column(Integer)
    simple_spell = Column(String)
    state = Column(String)
    state_time = Column(DateTime, default=datetime.now)
    create_time = Column(DateTime, default=datetime.now)
    descriptor = Column(String)
    customer_id = Column(String)
    account_id = Column(String)
    capability = Column(String)
    application = Column(String)
    issuccesscase = Column(String)
    isindex = Column(String)
    partnerCode = Column(String)

    @staticmethod
    def get_or_generate_org(flow):
        session = get_session(flow.db_env)
        org_tmp = session.query(Org).filter(Org.org_code == flow.org.org_code).first()
        if not org_tmp:
            flow.org.org_id = flow.generate_table_id(Org.__tablename__, 'org_id')
            flow.org.org_username = flow.org.name
            flow.org.state = 'D'
            return flow.org
        return org_tmp


# 组件
class Component(Base):
    __tablename__ = 'component'

    component_id = Column(Integer, primary_key=True)
    org_id = Column(Integer)
    code = Column(String)
    name = Column(String)
    component_type_id = Column(Integer, default=1)
    audit_flow_id = Column(Integer)
    reg_time = Column(DateTime, default=datetime.now)
    state = Column(String, default='D')
    state_time = Column(DateTime, default=datetime.now)
    password = Column(String)
    descriptor = Column(String)
    s_file_id = Column(Integer)

    @staticmethod
    def get_or_generate_component(flow):
        session = get_session(flow.db_env)
        component = session.query(Component).filter(Component.org_id == flow.org.org_id).first()
        if not component:
            component = Component()
            component.component_id = flow.generate_table_id(Component.__tablename__, 'component_id')
            component.org_id = flow.org.org_id
            component.code = flow.org.org_code
            component.name = flow.org.name
        return component


# APP
class App(Base):
    __tablename__ = 'app'

    app_id = Column(Integer, primary_key=True)
    app_name = Column(String)
    app_summa = Column(String)
    app_url = Column(String)
    app_deve = Column(Integer)
    component_id = Column(Integer)
    app_type = Column(String, default='1')
    app_oauth_type = Column(String)
    s_file_id = Column(Integer)
    appkey = Column(String)
    appsecure = Column(String)
    app_create_time = Column(DateTime, default=datetime.now)
    audit_flow_id = Column(Integer)
    app_state = Column(String, default='A')
    app_callback_url = Column(String)
    app_desc = Column(String)
    TOKEN_ENABLE_TIME = Column(Integer)

    @staticmethod
    def get_or_generate_app(flow):
        session = get_session(flow.db_env)
        app = session.query(App).filter(App.component_id == flow.component.component_id).first()
        if not app:
            app = App()
            app.app_name = flow.component.name
            app.component_id = flow.component.component_id
        return app


class Contract(Base):
    __tablename__ = 'contract'

    contract_id = Column(Integer, primary_key=True)
    base_contract_id = Column(Integer)
    name = Column(String)
    code = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_time = Column(DateTime, default=datetime.now)
    descriptor = Column(String)
    is_base = Column(Boolean, default=False)

    @staticmethod
    def get_contract_by_version(version, db_env):
        session = get_session(db_env)
        contract = session.query(Contract).from_statement(sqls.get_contract_by_version).params(version=version).first()
        return contract

    # 产生一个contract
    @staticmethod
    def generate_contract(flow, is_base_contract):
        contract = Contract()
        if is_base_contract:  # 如果是基类协议
            contract.contract_id = flow.generate_table_id(Contract.__tablename__, 'contract_id')
            contract.name = flow.org.name + '.Base'
            contract.code = flow.org.name + '.Base'
            contract.is_base = True
        else:
            contract.contract_id = flow.generate_table_id(Contract.__tablename__, 'contract_id')
            if hasattr(flow, 'base_contract'):
                contract.base_contract_id = flow.base_contract.contract_id
            contract.name = flow.org.name + '.' + flow.operation
            contract.code = flow.org.name + '.' + flow.operation
            contract.is_base = False
        return contract


# 协议版本
class Contract_version(Base):
    __tablename__ = 'contract_version'

    contract_version_id = Column(Integer, primary_key=True)
    contract_id = Column(Integer)
    version = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_time = Column(DateTime, default=datetime.now)
    eff_date = Column(DateTime, default=datetime.now)
    exp_date = Column(DateTime, default=datetime.now)
    descriptor = Column(String)
    is_need_check = Column(String)

    @staticmethod
    def generate_contract_version(flow, is_base):
        contract_version = Contract_version()
        contract_version.contract_version_id = flow.generate_table_id(Contract_version.__tablename__,
                                                                      'contract_version_id')
        if is_base:
            contract_version.contract_id = flow.base_contract.contract_id
            contract_version.version = flow.base_contract_version_str
        else:
            contract_version.contract_id = flow.contract.contract_id
            contract_version.version = flow.org.name + '.' + flow.operation + '1.0'
        return contract_version


# 协议格式
class Contract_format(Base):
    __tablename__ = 'contract_format'

    tcp_ctr_f_id = Column(Integer, primary_key=True)
    contract_version_id = Column(Integer)
    req_rsp = Column(String)
    con_type = Column(String, default='1')
    xsd_header_for = Column(Text)
    xsd_format = Column(Text)
    xsd_demo = Column(Text)
    create_time = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_time = Column(DateTime, default=datetime.now)
    separators = Column(String)
    newline = Column(String)
    descriptor = Column(String)

    # 配置业务格式
    @staticmethod
    def generate_contract_format(flow, req_rsp, is_base):
        contract_format = Contract_format()
        contract_format.tcp_ctr_f_id = flow.generate_table_id(Contract_format.__tablename__, 'tcp_ctr_f_id')
        if is_base:
            contract_format.contract_version_id = flow.base_contract_version.contract_version_id
        else:
            contract_format.contract_version_id = flow.contract_version.contract_version_id
        contract_format.req_rsp = req_rsp
        return contract_format


# 协议属性定义
class Contract_2_attr_spec(Base):
    __tablename__ = 'contract_2_attr_spec'

    CONTRACT_2_ATTR_SPEC_ID = Column(Integer, primary_key=True)
    TCP_CTR_F_ID = Column(Integer)
    ATTR_SPEC_ID = Column(Integer)
    VALUE = Column(String)
    STATE = Column(String)

    # 配置contract的属性
    @staticmethod
    def config_contract_attr(flow):
        # 如果是WebService方式 需要配置方法名,入参,出参
        if flow.protocol == constant.WEBSERVICE:
            # 方法名
            operation = flow.operation
            operation_attr = Contract_2_attr_spec()
            operation_attr.CONTRACT_2_ATTR_SPEC_ID = flow.generate_table_id(Contract_2_attr_spec.__tablename__,
                                                                            'CONTRACT_2_ATTR_SPEC_ID')
            operation_attr.TCP_CTR_F_ID = flow.req_contract_format.tcp_ctr_f_id
            operation_attr.ATTR_SPEC_ID = constant.attr_spec.webserviceoperation
            operation_attr.VALUE = operation
            # 输入参数
            input = get_xml_body_strutc_name(flow.req_doc or flow.input_doc)
            input_attr = Contract_2_attr_spec()
            input_attr.CONTRACT_2_ATTR_SPEC_ID = flow.generate_table_id(Contract_2_attr_spec.__tablename__,
                                                                        'CONTRACT_2_ATTR_SPEC_ID')
            input_attr.TCP_CTR_F_ID = flow.req_contract_format.tcp_ctr_f_id
            input_attr.ATTR_SPEC_ID = constant.attr_spec.webserviceInput
            input_attr.VALUE = input
            # 输出参数
            # output = get_xml_body_strutc_name(flow.rsp_doc)
            # output_attr = Contract_2_attr_spec()
            # output_attr.ATTR_SPEC_ID = constant.attr_spec.webserviceOutput
            # output_attr.VALUE = output

            contract_attrs = {'operation': operation_attr, 'input': input_attr}
            contract_attr_list = [operation_attr, input_attr]
            flow.contract_attrs = contract_attrs
            flow.contract_attr_list = contract_attr_list
        return flow


# 服务定义
class Service(Base):
    __tablename__ = 'service'

    service_id = Column(Integer, primary_key=True)
    contract_version_id = Column(Integer)
    service_cn_name = Column(String)
    service_en_name = Column(String)
    service_code = Column(String)
    service_type = Column(String, default='0')
    service_version = Column(String)
    create_date = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_date = Column(DateTime, default=datetime.now)
    service_desc = Column(String)
    is_published = Column(String, default='Y')
    service_priority = Column(String)
    service_timeout = Column(Integer)
    default_msg_flow = Column(Integer)
    audit_flow_id = Column(Integer)

    @staticmethod
    def generate_service(flow):
        service = Service()
        service.service_id = flow.generate_table_id(Service.__tablename__, 'service_id')
        service.contract_version_id = flow.contract_version.contract_version_id
        service.service_cn_name = flow.org.name + '.' + flow.operation
        service.service_en_name = service.service_cn_name
        service.service_version = service.service_en_name + '1.0'
        service.service_code = service.service_cn_name
        return service


# 端点的定义
class Endpoint(Base):
    __tablename__ = 'ENDPOINT'

    endpoint_id = Column(Integer, primary_key=True)
    endpoint_spec_id = Column(Integer)
    in_data_type_id = Column(Integer)
    out_data_type_id = Column(Integer)
    endpoint_name = Column(String)
    endpoint_code = Column(String)
    enable_in_trace = Column(String)
    enable_out_trace = Column(String)
    enable_in_log = Column(String)
    enable_out_log = Column(String)
    create_date = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_date = Column(DateTime, default=datetime.now)
    endpoint_desc = Column(String)
    map_code = Column(String)


# 业务协议适配
class Contract_adapter(Base):
    __tablename__ = 'contract_adapter'

    CONTRACT_ADAPTER_ID = Column(Integer, primary_key=True)
    SRC_CTR_F_ID = Column(Integer)
    TAR_CTR_F_ID = Column(Integer)
    APAPTER_NAME = Column(String)
    ADAPTER_TYPE = Column(Integer)
    SCRIPT_SRC = Column(Text)
    STATE = Column(String, default='A')
    CREATE_DT = Column(DateTime, default=datetime.now)


# 端点属性
class Endpoint_attr_value(Base):
    __tablename__ = 'endpoint_attr_value'

    endpoint_attr_value_id = Column(Integer, primary_key=True)
    endpoint_id = Column(Integer)
    endpoint_spec_attr_id = Column(Integer)
    attr_value = Column(String)
    long_attr_value = Column(Text)


# 技术实现
class Tech_impl(Base):
    __tablename__ = 'tech_impl'

    tech_impl_id = Column(Integer, primary_key=True)
    tech_impl_name = Column(String)
    tech_imp_con_po_id = Column(Integer, default=constant.comm_pro_type.out_protocol)
    component_id = Column(Integer)
    comm_pro_cd = Column(String)
    reg_time = Column(DateTime, default=datetime.now)
    usealbe_state = Column(String, default='A')
    laest_time = Column(DateTime, default=datetime.now)

    # 产生技术实现
    @staticmethod
    def generate_tech_impl(flow, con_po_id):
        tech_impl = Tech_impl()
        tech_impl.tech_impl_id = flow.generate_table_id(Tech_impl.__tablename__, 'tech_impl_id')
        # 如果是REST方案
        if flow.protocol == constant.REST:
            tech_impl.tech_impl_name = flow.org.name + '.' + flow.operation
            tech_impl.tech_imp_con_po_id = con_po_id
            tech_impl.component_id = constant.O2p_Commpoent_ID
            tech_impl.comm_pro_cd = constant.COMM_PRO_CD.rest
        return tech_impl


# 技术实现属性
class Tech_imp_att(Base):
    __tablename__ = 'tech_imp_att'

    tech_imp_att_id = Column(Integer, primary_key=True)
    attr_spec_id = Column(Integer)
    tech_impl_id = Column(Integer)
    attr_spec_value = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    lastest_time = Column(DateTime, default=datetime.now)
    state = Column(String)

    # 配置rest方案的技术实现属性列表
    @staticmethod
    def generate_rest_tech_impl_atts(flow):
        rest_tech_impl_attrs = []
        # rest资源属性
        rest_resource_attr = Tech_imp_att()
        rest_resource_attr.tech_imp_att_id = flow.generate_table_id(Tech_imp_att.__tablename__, 'tech_imp_att_id')
        rest_resource_attr.attr_spec_id = constant.attr_spec.rest_resource
        rest_resource_attr.tech_impl_id = flow.rest_tech_impl.tech_impl_id
        rest_resource_attr.attr_spec_value = flow.path
        rest_tech_impl_attrs.append(rest_resource_attr)
        # rest方法属性
        rest_action_attr = Tech_imp_att()
        rest_action_attr.tech_imp_att_id = flow.generate_table_id(Tech_imp_att.__tablename__, 'tech_imp_att_id')
        rest_action_attr.attr_spec_id = constant.attr_spec.rest_action
        rest_action_attr.tech_impl_id = flow.rest_tech_impl.tech_impl_id
        rest_action_attr.attr_spec_value = flow.action_method
        rest_tech_impl_attrs.append(rest_action_attr)

        return rest_tech_impl_attrs


# 服务技术实现
class Ser_tech_impl(Base):
    __tablename__ = 'ser_tech_impl'

    ser_tech_impl_id = Column(Integer, primary_key=True)
    service_id = Column(Integer)
    tech_impl_id = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_time = Column(DateTime, default=datetime.now)

    @staticmethod
    def generate_rest_ser_tech_impl(flow):
        ser_tech_impl = Ser_tech_impl()
        ser_tech_impl.ser_tech_impl_id = flow.generate_table_id(Ser_tech_impl.__tablename__, 'ser_tech_impl_id')
        ser_tech_impl.service_id = flow.service.service_id
        ser_tech_impl.tech_impl_id = flow.rest_tech_impl.tech_impl_id
        return ser_tech_impl


# 消息流
class Message_flow(Base):
    __tablename__ = 'message_flow'

    message_flow_id = Column(Integer, primary_key=True)
    message_flow_name = Column(String)
    first_endpoint_id = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_time = Column(DateTime, default=datetime.now)
    descriptor = Column(String)

    @staticmethod
    def generate_message_flow(flow):
        mf = Message_flow()
        mf.message_flow_id = flow.generate_table_id(Message_flow.__tablename__, 'message_flow_id')
        mf.message_flow_name = flow.org.name + '.' + flow.operation + '.MessageFlow'
        mf.first_endpoint_id = flow.endpoints[0].endpoint_id
        return mf


# 服务路由配置
class Service_route_config(Base):
    __tablename__ = 'service_route_config'

    route_id = Column(Integer, primary_key=True)
    route_policy_id = Column(Integer, default=0)
    from_endpoint_id = Column(Integer)
    to_endpoint_id = Column(Integer)
    message_flow_id = Column(Integer)
    syn_asyn = Column(String, default='SYN')
    state = Column(String, default='A')
    create_date = Column(DateTime, default=datetime.now)
    lastest_date = Column(DateTime, default=datetime.now)
    map_code = Column(String)


# 服务调用实例
class Ser_invoke_ins(Base):
    __tablename__ = 'ser_invoke_ins'

    ser_invoke_ins_id = Column(Integer, primary_key=True)
    message_flow_id = Column(Integer)
    component_id = Column(Integer)
    service_id = Column(Integer)
    ser_invoke_ins_name = Column(String)
    create_date = Column(DateTime, default=datetime.now)
    state = Column(String, default='A')
    lastest_date = Column(DateTime, default=datetime.now)
    ser_invoke_ins_desc = Column(String)

    @staticmethod
    def generate_ser_invoke_ins(flow):
        ser_invoke_ins = Ser_invoke_ins()
        ser_invoke_ins.ser_invoke_ins_id = flow.generate_table_id(Ser_invoke_ins.__tablename__, 'ser_invoke_ins_id')
        ser_invoke_ins.component_id = flow.component.component_id
        ser_invoke_ins.message_flow_id = flow.message_flow.message_flow_id
        ser_invoke_ins.service_id = flow.service.service_id
        ser_invoke_ins.ser_invoke_ins_name = flow.org.name + '.' + flow.operation
        return ser_invoke_ins


# 文件共享
class File_share(Base):
    __tablename__ = 'file_share'

    s_file_id = Column(Integer, primary_key=True)
    s_file_name = Column(String)
    s_file_content = Column(BLOB)
    state = Column(String)
    create_time = Column(DateTime)


# 协议文档
class Contract_doc(Base):
    __tablename__ = 'contract_doc'

    contract_doc_id = Column(Integer, primary_key=True)
    base_con_doc_id = Column(Integer)
    doc_name = Column(String)
    doc_version = Column(String, default='1.0')
    doc_create_time = Column(DateTime)
    state = Column(String, default='A')
    lastest_time = Column(DateTime, default=datetime.now)
    doc_path = Column(String)
    doc_type = Column(String, default='1')
    resource_aliss = Column(String)


    @staticmethod
    def get_or_generate_doc(flow, resource_alis):
        contract_doc = dao.get_contract_doc_by_resource_alis(flow.db_env, flow.resource_alis_str, flow.doc_version_str)
        if not contract_doc:
            contract_doc = Contract_doc()
            contract_doc.contract_doc_id = flow.generate_table_id(Contract_doc.__tablename__, 'contract_doc_id')
            contract_doc.doc_name = flow.org.name + '.wsdl'
            contract_doc.resource_aliss = resource_alis
            contract_doc.doc_version = flow.doc_version_str
        return contract_doc


# 文档与协议之间的映射
class Doc_contract(Base):
    __tablename__ = 'doc_contract'

    doc_contr_id = Column(Integer, primary_key=True)
    contract_doc_id = Column(Integer)
    contract_version_id = Column(Integer)
    descriptor = Column(String)

    @staticmethod
    def get_or_generate_doc_contract(flow):
        doc_contract = dao.exists_doc_contract(flow.contract_doc.contract_doc_id,
                                               flow.contract_version.contract_version_id, flow.db_env)
        if not doc_contract:
            doc_contract = Doc_contract()
            doc_contract.doc_contr_id = flow.generate_table_id(Doc_contract.__tablename__, 'doc_contr_id')
            doc_contract.contract_doc_id = flow.contract_doc.contract_doc_id
            doc_contract.contract_version_id = flow.contract_version.contract_version_id
            doc_contract.descriptor = flow.org.name + '.' + flow.operation
        return doc_contract


# 节点描述
class Node_desc(Base):
    __tablename__ = 'node_desc'

    node_desc_id = Column(Integer, primary_key=True)
    tcp_ctr_f_id = Column(Integer)
    node_name = Column(String)
    node_code = Column(String)
    parent_node_id = Column(Integer)
    node_path = Column(String)
    node_type = Column(String, default='2')
    node_length_cons = Column(String)
    node_type_cons = Column(String)
    node_number_cons = Column(String)
    nevl_cons_type = Column(String)
    nevl_cons_value = Column(String)
    nevl_cons_desc = Column(String)
    is_need_check = Column(String)
    state = Column(String, default='A')
    create_time = Column(DateTime, default=datetime.now)
    lastest_time = Column(DateTime, default=datetime.now)
    description = Column(String)
    is_need_sign = Column(String)
    java_field = Column(String)


class Ng_recv_msg(Base):
    __tablename__ = 'ng_recv_msg'

    recv_msg_id = Column(Integer, primary_key=True)
    message_id = Column(String)
    msg_type = Column(Integer)
    busi_config_id = Column(Integer)
    part_id = Column(Integer)
    source_number = Column(String)
    target_number = Column(String)
    recv_time = Column(DateTime)
    recv_content = Column(String)
    notify_time = Column(DateTime)
    next_notify_time = Column(DateTime)
    notify_status = Column(Integer)
    notify_desc = Column(String)
    notify_count = Column(Integer)
    notify_resp_code = Column(String)
    subject = Column(String)
    tenant_id = Column(String)