# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'
import string
import MySQLdb as mysql

import sys

reload(sys)
sys.setdefaultencoding('utf8')

conn = mysql.connect(host='10.30.1.7', user='mig', passwd='mig', db='dev_op2_conf', port=3306, use_unicode=True,
                     charset='utf8')


def fecth_select_sqls(sql_text):
    sqls = []
    lines = sql_text.split('\n')
    sqls = [line.strip() for line in lines if line.strip().lower().startswith('select')]
    return sqls


def join_insert_sql(tablename, fields, values):
    sql = '''insert into ${table}($fields) values(${values})'''
    template = string.Template(sql)
    fields = ','.join(fields)
    temp=[]
    for value in values:
        if "'" in str(value):
            value = value.replace("'", "''")
        temp.append("'%s'" % value)
    values = ','.join(temp)
    return template.substitute(table=tablename, fields=fields, values=values)


import re

import sqlparse


def get_table_name(sql):
    format_sql = sqlparse.format(sql, reindent=True).lower()
    tablename = format_sql.split('\n')[1].replace('from', '').strip()
    return tablename


def execute_sql(cur, sql):
    '''
    :param cur:
    :param sql:
    :return:
    tablename:The select table name
    fields:The select fields.
    values:The select values
    for example.tablename:'user'
    fileds:['id', 'name', 'sex']
    values(('1', 'jim', 'm'), ('2', 'herry', 'f'), ('3', 'jeffy', 'm'))
    '''

    tablename = get_table_name(sql)
    cur.execute(sql)
    fields = [field[0] for field in cur.description]
    rows = cur.fetchall()
    return tablename, fields, rows


def selects_2_inserts(conn, sql_file):
    insert_sqls = []
    f = open(sql_file, 'r')
    sql_text = f.read()
    sqls = fecth_select_sqls(sql_text)
    cur = conn.cursor()
    for sql in sqls:
        r = execute_sql(cur, sql)
        for row in r[2]:
            insert_sql = join_insert_sql(r[0], r[1], row)
            insert_sqls.append(insert_sql + ';')
        insert_sqls.append('\n')
    f.close()
    return insert_sqls


def write_sql_file(file, sqls):
    f = open(file, 'w')
    for sql in sqls:
        f.write(sql + '\n')
    f.close()


if __name__ == '__main__':
    file = '/Users/gongxingfa/wimp_query2.sql'
    f2 = '/Users/gongxingfa/demo3.sql'
    sqls = selects_2_inserts(conn, file)
    write_sql_file(f2, sqls)

