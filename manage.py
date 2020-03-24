# _*_coding:utf-8_*_

import os, logging

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Item, Role, Record


if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


app = create_app('production')
manager = Manager(app)
migrate = Migrate(app, db)  # migrate感觉可以放在工厂函数里去


def make_shell_context():
    return dict(db=db, User=User, Item=Item, Role=Role, Record=Record)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def deploy():
    """Run deployment tasks."""
    db.drop_all()
    db.create_all()
    # 创建用户角色
    if len(Role.query.all())<2:
        Role.insert_roles()
    # 创建管理员帐号
    if not User.query.filter_by(username=os.environ['ADMIN_NAME']).first():
        u=User(username=os.environ['ADMIN_NAME'],
        password=os.environ['ADMIN_PASS'],
        email=os.environ['AP_ADMIN'],
        role=Role.query.filter_by(name='Asist').first())
        db.session.add(u)
        db.session.commit()


if __name__ == "__main__":
    manager.run()

else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
