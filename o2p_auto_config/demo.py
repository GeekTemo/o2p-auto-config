# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, BLOB, Text, Boolean

Base = declarative_base()


class Ng_recv_msg_view(Base):
    __tablename__ = 'v_ng_recv_msg'

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


class Ng_recv_msg(Base):
    __tablename__ = 'ng_recv_msg_0'

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


def creat_session(host, user, passwd, db):
    engine = create_engine('mysql://%s:%s@%s/%s' % (user, passwd, host, db))
    Session = sessionmaker(bind=engine)
    return Session()


iot_session = creat_session('10.30.1.7:3320', 'dbadmin', 'pwd_dbadmin', 'gateway_email')
pch_session = creat_session('10.1.196.41', 'root', 'lyqailk', 'gateway_email')


def query_ng_recv_msg(session, target_number):
    return session.query(Ng_recv_msg).filter(Ng_recv_msg.target_number == target_number).all()


def save_ng_recv_msg(session, ng_recv_msgs):
    session.add_all(ng_recv_msgs)
    session.commit()


def convert_view_2_table(view_obj):
    table_obj = Ng_recv_msg()
    table_obj.message_id = view_obj.message_id
    table_obj.msg_type = view_obj.msg_type
    table_obj.busi_config_id = view_obj.busi_config_id
    table_obj.part_id = view_obj.part_id
    table_obj.source_number = view_obj.source_number
    table_obj.target_number = view_obj.target_number
    table_obj.recv_time = view_obj.recv_time
    table_obj.recv_content = view_obj.recv_content
    table_obj.notify_time = view_obj.notify_time
    table_obj.next_notify_time = view_obj.next_notify_time
    table_obj.notify_status = view_obj.notify_status
    table_obj.notify_desc = view_obj.notify_desc
    table_obj.notify_count = view_obj.notify_count
    table_obj.notify_resp_code = view_obj.notify_resp_code
    table_obj.subject = view_obj.subject
    table_obj.tenant_id = view_obj.tenant_id
    return table_obj


def change_content_path(content_path, target_path):
    return target_path + content_path[content_path.rfind('/') + 1:]


if __name__ == '__main__':
    print 'start move........................'
    iot_msgs = query_ng_recv_msg(iot_session, 'columbine@fand01-12.dev.telenor.dk')
    table_objs = []
    for view_obj in iot_msgs:
        table_obj = convert_view_2_table(view_obj)
        table_obj.recv_content = change_content_path(table_obj.recv_content, '/home/ng/filedata/mail/receive/')
        table_obj.notify_status = 3
        table_objs.append(table_obj)
    save_ng_recv_msg(pch_session, table_objs)
    print 'move success.....................'



