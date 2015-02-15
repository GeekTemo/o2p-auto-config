# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'
import tornado.ioloop
import tornado.web

from pycket.session import SessionMixin

from core import *
from bo import *
from db_utils import *
import constant
import configurers

import sys


class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def get_current_user(self):
        return self.session.get("user_name")


# 登录处理
class LoginHandler(BaseHandler):
    def post(self, *args, **kwargs):
        flow = ConfigFlow()
        flow.db_env['host'] = self.get_argument('host')
        flow.db_env['user'] = self.get_argument('user')
        flow.db_env['passwd'] = self.get_argument('passwd')
        flow.db_env['db'] = self.get_argument('db')
        flow.db_env['port'] = self.get_argument('port')
        sqlsession = get_session(flow.db_env)
        try:
            sqlsession.query(Org).first()
        except Exception, e:
            self.redirect('/login.html')
        self.session['user_name'] = flow.db_env['user']
        self.session['state'] = constant.LOGINED
        self.session['flow'] = flow
        self.render('base.html')


# 主页面
class MainHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.redirect('/login.html')


# 下一步
class NextHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        flow = self.session['flow']
        flow.org.org_code = self.get_argument('orgcode').strip()
        flow.org.name = self.get_argument('orgname').strip()
        # 调用O2P协议方案
        flow.protocol = self.get_argument('protocol').strip()
        # 调用O2P路径
        flow.path = self.get_argument('path').strip()
        # 调用方法
        flow.action_method = self.get_argument('action_method')
        # 调用方案,透传or协转
        flow.configplan = self.get_argument('configplan')
        self.session['flow'] = flow
        if flow.configplan == 'tranis':
            self.render('transm.html')
        elif flow.configplan == 'convert':
            self.render('convert.html')


# 透传方案配置
class TransConfigHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        flow = self.session['flow']
        # 方法名
        flow.operation = self.get_argument('operation')
        # 目标调用地址
        flow.target_url = self.get_argument('targeturl')
        # 目标调用协议此时和调用O2P的协议是一样的
        flow.target_protocol = flow.protocol
        # 目标调用方法也是和调用O2P的方法是一样的
        flow.target_method = flow.operation
        flow.req_doc = self.get_argument('reqdoc')
        # 配置类
        configuer = configurers.configuers[flow.protocol]
        cf = configuer(flow)
        (flow, result) = cf.config()
        self.session['flow'] = flow
        if result == constant.SUCCESS or result == constant.FAIL:
            self.render('info.html', info=flow.info)
        # 如果已经配置,则重新开始配置
        elif result == constant.HAVED_CONFIGED:
            self.render('base.html', message='该业务已经配置过')


# 协转方案配置
class ConvertConfigHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        flow = self.session['flow']
        # 方法名
        flow.operation = self.get_argument('operation')
        # 目标调用地址
        flow.target_url = self.get_argument('target_url')
        # 目标调用协议
        flow.target_protocol = self.get_argument('target_protocol')
        # 目标调用方法
        flow.target_method = self.get_argument('target_method')
        # 发起方入参,双引号都变为单引号
        flow.input_doc = self.get_argument('input').replace('"', "'")
        # 落地方入参
        flow.target_input_doc = self.get_argument('target_input').replace('"', "'")
        # 输入参数映射
        flow.input_map_rule_text = self.get_argument('input_map')
        # 发起方出参
        flow.output_doc = self.get_argument('output').replace('"', "'")
        # 落地方出参
        flow.target_output_doc = self.get_argument('target_output').replace('"', "'")
        # 输出参数映射
        flow.output_map_rule_text = self.get_argument('output_map')
        # 配置类
        configuer = configurers.configuers[flow.protocol]
        cf = configuer(flow)
        (flow, result) = cf.config()
        self.session['flow'] = flow
        self.render('info.html', info=flow.info)


