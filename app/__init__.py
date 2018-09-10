#_*_coding:utf-8_*_

from flask import Flask, render_template
from flask_mail import Mail
from flask_moment import Moment
from flask_nav.elements import Navbar, View
from flask_sqlalchemy import SQLAlchemy
from flask_nav import Nav
from flask_login import LoginManager

from config import config
from flask_bootstrap import Bootstrap

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
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
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    nav.init_app(app)
    login_manager.init_app(app)
# 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    from .manage import manage as manage_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(manage_blueprint,url_prefix='/manage')
    return app
