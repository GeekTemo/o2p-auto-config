# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bo import *
import constant

# 拼接sqlalchemy连接url
def join_sqlalchemy_url(host, user, passwd, db, port=3306):
    urlTemp = string.Template('mysql://${user}:${passwd}@${host}/${db}')
    kws = {'user': user, 'passwd': passwd, 'host': host + ':' + str(port), 'db': db}
    return urlTemp.substitute(kws)


# 创建数据库连接会话
def create_session(db_env):
    url = join_sqlalchemy_url(db_env['host'], db_env['user'], db_env['passwd'], db_env['db'], db_env['port'])
    engine = create_engine(url, echo=True, encoding='utf-8')
    Session = sessionmaker(bind=engine)
    return Session()


# 根据id查询指定的表
def get_table_by_id(session, talename, id, value):
    sql = 'select %s from %s where %s=%d' % (id, talename, id, int(value))
    query_id = session.query(id).from_statement(sql).first()
    return query_id


# 产生唯一主键
# 规则 OP2表id规则:组织代码(前缀)+(0000~1000)的数字
# start起始点
def generate_id(tablename, primary_key, start, db_env):
    session = get_session(db_env)
    for i in range(int(start), int(start) + constant.MAX_ID_SUFFIX_NUMBER):
        query_id = get_table_by_id(session, tablename, primary_key, i)
        if not query_id:
            return i
    return None


def add_if_not_exits(session, obj):
    pass


# 获取 key:host:user:passwd:db:port  value:session值
sessions = {}
import thread

sessions_lock = thread.allocate_lock()


def get_session(db_env):
    sessions_lock.acquire()
    session = None
    key = db_env['host'] + ':' + db_env['user'] + ':' + db_env['passwd'] + ':' + db_env['db'] + ':' + str(
        db_env['port'])
    if key in sessions:
        session = sessions[key]
    else:
        session = create_session(db_env)
        sessions[key] = session
    sessions_lock.release()
    return session













