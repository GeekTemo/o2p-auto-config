# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

import tornado.ioloop
import tornado.web
import os

from handlers import *


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login.html",
    "xsrf_cookies": False,
    'pycket': {
        'engine': 'redis',
        'storage': {
            'host': 'localhost',
            'port': 6379,
            'db_sessions': 10,
            'db_notifications': 11,
            'max_connections': 2 ** 31,
        },
        'cookies': {
            'expires_days': 120,
        },
    }
}

handlers = [(r'/', MainHandler),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
             dict(path=settings['static_path'])),
            (r"/(login\.html)", tornado.web.StaticFileHandler,
             dict(path=settings['static_path'])),
            (r'/login', LoginHandler), (r'/next', NextHandler),
            (r'/transm', TransConfigHandler),
            (r'/convert', ConvertConfigHandler)]

app = tornado.web.Application(handlers=handlers,
                              template_path=os.path.join(os.path.dirname(__file__), "templates"),
                              **settings)

if __name__ == '__main__':
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()