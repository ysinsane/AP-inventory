#_*_coding:utf-8_*_

from flask import Flask, render_template
from flask_mail import Mail
from flask_moment import Moment
from flask_nav.elements import Navbar, View
from flask_sqlalchemy import SQLAlchemy
from flask_nav import Nav

from config import config
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
nav = Nav()

topbar = Navbar('',
    View('Home', 'main.index'),
)   

nav.register_element('top', topbar)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])#这才真的把config类里的配置写入app
    config[config_name].init_app(app)#没啥用，对齐格式的东西...
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    nav.init_app(app)
# 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
